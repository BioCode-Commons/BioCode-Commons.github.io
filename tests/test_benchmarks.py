import copy
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import benchmarks as b
import sync_benchmarks as sync

class PublishedBenchmarks(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'benchmarks/NuExpansionHunter.json').read_text())

    def test_nonbenchmark_content_matches_original_site(self):
        import hashlib
        template = b.render((ROOT / 'template.html').read_text(), ROOT / 'benchmarks')
        original_template = (ROOT / 'tests/nonbenchmark-template.sha256').read_text().strip()
        template = re.sub(r'<div class="benchmark-table-wrap".*?</div>', '', template, flags=re.S)
        template = re.sub(r'<p class="benchmark-note">.*?</p>', '', template, flags=re.S)
        template = re.sub(r'(<th scope="row"><a href="#project-[^"]+">.*?</th>\s*<td>.*?</td>\s*<td>).*?(</td>)', r'\1\2', template, flags=re.S)
        template = '\n'.join(line for line in template.splitlines() if line.strip())
        self.assertEqual(hashlib.sha256(template.encode()).hexdigest(), original_template)

    def test_all_published_records(self):
        for p in b.PROJECTS:
            b.validate(json.loads((ROOT / 'benchmarks' / (p + '.json')).read_text()), p)

    def test_first_publication(self):
        p = 'NuVCFtools'
        pending = {'schema_version': 1, 'project': p, 'status': 'unpublished'}
        self.assertEqual(b.validate(pending, p), pending)
        self.assertNotIn('<table>', b.render_table(pending))
        self.assertNotIn('×', b.render_summary(pending))
        for change in ({'rows': []}, {'status': 'typo'}, {'project': 'NuTRF'}):
            with self.assertRaises(ValueError):
                b.validate({**pending, **change}, p)
        measured = {**self.data, 'project': p,
                    'evidence_url': self.data['evidence_url'].replace(self.data['project'], p)}
        self.assertIn('<table>', b.render_table(b.validate(measured, p)))
        self.assertIn('×', b.render_summary(measured))
        with self.assertRaises(ValueError):
            b.validate({**measured, 'rows': []}, p)

    def test_memory_measure_uses_source_label(self):
        for metric in ('Peak RAM', 'Peak RSS'):
            d = {**self.data, 'memory_metric': metric}
            self.assertIn(metric, b.render_header(b.validate(d, d['project'])))
            self.assertIn(metric, b.render_summary(d))
        d.pop('memory_metric')
        self.assertIn('Peak RSS', b.render_header(d))
        with self.assertRaises(ValueError):
            b.validate({**d, 'memory_metric': 'unknown'}, d['project'])

    def test_invalid_numbers(self):
        for value in (0, -1, True, '1', float('nan'), float('inf')):
            d = copy.deepcopy(self.data)
            d['rows'][0]['candidate_seconds'] = value
            with self.assertRaises(ValueError): b.validate(d, d['project'])

    def test_invalid_metadata(self):
        for key, value in [('rss_unit', 'GB'), ('evidence_url', 'https://github.com/x/y/blob/main/BENCHMARKS.md'), ('project', 'Unknown')]:
            d = copy.deepcopy(self.data); d[key] = value
            with self.assertRaises(ValueError): b.validate(d, 'NuExpansionHunter')

    def test_duplicate_rows(self):
        self.data['rows'].append(copy.deepcopy(self.data['rows'][0]))
        with self.assertRaises(ValueError): b.validate(self.data, self.data['project'])

    def test_text_is_escaped(self):
        self.data['rows'][0]['dataset'] = '<script>alert(1)</script>'
        self.assertNotIn('<script>', b.render_rows(self.data))
        with self.assertRaises(ValueError): b.segments([{'text': 'x', 'url': 'javascript:alert(1)'}])

    def test_speedup_is_calculated(self):
        self.data['rows'][0]['baseline_seconds'] = 100
        self.data['rows'][0]['candidate_seconds'] = 25
        self.assertIn('<td>4.000×</td>', b.render_rows(self.data))

    def test_only_placeholders_change(self):
        template = (ROOT / 'template.html').read_text()
        rendered = b.render(template, ROOT / 'benchmarks')
        pieces = re.split(r'\{\{BENCHMARK_[A-Z]+:[^}]+\}\}', template)
        cursor = 0
        for piece in pieces:
            pos = rendered.find(piece, cursor)
            self.assertGreaterEqual(pos, cursor)
            cursor = pos + len(piece)
        self.assertNotIn('{{BENCHMARK_', rendered)
        self.assertEqual(rendered, b.render(template, ROOT / 'benchmarks'))

    def test_failed_fetch_does_not_write(self):
        before = {p: p.read_bytes() for p in (ROOT / 'benchmarks').glob('*.json')}
        with patch.object(sync, 'fetch', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError): sync.main()
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_snapshot_uses_commit_not_moving_main(self):
        calls = []
        def fake(url):
            calls.append(url)
            if '/git/ref/' in url: return {'object': {'sha': 'a' * 40}}
            project = url.split('/')[4]
            return json.loads((ROOT / 'benchmarks' / (project + '.json')).read_text())
        with patch.object(sync, 'fetch', side_effect=fake):
            snapshot, refs = sync.collect()
        self.assertEqual(set(snapshot), set(b.PROJECTS))
        self.assertTrue(all('/' + 'a' * 40 + '/' in u for u in calls if 'raw.githubusercontent' in u))

if __name__ == '__main__': unittest.main()
