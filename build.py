#!/usr/bin/env python3
"""Build a dependency-free website from the supplied source document."""
from pathlib import Path
import html
import hashlib
import json
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

root = Path(__file__).resolve().parent
source = (root / 'content/source.txt').read_text(encoding='utf-8-sig')
mission, rest = source.split('Our Vision', 1)
community, approach = rest.split('Our Approach', 1)
navigation = json.loads((root / 'content/navigation.json').read_text())


def paragraphs(text):
    return '\n'.join(f'<p>{html.escape(paragraph.strip())}</p>'
                     for paragraph in re.split(r'\n\s*\n', text.strip()) if paragraph.strip())


def contents(items):
    return '\n'.join(f'<a class="toc-heading" href="{html.escape(item["href"], quote=True)}">'
                     f'{html.escape(item["label"])}</a>' for item in items)


template = (root / 'template.html').read_text()
rendered = template.replace('{{MISSION}}', html.escape(mission.strip()))
rendered = rendered.replace('{{COMMUNITY}}', paragraphs(community))
rendered = rendered.replace('{{APPROACH}}', paragraphs(approach))
rendered = rendered.replace('{{CONTENTS}}', contents(navigation))


def version_asset(match):
    parts = urlsplit(match.group(2))
    path = root / parts.path
    if parts.scheme or parts.netloc or not path.is_file():
        return match.group(0)
    version = hashlib.blake2s(path.read_bytes(), digest_size=6).hexdigest()
    query = [(key, value) for key, value in parse_qsl(parts.query) if key != 'v']
    query.append(('v', version))
    url = urlunsplit(('', '', parts.path, urlencode(query), parts.fragment))
    return f'{match.group(1)}="{html.escape(url, quote=True)}"'


rendered = re.sub(r'(href|src)="([^"]+)"', version_asset, rendered)
(root / 'index.html').write_text(rendered)
print('Built index.html: mission, vision, approach, projects, and Discord contact.')
