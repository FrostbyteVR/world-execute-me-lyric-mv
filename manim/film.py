"""world.execute(me); lyric MV — the Manim scene, for a 960 x 320 (3:1 landscape) display.

    manim -qh film.py WorldExecuteMe                       the whole film (see manim.cfg: 960 x 320, 30 fps)
    WEM_FROM=59.4 WEM_TO=74.2 manim film.py WorldExecuteMe one stretch (song seconds; the film starts at -5)
    WEM_SHOT=c1-kw2 manim film.py WorldExecuteMe           one shot
    python tools/render.py ...                             the same, plus the song muxed in (see the README)

Every frame is a pure function of song time (as in the browser film): a ValueTracker runs through the song and one
updater rebuilds the frame from it, so any stretch renders identically on its own.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manim import Group, Scene, ValueTracker, config, linear  # noqa: E402

from wem.setup import configure  # noqa: E402

# the display is 960 x 320 whatever quality flag manim was given (-ql / -qh only change the frame rate here);
# WEM_W / WEM_H render the same 3:1 film at another size (e.g. 1920 x 640)
configure(int(os.environ.get('WEM_W', 960)), int(os.environ.get('WEM_H', 320)), fps=float(os.environ['WEM_FPS']) if os.environ.get('WEM_FPS') else None)


class WorldExecuteMe(Scene):
    def construct(self):
        from wem.engine import Film
        film = Film()
        t0, t1 = film.start_time, film.end_time
        shot = os.environ.get('WEM_SHOT')
        if shot:
            s = next((s for s in film.shots if s.id == shot), None)
            if s is None:
                raise SystemExit(f'no shot "{shot}" (see STORYBOARD.md)')
            t0, t1 = s.at, s.until
        t0 = float(os.environ.get('WEM_FROM', t0))
        t1 = float(os.environ.get('WEM_TO', t1))
        from wem.data import path as repo_path
        audio = repo_path(film.env.cfg['paths']['audio'])
        if os.environ.get('WEM_AUDIO', '1') != '0' and os.path.exists(audio) and t0 <= 0:
            self.add_sound(audio, time_offset=-t0)
        clock = ValueTracker(t0)
        frame = Group()
        # a time-based updater (it takes dt), so Manim treats the frame as moving and never bakes it into a static background
        # It starts EMPTY: Manim lists the family of every moving mobject once, when play() begins, and draws that list
        # each frame; pooled mobjects listed there would be drawn again wherever a later frame left them.
        frame.add_updater(lambda m, dt: setattr(m, 'submobjects', film.frame(clock.get_value())))
        self.add(frame)
        self.play(clock.animate.set_value(t1), run_time=t1 - t0, rate_func=linear)
