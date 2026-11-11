"""Register the film's three type families with Pango before any text is set.

JetBrains Mono (system / code), Source Serif 4 (what the AI says) and Inter (interface and the user), all SIL OFL 1.1.
`python tools/fetch_fonts.py` downloads them into manim/fonts/ (git ignores that folder); fonts installed on the
system are used as they are.
"""
import glob
import os

FONT_DIR = os.path.join(os.path.dirname(__file__), '..', 'fonts')
_done = False


def register():
    global _done
    if _done:
        return
    _done = True
    import manimpango
    for p in sorted(glob.glob(os.path.join(FONT_DIR, '**', '*.[ot]tf'), recursive=True)):
        manimpango.register_font(os.path.abspath(p))
    have = set(manimpango.list_fonts())
    missing = [f for f in ('JetBrains Mono', 'Source Serif 4', 'Inter') if f not in have]
    if missing:
        print(f"[wem] fonts not found: {', '.join(missing)} (run `python tools/fetch_fonts.py`); Pango will substitute.")
