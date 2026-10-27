# NIN-VAVE: Sloop n' Slip

**[SLOOP](https://github.com/isod89/sloop-fm1), the live groovebox firmware for the M-VAVE FM-1, turned into a Nine
Inch Nails instrument: 14 NIN drum kits, 22 NIN sounds, 33 factory patterns cut from the songs themselves, and NIN
packs for the four user sample slots.**

Everything SLOOP does is still here: three synth tracks and a drum track, twelve engines, parameter locks, fills,
song mode, punch-in effects, pitch bend, the web editor. NIN-VAVE puts the NIN material first everywhere and keeps
only a few of SLOOP's own sounds on the knobs: the 808, 909 and acid, and some 90s studio staples.

> **Status: 1.1 (dev).** Builds on SLOOP 2.8.1 and passes its host tests (but for two cost checks SLOOP 2.8.1
> fails too); 1.0 runs on the FM-1.

## It boots as NIN-VAVE

- The boot screen says **NIN-VAVE / SLOOP N' SLIP**.
- **The first power-on** (coming from SLOOP, an older NIN-VAVE, or a fresh FM-1) loads **HLAH A**: the Head Like a
  Hole kit and drums, its bass line on track 1 (NIN.HLAH BASS), **NIN.LETU STAB** on track 2 and **NIN.DISC PIANO**
  on track 3, empty to play over, at 115 BPM. Press **PLAY**. After that it resumes what you left, as SLOOP does.
- **PRESETS lists NIN first.** On a synth track: the 22 `NIN.` sounds (the kind column says NIN), then 808 BOOM,
  ACID 303, SUB BASS, DX RHODES, ENSEMBLE, BOWED MTL, NZ METAL, BITCRUSH. On the drum track: the 14 `NIN.` kits, then
  808, 909, 606, VINTAGE, INDUSTR, then your USR and SYN kits.
- SLOOP's other 134 sounds and 27 kits are off the knobs, not gone: projects that use them still load and play them.

## What's NIN in it

**14 drum kits**, one per song (drum track: **PRESETS**):

| KIT | Song | Album |
| --- | --- | --- |
| NIN.HLAH (and NIN.DEEP, NIN.TIGHT, NIN.BRITE, NIN.DUST: SLOOP's four treatments of it) | Head Like a Hole | Pretty Hate Machine |
| NIN.TLIE · NIN.SANC · NIN.ONLY | Terrible Lie · Sanctified · The Only Time | Pretty Hate Machine |
| NIN.MOTP · NIN.CLSR | March of the Pigs · Closer | The Downward Spiral |
| NIN.THTF | The Hand That Feeds | With Teeth |
| NIN.SURV | Survivalism | Year Zero |
| NIN.DISC · NIN.ECHO · NIN.LETU · NIN.DEMN · NIN.CORO · NIN.9999 | Discipline · Echoplex · Letting You · Demon Seed · Corona Radiata · 999,999 | The Slip |

Each kit has the song's kick (and a lower KICK 2), snare, a second snare or the clap, closed and open hats, two
percussion hits on the rim, conga and tom lanes, and the song's noise on ride and cowbell.

**22 NIN sounds** (synth tracks: **PRESETS**, SAMPLE engine), in tune across the keys. Each NIN recording comes three
ways: as recorded, and twice bent by the SAMPLE engine itself (tuning, bit depth, drive, filter, envelope, sends):

| Recording | As recorded | Bent |
| --- | --- | --- |
| Head Like a Hole, bass guitar | NIN.HLAH BASS | NIN.HLAH FUZZ, NIN.HLAH SUB |
| Echoplex, bass | NIN.ECHO BASS | NIN.ECHO SUB, NIN.ECHO FUZZ |
| Discipline, piano | NIN.DISC PIANO | NIN.PIANO RUST, NIN.PIANO DARK |
| Letting You, stab synth | NIN.LETU STAB | NIN.STAB DIRT, NIN.STAB OCT |
| Demon Seed, strings | NIN.DEMN STRGS | NIN.STRGS SLOW, NIN.STRGS BURN |
| Discipline, marimba | NIN.DISC MRMBA | NIN.MRMBA CRUSH, NIN.MRMBA ECHO |
| Corona Radiata, drone (held) | NIN.CORO DRONE | NIN.DRONE DARK, NIN.DRONE GRIT |
| the Head Like a Hole kit, on the keys | NIN.HLAH KIT | |

Bend them further live: SLOOP's pitch bend, LFOs, the FILTER, the INSERT effects (SOFT, HARD, FOLD, FUZZ, CRUSH ...)
and the 27 punch-in effects (hold **FX**).

**33 factory patterns**, the bars that repeat most in each song (or in each named section, for The Slip). Loading one
sets the drum track to the song's kit and writes its steps, puts the song's bass line on track 1, and sets the length
and the tempo. Tracks 2 and 3 are yours.

| Song | Patterns |
| --- | --- |
| Head Like a Hole · Terrible Lie · Sanctified · The Only Time | HLAH A B C · TLIE A B C · SANC A B C · ONLY A B C |
| Closer | CLSR A B C |
| The Hand That Feeds | THTF A B C |
| Discipline · Echoplex · Letting You | DISC A1 PIAN FADE · ECHO V1 CH2 MORE · LETU INTR M8 OUTR |
| Demon Seed (6/4: 24 steps) · Corona Radiata · 999,999 | DEMN STAR GTRA MID · CORO POSS PRIN · 9999 INSE |

March of the Pigs (its metre keeps moving) and Survivalism (its kick, snare and hats would not come apart in one
dense stem) have kits but no patterns; Discipline's and Sanctified's patterns have no snare (tap it in on the STEP
page). `build/nin/report.txt` lists every pattern with its steps.

## NIN packs: more NIN in the user sample slots

The FM-1 keeps four user sample slots (USR1..USR4, about 7 s each) besides the firmware. A **NIN pack** fills all
four with more NIN: full 16-pad kits at a better rate than the built-in ones, and NIN instruments sampled over
several notes. Load one, play it, load another: a pack replaces the slots.

```sh
python3 tools/nin_pack.py list                 # the packs
python3 tools/nin_pack.py load TDS             # FM-1 on USB: USR1..USR4 <- the pack (about a minute)
```

| Pack | USR1 | USR2 | USR3 | USR4 |
| --- | --- | --- | --- | --- |
| TDS (The Downward Spiral) | NIN.CLSR kit (16 pads) | NIN.MOTP kit (16 pads) | Closer bass, 4 notes | March of the Pigs bass synth, 4 notes |

Then: drum track, PRESETS to **USR1** or **USR2** for the kits; a synth track on the SAMPLE engine, **SET USR3** or
**USR4** for the instruments (SAVE > USER stores the sound as a user preset).

## nin.chapter23.uk: install from the browser

**[nin.chapter23.uk](https://nin.chapter23.uk)** installs everything from Chrome or Edge, no terminal: **Install the
firmware** (SLOOP's own installer, for this package), and each NIN pack with a button (tick the slots to write). The
pack installer (`web/nin_packs.js`) sends what `tools/fm1_sample_upload.py` sends, frame for frame
(`web/test_nin_packs.mjs` checks every slot of every pack).

Publish a new firmware or new packs (after `./build.sh` and `tools/nin_pack.py build`):

```sh
tools/deploy_nin_site.sh 1.2                       # build/site from build/nin-vave.fwsc + build/nin/packs/*, test, deploy
tools/deploy_nin_site.sh 1.2 --dry-run             # everything but the upload
```

The site is static (`tools/make_nin_site.py`), served by Cloudflare (`site/wrangler.jsonc`: the Worker `nin-vave`, the
custom domain nin.chapter23.uk); `npx wrangler login` once on the machine that deploys.

## Load a NIN pattern and jam

1. Hold **HOME** (0.7 s): the menu opens.
2. **SELECT** to the **SEQ** section.
3. **KNOB 3** picks the pattern (**NIN PATTERN**: HLAH A, TLIE B, ECHO V1 ...).
4. **PRESETS** moves the cursor to NIN PATTERN, **OCT+** loads it.
5. Hold **HOME** again to leave the menu, and press **PLAY**.

Then it is SLOOP: play track 2 or 3 over it (NIN.DISC PIANO, NIN.LETU STAB, NIN.DEMN STRGS on PRESETS), mute and solo, change
the kit (NIN.CLSR, USR1, 808 ...), record, punch in the effects (hold FX), save the section (SAVE).

Loading a pattern replaces the drum track's and track 1's steps: save first what you want to keep.

The rest of the FM-1's controls: SLOOP's [complete guide](GUIDE.md) and [manual](SLOOP.md). SLOOP's own README is
[SLOOP-README.md](SLOOP-README.md).

## Build

As SLOOP ([BUILDING.md](BUILDING.md)): Linux x86-64 natively (macOS / Windows with Docker), the JieLi toolchain and
the AC79 SDK.

```sh
./build.sh                          # -> build/nin-vave.fwsc, identity FM-1_950
tests/run_tests.sh                  # SLOOP's host tests
python3 tools/fm1_install.py build/nin-vave.fwsc
```

The NIN material is checked in (`assets/nin-kits/`, the NIN WAVs in `assets/samples-cc0/`,
`firmware/src/nin_patterns.h`). To cut it again, or from more songs, put the multitracks under
`~/.cache/ninvave/stems` and run `tools/nin_kits.py` (numpy, scipy, soundfile, librosa, mido): it also renders every
pattern to `build/nin/patterns/*.wav` to audition. Where every sound comes from: [SOURCES.md](SOURCES.md).

Going back: SLOOP, Felucca or the official firmware with the [FM-1 Firmware Hub](https://thefirmwarehub.com) or
M-VAVE's M-UPGRADE. If it will not start, hold **OCT-** while switching on (the USB rescue). Installing firmware is at
your own risk.

## Credits and licence

SLOOP by isod89, on Felucca by Leo Kuroshita (Hügelton Instruments); everything they and SLOOP's contributors made is
theirs, under GPL-3.0 ([LICENSING.md](LICENSING.md), [SLOOP-README.md](SLOOP-README.md#credits-and-thanks)). The NIN
kits, sounds and patterns are excerpts of Nine Inch Nails recordings and stay theirs ([SOURCES.md](SOURCES.md)).
NIN-VAVE is not affiliated with Nine Inch Nails, M-VAVE or SLOOP.
