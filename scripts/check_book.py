#!/usr/bin/env python3
"""Validate Quarto artifacts, local links/anchors, citations and source labels.

Uses only the Python standard library, and works locally and in GitHub Actions.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
errors = []


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = set()
        self.links = []
        self.citations = set()
        self.feed(path.read_text())

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for attribute in ('href', 'src', 'poster'):
            if attrs.get(attribute):
                self.links.append(attrs[attribute])
        self.citations.update(attrs.get('data-cites', '').split())


chapters = sorted(ROOT.glob('*.qmd'))
bibs = sorted((ROOT / 'assets').glob('refs-*.bib'))
keys = []
for bib in bibs:
    keys += re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib.read_text())
for key in set(keys):
    if keys.count(key) > 1:
        errors.append(f'Duplicate bibliography key: {key}')
labels = set()
for chapter in chapters:
    labels.update(re.findall(r'\{#([\w-]+)', chapter.read_text()))
for chapter in chapters:
    for reference in re.findall(r'(?<![\w/])@([a-zA-Z][\w:.-]*)', chapter.read_text()):
        reference = reference.rstrip('.')
        if reference not in labels and reference not in keys:
            errors.append(f'{chapter.name}: unresolved source reference @{reference}')

pages = {p.resolve(): Page(p) for p in SITE.rglob('*.html')}
if not pages:
    errors.append('No HTML output found')
for chapter in chapters:
    if not (SITE / chapter.with_suffix('.html').name).is_file():
        errors.append(f'Missing chapter page: {chapter.name}')
for path, page in pages.items():
    for key in page.citations:
        if key not in keys:
            errors.append(f'{path.name}: unknown rendered citation {key}')
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc or link.startswith('//'):
            continue
        raw_path = unquote(url.path)
        if raw_path.startswith('/levy-walks-book/'):
            target = SITE / raw_path.removeprefix('/levy-walks-book/')
        elif raw_path.startswith('/'):
            target = SITE / raw_path.lstrip('/')
        elif raw_path:
            target = path.parent / raw_path
        else:
            target = path
        target = target.resolve()
        if target.is_dir():
            target /= 'index.html'
        if not target.is_file():
            errors.append(f'{path.name}: missing local target {link}')
        elif url.fragment and target.suffix == '.html':
            other = pages.get(target)
            if other and unquote(url.fragment) not in other.ids:
                errors.append(f'{path.name}: missing anchor {link}')
    text = path.read_text()
    if 'quarto-xref-unresolved' in text or 'citation-not-found' in text:
        errors.append(f'{path.name}: unresolved rendered reference marker')

pdf = SITE / 'levy-walks-book.pdf'
if not pdf.is_file() or pdf.read_bytes()[:5] != b'%PDF-':
    errors.append('Combined PDF is missing or invalid')
if not (SITE / '.nojekyll').is_file():
    errors.append('Missing .nojekyll in site')
index = SITE / 'index.html'
if index.is_file() and 'levy-walks-book.pdf' not in index.read_text():
    errors.append('Home page has no PDF download link')

if errors:
    print('\n'.join(sorted(set(errors))))
    sys.exit(1)
print(f'PASS: {len(chapters)} chapters; {len(keys)} bibliography entries; '
      f'{len(pages)} HTML pages; local links, anchors, references, PDF download.')
