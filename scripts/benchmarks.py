"""Validate published benchmark records and render only benchmark placeholders."""
import html
import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

PROJECTS = ('NuSTAR', 'NuExpansionHunter', 'NuTRF', 'NuMAFFT')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    require(isinstance(value, str) and bool(value.strip()), 'Expected nonempty text')
    return value


def url(value):
    p = urlsplit(text(value))
    require(p.scheme == 'https' and p.hostname == 'github.com' and not p.username,
            'Evidence links must be HTTPS GitHub URLs')
    return value


def segments(value):
    require(isinstance(value, list), 'Expected text/link segments')
    for item in value:
        require(isinstance(item, dict) and set(item) in ({'text'}, {'text', 'url'}), 'Invalid text segment')
        text(item['text'])
        if 'url' in item:
            url(item['url'])


def validate(d, project):
    fields = {'schema_version', 'project', 'evidence_url', 'rss_unit', 'rss_scope',
              'time_scope', 'rows', 'caption', 'note', 'display', 'summary_context'}
    require(isinstance(d, dict) and set(d) == fields, 'Unexpected or missing document fields')
    require(type(d['schema_version']) is int and d['schema_version'] == 1, 'Unsupported schema')
    require(project in PROJECTS and d['project'] == project, 'Project mismatch')
    evidence = url(d['evidence_url'])
    require(re.fullmatch(r'https://github.com/BioCode-Commons/' + re.escape(project)
                         + r'/blob/[0-9a-f]{40}/.+', evidence), 'Pin evidence to a full commit SHA')
    require(d['rss_unit'] in ('MiB', 'GiB'), 'RSS unit must be MiB or GiB')
    text(d['rss_scope']); text(d['time_scope'])
    require(isinstance(d['summary_context'], str), 'Invalid summary context')
    segments(d['caption']); segments(d['note'])
    require(bool(d['caption']), 'Caption required')
    display = d['display']
    require(isinstance(display, dict) and set(display) == {'time_decimals', 'rss_decimals', 'speedup_column'}, 'Invalid display fields')
    for key in ('time_decimals', 'rss_decimals'):
        require(type(display[key]) is int and 0 <= display[key] <= 6, 'Invalid precision')
    require(type(display['speedup_column']) is bool, 'Invalid speedup-column flag')
    require(isinstance(d['rows'], list) and 0 < len(d['rows']) <= 1000, 'Expected benchmark rows')
    seen = set()
    for row in d['rows']:
        require(isinstance(row, dict) and set(row) == {'dataset', 'resources', 'baseline_seconds', 'candidate_seconds', 'baseline_rss', 'candidate_rss'}, 'Invalid row fields')
        key = (text(row['dataset']), text(row['resources']))
        require(key not in seen, 'Duplicate dataset/resources row')
        seen.add(key)
        for name in ('baseline_seconds', 'candidate_seconds', 'baseline_rss', 'candidate_rss'):
            value = row[name]
            require(type(value) in (int, float) and math.isfinite(value) and value > 0,
                    name + ' must be finite and positive')
    return d


def render_segments(items):
    return ''.join('<a href="' + html.escape(i['url'], quote=True) + '">' + html.escape(i['text']) + '</a>'
                   if 'url' in i else html.escape(i['text']) for i in items)


def render_rows(d):
    result = []
    for row in d['rows']:
        cells = '<th scope="row">' + html.escape(row['dataset']) + '</th><td>' + html.escape(row['resources']) + '</td>'
        for key in ('baseline_seconds', 'candidate_seconds'):
            cells += '<td>' + format(row[key], f",.{d['display']['time_decimals']}f") + '</td>'
        if d['display']['speedup_column']:
            cells += f"<td>{row['baseline_seconds'] / row['candidate_seconds']:.3f}×</td>"
        for key in ('baseline_rss', 'candidate_rss'):
            cells += '<td>' + format(row[key], f",.{d['display']['rss_decimals']}f") + '</td>'
        result.append('              <tr>' + cells + '</tr>')
    return '\n'.join(result)


def render_header(d):
    original = html.escape(d['project'][2:])
    candidate = html.escape(d['project'])
    speedup = '<th scope="col" rowspan="2">Speedup</th>' if d['display']['speedup_column'] else ''
    return ('              <tr><th scope="col" rowspan="2">Dataset / Task</th><th scope="col" rowspan="2">Cores / Threads</th><th scope="colgroup" colspan="2">Wall time (s)</th>' + speedup + '<th scope="colgroup" colspan="2">Peak RSS (' + d['rss_unit'] + ')</th></tr>\n'
            + '              <tr><th scope="col">' + original + '</th><th scope="col">' + candidate + '</th><th scope="col">' + original + '</th><th scope="col">' + candidate + '</th></tr>')


def render_summary(d):
    ratios = [r['baseline_seconds'] / r['candidate_seconds'] for r in d['rows']]
    savings = [100 * (1 - r['candidate_rss'] / r['baseline_rss']) for r in d['rows']]
    def memory_change(value):
        return f"{abs(value):.1f}% {'less' if value >= 0 else 'more'}"
    context = ' (' + html.escape(d['summary_context']) + ')' if d['summary_context'] else ''
    return (f'<strong>Wall time:</strong> {min(ratios):.2f}–{max(ratios):.2f}× speedup' + context
            + '<br><strong>Peak RSS:</strong> ' + memory_change(min(savings)) + '–' + memory_change(max(savings)))



def render(template, directory):
    for project in PROJECTS:
        d = validate(json.loads((Path(directory) / (project + '.json')).read_text()), project)
        for key, value in [('ROWS', render_rows(d)), ('HEADER', render_header(d)), ('SUMMARY', render_summary(d)), ('CAPTION', render_segments(d['caption'])), ('NOTE', render_segments(d['note']))]:
            template = template.replace('{{BENCHMARK_' + key + ':' + project + '}}', value)
    require('{{BENCHMARK_' not in template, 'Unknown benchmark placeholder')
    return template


if __name__ == '__main__':
    import sys
    validate(json.loads(Path(sys.argv[1]).read_text()), sys.argv[2])
    print('Published benchmark data valid')
