"""Render the film (or a stretch of it) with Manim at 960 x 320 and mux your own copy of the song in.

    python tools/render.py                          the whole film, 30 fps -> ../out/manim_960x320.mp4
    python tools/render.py --fps 60
    python tools/render.py --from 59.4 --to 74.2    one stretch (song seconds; the film starts at -5, the warning page)
    python tools/render.py --shot c1-kw2            one shot
    python tools/render.py --size 1920x640          the same 3:1 film at twice the size

The song is never in the repository (see 音頻&歌詞/README.md): when config.json -> paths.audio exists it is cut to the
rendered stretch and muxed in; otherwise the video is silent.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MANIM_DIR = os.path.dirname(HERE)
ROOT = os.path.dirname(MANIM_DIR)
sys.path.insert(0, MANIM_DIR)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='t0', type=float)
    ap.add_argument('--to', dest='t1', type=float)
    ap.add_argument('--shot')
    ap.add_argument('--fps', type=float, default=30)
    ap.add_argument('--size', default='960x320')
    ap.add_argument('--out')
    args = ap.parse_args()
    w, h = (int(v) for v in args.size.lower().split('x'))

    from wem.data import Env, path as repo_path
    env = Env()
    t0, t1 = -env.preroll, env.duration
    if args.shot:
        s = env.shot(args.shot)
        if not s:
            sys.exit(f'no shot "{args.shot}" in STORYBOARD.md')
        t0, t1 = s['at'], s['until']
    t0 = args.t0 if args.t0 is not None else t0
    t1 = args.t1 if args.t1 is not None else t1
    out = args.out or os.path.join(ROOT, 'out', f'manim_{w}x{h}' + (f'_{args.shot}' if args.shot else '') +
                                   (f'_{t0:g}-{t1:g}' if (args.t0 is not None or args.t1 is not None) else '') + '.mp4')
    os.makedirs(os.path.dirname(out), exist_ok=True)

    media = os.path.join(MANIM_DIR, 'media')
    envv = dict(os.environ, WEM_FROM=str(t0), WEM_TO=str(t1), WEM_W=str(w), WEM_H=str(h), WEM_FPS=str(args.fps), WEM_AUDIO='0')
    manim = shutil.which('manim') or os.path.join(os.path.dirname(sys.executable), 'manim')
    cmd = [manim, '--disable_caching', '--frame_rate', str(args.fps), '-r', f'{w},{h}', '--media_dir', media,
           '-o', 'wem_render', 'film.py', 'WorldExecuteMe']
    print(f'[render] song {t0:.2f} .. {t1:.2f} s, {w}x{h} @ {args.fps:g} fps')
    start = time.time()
    subprocess.run(cmd, cwd=MANIM_DIR, env=envv, check=True)
    found = sorted(glob.glob(os.path.join(media, 'videos', 'film', '**', 'wem_render.mp4'), recursive=True), key=os.path.getmtime)
    if not found:
        sys.exit('manim produced no video')
    video = found[-1]
    audio = repo_path(env.cfg['paths']['audio'])
    ff = shutil.which('ffmpeg')
    if os.path.exists(audio) and ff:
        # the video starts at song time t0 (negative = the silent warning page before the song)
        a_in = ['-ss', f'{max(0.0, t0):.3f}', '-i', audio]
        delay = max(0.0, -t0)
        af = ['-af', f'adelay={int(delay * 1000)}:all=1'] if delay > 0 else []
        subprocess.run([ff, '-y', '-v', 'error', '-i', video, *a_in, '-map', '0:v', '-map', '1:a', *af, '-c:v', 'copy',
                        '-c:a', 'aac', '-b:a', '256k', '-shortest', out], check=True)
        print(f'[render] muxed the song from {audio}')
    else:
        shutil.copyfile(video, out)
        print('[render] no audio file (see 音頻&歌詞/README.md): the video is silent')
    print(f'[render] {out}  ({time.time() - start:.0f} s)')


if __name__ == '__main__':
    main()
