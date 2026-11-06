#!/usr/bin/env python3
"""Build a dependency-free website from the supplied source document."""
from pathlib import Path
import html
import re

root = Path(__file__).resolve().parent
source = (root / 'content/source.txt').read_text(encoding='utf-8-sig')
mission, rest = source.split('Community Engagement', 1)
community, approach = rest.split('Our Approach', 1)


def sections(text):
    entries = re.split(r'(?:^|\n)\s*\d+\.\s+', text.strip())
    return [entry.strip() for entry in entries if entry.strip()]


def rows(text, kind, prefix):
    output = []
    for number, entry in enumerate(sections(text), 1):
        title, body = re.split(r'\.\s+', entry, maxsplit=1)
        output.append(f'<article id="{prefix}-{number}" class="{kind}"><span class="number">{number}.</span>'
                      f'<h3>{html.escape(title)}.</h3><p>{html.escape(body)}</p></article>')
    return '\n'.join(output)


def contents(text, prefix, heading):
    items = []
    for number, entry in enumerate(sections(text), 1):
        title = re.split(r'\.\s+', entry, maxsplit=1)[0]
        items.append(f'<li><a href="#{prefix}-{number}">{number}. {html.escape(title)}</a></li>')
    return (f'<div class="toc-group"><a class="toc-heading" href="#{prefix}">{heading}</a>'
            f'<ol>{"".join(items)}</ol></div>')


template = (root / 'template.html').read_text()
rendered = template.replace('{{MISSION}}', html.escape(mission.strip()))
rendered = rendered.replace('{{COMMUNITY}}', rows(community, 'community-row', 'community'))
rendered = rendered.replace('{{APPROACH}}', rows(approach, 'approach-card', 'approach'))
rendered = rendered.replace('{{CONTENTS}}', contents(community, 'community', 'Community Engagement')
                            + contents(approach, 'approach', 'Our Approach'))
(root / 'index.html').write_text(rendered)
print('Built index.html: original mission, 3 community sections, 4 approach sections.')
