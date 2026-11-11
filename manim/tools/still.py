"""Render single frames (song time) to PNG without running a Manim scene: quick checks and contact sheets.

    python tools/still.py --times 15.2,30,61.98 --out ../out/manim_sheet.png [--cols 3] [--scale 1]
    python tools/still.py --shots                    one frame from the middle of every shot
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from wem.setup import configure  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--times', default='')
    ap.add_argument('--shots', action='store_true', help='one frame from the middle of every shot')
    ap.add_argument('--only', default='', help='comma-separated shot ids (with --shots)')
    ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', '..', 'out', 'manim_sheet.png'))
    ap.add_argument('--cols', type=int, default=2)
    ap.add_argument('--label', action='store_true', default=True)
    args = ap.parse_args()
    configure()
    from manim import Camera, config
    from PIL import Image, ImageDraw
    from wem.engine import Film
    film = Film()
    if film.missing:
        print(f'[still] shots with no drawing yet (fallback): {len(film.missing)}')
    if args.shots:
        only = set(filter(None, args.only.split(',')))
        times = [((s.at + s.until) / 2, s.id) for s in film.shots if not only or s.id in only]
    else:
        times = [(float(x), '') for x in args.times.split(',') if x]
    tiles = []
    for t, sid in times:
        cam = Camera()
        t0 = time.time()
        cam.capture_mobjects(film.frame(t))
        im = cam.get_image().convert('RGB')
        if args.label:
            ImageDraw.Draw(im).text((6, 4), f'{t:.2f} {sid}', fill=(255, 80, 120))
        tiles.append(im)
        print(f'  {t:8.3f} {sid:16s} {time.time() - t0:.2f}s')
    W, H = config.pixel_width, config.pixel_height
    cols = min(args.cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * W + (cols - 1) * 4, rows * H + (rows - 1) * 4), (40, 40, 40))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * (W + 4), (i // cols) * (H + 4)))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    sheet.save(args.out)
    print('->', os.path.abspath(args.out))


if __name__ == '__main__':
    main()
