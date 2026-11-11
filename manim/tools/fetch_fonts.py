"""Download the film's three type families into manim/fonts/ (SIL OFL 1.1; git ignores that folder).

    python tools/fetch_fonts.py

JetBrains Mono (system / code), Source Serif 4 (what the AI says), Inter (interface and the user). Families already
installed on the system are skipped. The CJK lines of the warning page and the count cards use whatever CJK font
Pango finds (Noto Sans CJK is a good one to install).
"""
import io
import os
import sys
import urllib.request
import zipfile

DEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
SOURCES = {
    'Source Serif 4': ('https://github.com/adobe-fonts/source-serif/releases/download/4.005R/source-serif-4.005_Desktop.zip',
                       lambda n: '/TTF/SourceSerif4-' in n and n.endswith('.ttf') and 'Caption' not in n),
    'JetBrains Mono': ('https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip',
                       lambda n: n.startswith('fonts/ttf/') and n.endswith('.ttf')),
    'Inter': ('https://github.com/rsms/inter/releases/download/v4.0/Inter-4.0.zip',
              lambda n: n.startswith('extras/ttf/Inter-') and n.endswith('.ttf')),
}


def main():
    try:
        import manimpango
        have = set(manimpango.list_fonts())
    except Exception:
        have = set()
    os.makedirs(DEST, exist_ok=True)
    for family, (url, want) in SOURCES.items():
        if family in have and '--force' not in sys.argv:
            print(f'{family}: installed on the system, skipped')
            continue
        print(f'{family}: {url}')
        data = urllib.request.urlopen(url, timeout=120).read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = [n for n in z.namelist() if want(n)]
            for n in names:
                with open(os.path.join(DEST, os.path.basename(n)), 'wb') as fh:
                    fh.write(z.read(n))
        print(f'  {len(names)} files -> {DEST}')


if __name__ == '__main__':
    main()
