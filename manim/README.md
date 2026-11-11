# world.execute(me); — Manim version for a 960 × 320 display

A port of the lyric MV to [Manim Community](https://www.manim.community/), reframed for a **960 × 320 (3:1)
landscape display**. It renders the same film as the browser project at the root of this repository: the same shots
at the same cut times, the same lyric timing, conversation, colour states and transitions, every shot redrawn for the
wide, low frame.

This page is the complete guide: [what you need](#1-what-you-need), [setting up](#2-set-up), [adding your song and
lyrics](#3-add-your-song-and-lyrics), [rendering](#4-render), [checking frames without rendering](#5-check-frames-without-rendering),
[using it from your own display project](#6-use-it-from-your-own-project), [how it is built](#7-how-it-is-built) and
[troubleshooting](#8-troubleshooting).

---

## 1. What you need

| | Why |
| --- | --- |
| **Python 3.10 or newer** | the port and Manim are Python |
| **Manim's system libraries**: Cairo, Pango, ffmpeg | Manim draws with Cairo/Pango and encodes with ffmpeg. The [Manim install guide](https://docs.manim.community/en/stable/installation.html) has the exact packages for each OS (below: the short version) |
| **Node.js 20 or newer** | only for one step: `node tools/fill_lyrics.mjs`, which joins *your* lyric text with the film's timing table |
| **Your own copy of the song** and **its lyrics** | neither is in the repository; they belong to Mili (see [§3](#3-add-your-song-and-lyrics)) |

No LaTeX is needed (the film sets no TeX), and no GPU: Manim's Cairo renderer runs on the CPU.

System libraries, the short version:

```bash
# Debian / Ubuntu
sudo apt install build-essential python3-dev libcairo2-dev libpango1.0-dev pkg-config ffmpeg
# macOS (Homebrew)
brew install cairo pango pkg-config ffmpeg
# Windows: install ffmpeg (e.g. `winget install ffmpeg` or `choco install ffmpeg`); the Python wheels of Manim bring
#          Cairo and Pango with them
```

## 2. Set up

From the root of the repository (clone it, or unpack "Source code (zip)" from the Releases page):

```bash
cd manim
python -m venv .venv
. .venv/bin/activate                 # Windows (cmd):  .venv\Scripts\activate.bat
                                     # Windows (PowerShell):  .venv\Scripts\Activate.ps1
pip install -r requirements.txt      # manim, numpy, pillow
python tools/fetch_fonts.py          # the film's three typefaces -> manim/fonts/
```

`fetch_fonts.py` downloads **JetBrains Mono** (system and code), **Source Serif 4** (what the AI says) and **Inter**
(interface and the user), all under the SIL Open Font License, into `manim/fonts/` (which git ignores). Families
already installed on your system are skipped. The two Chinese lines (the warning page before the song, the last
count card) use whatever CJK font Pango finds; installing *Noto Sans CJK* gives the intended look.

Check the install:

```bash
python tools/still.py --times=15.2 --out ../out/check.png
```

This writes one frame (the title shot, song time 15.2 s) to `out/check.png` without rendering a video. If it opens
and shows the orange spark over the launch command, Manim, Cairo, Pango and the fonts all work. Until you add
lyrics (next step) the lyric lines are drawn as rows of dots, and the console says so.

## 3. Add your song and lyrics

**The repository contains no music and no lyric text.** Bring your own and put both into the folder `音頻&歌詞/`
("audio & lyrics") at the root of the repository; git ignores whatever you put there.

| File | Default path (`config.json → paths`) | What it has to be |
| --- | --- | --- |
| Song | `音頻&歌詞/Mili - world.execute (me) ;.wav` | your own audio file of the original song. A `.wav` is what the project was made with; other formats ffmpeg can read work for the Manim render. If your copy has a different amount of silence at the start, shift everything with `config.json → timing.offset` (seconds; positive = later) |
| Lyrics | `音頻&歌詞/Mili - world.execute (me) ;.lrc` | an LRC file with *any* timing, or a plain `.txt`. If the folder holds exactly one `.lrc` / `.txt`, its name does not matter |

The lyric file only has to carry **the same words in the same order**. The time of every line of the film is in
`data/lyric_timing.json` (which has no text); the next command joins your words with those times:

```bash
cd ..                                # back to the repository root
node tools/fill_lyrics.mjs           # -> data/lyrics.json  (local, git ignores it)
```

What it does with your file:

- its own time tags are not used, so an LRC from any source works and moves no cue;
- rows divided differently from the film (two lines in one row, one line over two rows) are re-divided;
- rows that are no line of the film (credits, translations, tags) are passed over;
- if only punctuation or capitals differ, your spelling is kept (keyword lines are always set in capitals); lines with
  other words are listed as a warning;
- if lines of the film are missing from your file, their numbers and song times are listed and nothing is written.

Run it again whenever you change the lyric file. The Manim port reads `data/lyrics.json`; without it, lines are dots.

## 4. Render

Everything below runs from the `manim/` folder with the virtual environment active.

### The whole film

```bash
python tools/render.py
```

Renders the complete film, 960 × 320 at 30 fps, from the silent warning page (5 s before the song) to the end, and
muxes your song in. Output: `out/manim_960x320.mp4` at the repository root. Expect **15–25 minutes** on one CPU
core (about 0.1–0.2 s a frame); Manim renders on a single core.

### Options

```bash
python tools/render.py --fps 60                   # 60 fps (twice the render time)
python tools/render.py --from 59.4 --to 74.2      # one stretch, in SONG seconds (the film starts at -5)
python tools/render.py --shot c1-kw2              # one shot, by its id in ../STORYBOARD.md
python tools/render.py --size 1920x640            # the same 3:1 film at twice the size
python tools/render.py --out /path/to/file.mp4    # where to write
```

All times are **song time**: the audio starts at 0, the warning page runs from −5 to 0, and `STORYBOARD.md` lists
every shot with its id and its start/end in *film* time (song time + 5 s). Audio is cut to the rendered stretch;
when no song file is found the video is silent and the script says so.

### Calling Manim directly

`manim.cfg` in this folder sets 960 × 320 at 30 fps, so the plain Manim command works too (no song is muxed unless
the whole film from −5 s is rendered, in which case `film.py` adds it itself):

```bash
manim film.py WorldExecuteMe                                   # whole film
WEM_FROM=148 WEM_TO=162 manim film.py WorldExecuteMe           # a stretch (song seconds)
WEM_SHOT=cx-fall manim film.py WorldExecuteMe                  # one shot
WEM_W=1920 WEM_H=640 WEM_FPS=60 manim film.py WorldExecuteMe   # another size / frame rate (keep 3:1)
WEM_AUDIO=0 manim film.py WorldExecuteMe                       # never add the song
```

Manim's `-ql` / `-qh` quality flags change nothing here: the size is fixed to the display by `WEM_W` / `WEM_H`.
Manim writes to `manim/media/videos/film/<size><fps>/WorldExecuteMe.mp4`. Use `--disable_caching` if Manim
complains about partial movie files from an earlier run.

## 5. Check frames without rendering

`tools/still.py` draws frames straight to PNG — a few seconds instead of minutes — and is the fastest way to look at
a shot, check your lyrics, or compare before and after a change:

```bash
python tools/still.py --times=-3,15.2,61.98,150 --out ../out/sheet.png     # these song times, as a contact sheet
python tools/still.py --shots --out ../out/all_shots.png                    # one frame from the middle of EVERY shot
python tools/still.py --shots --only c1-kw1,c1-kw2 --cols 2                 # only these shots
```

Each tile is labelled with its song time and shot id (top left, in pink).

## 6. Use it from your own project

`WorldExecuteMe` in `film.py` is an ordinary Manim `Scene`. A display project that drives Manim scenes can import it,
or render it with the commands above and play the MP4.

For a tighter integration, `wem.engine.Film` is the film as a pure function of time, without Manim's animation loop:

```python
import sys; sys.path.insert(0, 'path/to/manim')
from wem.setup import configure
from wem.engine import Film

configure(960, 320)               # Manim config: frame size, fonts
film = Film()
mobjects = film.frame(61.98)      # the Manim mobjects of the frame at song time 61.98 s
# film.start_time = -5 (the warning page), film.end_time = the end of the song; film.shots lists the shots
```

`frame(t)` returns the same picture for the same `t` whatever was drawn before, so frames can be rendered in any
order, in parallel, or on demand.

## 7. How it is built

```
manim/
  film.py                 the Manim Scene: one ValueTracker runs through the song, one updater rebuilds the frame
  manim.cfg               960 x 320, 30 fps
  requirements.txt
  wem/
    data.py               config, beat grid, lyrics, cues, shot list (STORYBOARD.md), palettes
    engine.py             shots -> frames: overlaps, transitions (cut, push, zoom, scan, fade, glitch), overlay, flash
    ctx.py                the canvas-style drawing API of src/engine/draw.js on top of pooled Manim mobjects
    components.py         spark, cursor, the chat client re-laid out for 3:1, controls, toasts
    plates.py             the print plates: paper, keyword type, shadow plates, the four chorus plates, the loop listing
    art.py                the silhouettes as three-ink prints recoloured by palette role
    geom.py               wireframes, outlines, type along paths
    sections/s01..s13     one file per section of the film, one drawing per shot
  tools/render.py         render + mux the song     tools/still.py  still frames     tools/fetch_fonts.py  fonts
```

### What it reads from the main project (nothing is copied by hand)

| File | Used for |
| --- | --- |
| `config.json` | palettes (colour states), timing offsets, typing speed, pre-roll / flash range, spot colours |
| `data/audio_features.json` | beat grid, onsets, levels (beat pulses, kicks) |
| `data/lyrics.json` | the lyric lines with your text (see [§3](#3-add-your-song-and-lyrics)); `data/lyric_timing.json` when it is missing |
| `docs/v4/chat_script.json`, `docs/v4/errors.json` | the written conversation, the error dialogs |
| `src/scenes/cues.js` | the word and drum cues that are not on the beat grid |
| `STORYBOARD.md` | the shot list: id, cut time, lyric lines, colour state, transition |
| `assets/character/*.png` | the silhouettes, separated into their three inks |

If a cue or a cut is corrected in the JS project (and `npm run storyboard` is run), the Manim port follows.

Shots draw in a virtual frame of 1920 × 640 px (twice the display), so type sizes are comparable to the browser
film's 1920 × 1080 frame. Every frame is a pure function of song time, as in the browser renderer.

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
- **Re-composed shots.** Sections 6–14 follow the JS drawing code shot by shot (same events on the same beats and
  cues); sections 1–5 and the execution / count cards are more compact re-compositions of each storyboard moment.
  Some fine detail (the ASCII world, the cut-paper history strip) is drawn more simply.
- Lyric text is dots until `data/lyrics.json` exists.

## 8. Troubleshooting

| Symptom | What to do |
| --- | --- |
| `pip install` fails building `manimpango` / `pycairo` | the Cairo / Pango development packages are missing: install them ([§1](#1-what-you-need)) and run `pip install -r requirements.txt` again |
| `[wem] fonts not found: ...` | run `python tools/fetch_fonts.py` (needs internet once), or install those three families system-wide. Without them Pango substitutes another face and the layout drifts |
| `Font Noto Sans CJK TC not in ...` warning | only the two Chinese lines are affected; install Noto Sans CJK (or any CJK font) to set them in the intended face |
| `[wem] data/lyrics.json not found` and dots instead of words | add your lyric file to `音頻&歌詞/` and run `node tools/fill_lyrics.mjs` at the repository root ([§3](#3-add-your-song-and-lyrics)) |
| `fill_lyrics` lists missing lines | your file lacks some lines of the film; the message gives their numbers and song times. Add them (any timing) and run it again |
| `[render] no audio file` | the song is not at `config.json → paths.audio`; the video is rendered silent. Put it there and render again |
| Picture and song drift apart | your copy of the song has a different lead-in: set `config.json → timing.offset` (seconds; positive makes the picture later) and render a short stretch to check |
| `shot "<id>" failed: ...` printed in a frame | one shot threw; the frame shows the message instead of taking the film down. Please report it with the song time |
| Render is slow | that is expected: Manim is single-threaded. Render stretches in parallel with `--from/--to` and join them with ffmpeg, or check frames with `still.py` first |

The credits and licences of the main project apply unchanged (see `../CREDITS.md`, `../LICENSE`): the character
silhouettes are CC BY-NC-SA 4.0 (credit: Nyankomint), and the song and its lyrics belong to Mili — share a render
only as [Mili's copyright guidelines](https://projectmili.com/copyright-guidelines) allow (personal, non-commercial;
mark AI-generated content).
