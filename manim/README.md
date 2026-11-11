# world.execute(me); — Manim port for a 960 × 320 display

A port of the lyric MV to [Manim Community](https://www.manim.community/), reframed for a **960 × 320 (3:1) landscape
display**. It renders the same film as the browser project at the root of this repository: the same shots at the same
cut times, the same lyric timing, conversation, colour states and transitions. Every shot is redrawn for the wide, low
frame.

## What it reads (nothing is copied by hand)

| From the main project | Used for |
| --- | --- |
| `config.json` | palettes (colour states), timing offsets, typing speed, pre-roll / flash range, spot colours |
| `data/audio_features.json` | beat grid, onsets, levels (beat pulses, kicks) |
| `data/lyrics.json` | the lyric lines with your own text (made by `node tools/fill_lyrics.mjs`, see the main README) |
| `data/lyric_timing.json` | used instead when `lyrics.json` is missing: lines are then drawn as dots |
| `docs/v4/chat_script.json`, `docs/v4/errors.json` | the written conversation, the error dialogs |
| `src/scenes/cues.js` | the word and drum cues that are not on the beat grid |
| `STORYBOARD.md` | the shot list: id, cut time, lyric lines, colour state, transition |
| `assets/character/*.png` | the silhouettes, separated into their three inks |

If a cue or a cut is corrected in the JS project (and `npm run storyboard` is run), the Manim port follows.

## Setup

Python 3.10+ and the system libraries Manim needs (Cairo, Pango, ffmpeg; see the
[Manim install guide](https://docs.manim.community/en/stable/installation.html)).

```bash
cd manim
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python tools/fetch_fonts.py                       # JetBrains Mono, Source Serif 4, Inter -> manim/fonts/ (OFL)
```

The lyric text is not in the repository. Put your own song and lyric file into `音頻&歌詞/` and run, at the repository
root, `node tools/fill_lyrics.mjs` once: it writes `data/lyrics.json`, which this port reads.

## Render

```bash
cd manim
python tools/render.py                            # whole film, 960x320 @ 30 fps, song muxed in -> out/manim_960x320.mp4
python tools/render.py --fps 60
python tools/render.py --from 59.4 --to 74.2      # a stretch, in song seconds (the film starts at -5: the warning page)
python tools/render.py --shot c1-kw2              # one shot (ids: STORYBOARD.md)
python tools/still.py --times=15.2,61.98          # still frames / contact sheet, no video (fast checks)
python tools/still.py --shots                     # one frame from the middle of every shot
```

Or call Manim directly; `manim.cfg` sets 960 × 320 at 30 fps:

```bash
manim film.py WorldExecuteMe                                   # whole film (adds the song itself if it exists)
WEM_FROM=148 WEM_TO=162 manim film.py WorldExecuteMe           # a stretch
WEM_SHOT=cx-fall manim film.py WorldExecuteMe                  # one shot
WEM_W=1920 WEM_H=640 manim film.py WorldExecuteMe              # the same 3:1 film at another size
```

`WorldExecuteMe` is an ordinary Manim `Scene`, so a display project that drives Manim scenes can import `film.py`
(or `wem.engine.Film`, whose `frame(t)` returns the mobjects of the frame at song time `t`).
A full render at 30 fps takes roughly 15–20 minutes on one core (about 0.1–0.2 s a frame).

## How it is built

```
manim/
  film.py                 the Manim Scene: one ValueTracker runs through the song, one updater rebuilds the frame
  manim.cfg               960 x 320, 30 fps
  wem/
    data.py               config, beat grid, lyrics, cues, shot list (STORYBOARD.md), palettes
    engine.py             shots -> frames: overlaps, transitions (cut, push, zoom, scan, fade, glitch), overlay, flash
    ctx.py                the canvas-style drawing API of src/engine/draw.js on top of pooled Manim mobjects
    components.py         spark, cursor, the chat client re-laid out for 3:1, controls, toasts
    plates.py             the print plates: paper, keyword type, shadow plates, the four chorus plates, the loop listing
    art.py                the silhouettes as three-ink prints recoloured by palette role
    geom.py               wireframes, outlines, type along paths
    sections/s01..s13     one file per section of the film, one drawing per shot
  tools/render.py         render + mux the song;  tools/still.py  still frames;  tools/fetch_fonts.py
```

Shots draw in a virtual frame of 1920 × 640 px (twice the display), so type sizes are comparable to the browser film's
1920 × 1080 frame. Every frame is a pure function of song time, as in the browser renderer.

### Reframing for 3:1

The browser film is 16:9. Here the frame is three times as wide as it is tall, so every shot was re-composed rather
than cropped: the chat window is a wide, low band (sidebar left, thread in the middle, settings drawer right); plates
keep their picture in the upper five sixths of the sheet and set the keyword across the foot; tall compositions
(the persona card, the pre-chorus controls, the count cards, the last shout) are laid out side by side instead of
stacked.

### What is different from the browser film

- **No WebGL post pass.** Manim's Cairo renderer has no pixel shaders, so bloom, grain, scanlines, chromatic
  aberration, datamosh and the mosaic pass are not ported. Glows are drawn as soft strokes, rays and flashes as shapes,
  tears as shifted bands, the Vision mosaic as drawn blocks, and a static vignette finishes the frame.
- **No clipping or masks.** Where the browser film shows a picture *through* letters (the last shout) or clips a
  scrolling thread, the port fades or layers instead.
- **Re-composed shots.** Sections 6-14 follow the JS drawing code shot by shot (same events on the same beats and
  cues); sections 1-5 and the execution / count cards are more compact re-compositions of each storyboard moment.
  Some fine detail (the ASCII world, the cut-paper history strip) is drawn more simply.
- Lyric text is dots until `data/lyrics.json` exists (the repository carries no lyrics).

The credits and licences of the main project apply unchanged (see `../CREDITS.md`, `../LICENSE`): the character
silhouettes are CC BY-NC-SA 4.0, and the song belongs to Mili.
