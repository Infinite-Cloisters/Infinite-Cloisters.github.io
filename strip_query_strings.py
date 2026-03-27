"""
strip_query_strings.py

Post-process Sphinx-generated HTML files to remove ?v=<hash> cache-busting
query strings from static asset URLs.  GitHub Pages serves static files
directly and does not strip query strings before looking up the file on disk,
so ?v=... causes 404 errors for .css/.js resources.

Usage:
    python strip_query_strings.py [html_dir]

    html_dir defaults to ./docs
"""

import re
import sys
from pathlib import Path

# Matches  ?v=  followed by one or more hex digits (Sphinx cache-buster format)
QUERY_RE = re.compile(r'\?v=[0-9a-f]+')


def strip_file(path: Path) -> bool:
    """Return True if the file was modified."""
    original = path.read_text(encoding='utf-8')
    cleaned = QUERY_RE.sub('', original)
    if cleaned != original:
        path.write_text(cleaned, encoding='utf-8')
        return True
    return False


def main():
    html_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('docs')
    if not html_dir.is_dir():
        print(f'Error: directory "{html_dir}" not found.', file=sys.stderr)
        sys.exit(1)

    html_files = list(html_dir.rglob('*.html'))
    modified = 0
    for f in html_files:
        if strip_file(f):
            modified += 1
            print(f'  stripped: {f}')

    print(f'\nDone. {modified}/{len(html_files)} HTML file(s) modified.')


if __name__ == '__main__':
    main()
