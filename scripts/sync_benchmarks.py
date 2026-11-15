"""Fetch a complete, validated snapshot before replacing any cached records."""
import json
import os
import tempfile
import urllib.request
from pathlib import Path
from benchmarks import PROJECTS, validate

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'BioCode-Commons-benchmarks', 'Accept': 'application/vnd.github+json'})
    if url.startswith('https://api.github.com/') and os.environ.get('GH_TOKEN'):
        request.add_header('Authorization', 'Bearer ' + os.environ['GH_TOKEN'])
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def collect():
    snapshot, refs = {}, {}
    for project in PROJECTS:
        ref = fetch(f'https://api.github.com/repos/BioCode-Commons/{project}/git/ref/heads/main')['object']['sha']
        data = fetch(f'https://raw.githubusercontent.com/BioCode-Commons/{project}/{ref}/benchmarks/published.json')
        snapshot[project] = validate(data, project)
        refs[project] = ref
    return snapshot, refs


def main():
    snapshot, refs = collect()  # Failure leaves the previous snapshot untouched.
    destination = ROOT / 'benchmarks'
    destination.mkdir(exist_ok=True)
    for project, data in snapshot.items():
        with tempfile.NamedTemporaryFile(mode='w', dir=destination, delete=False) as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
        os.replace(f.name, destination / (project + '.json'))
    (destination / 'sources.json').write_text(json.dumps(refs, indent=2) + '\n')


if __name__ == '__main__':
    main()
