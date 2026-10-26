# NIN-VAVE: Sloop n' Slip

**[SLOOP](https://github.com/isod89/sloop-fm1), the live groovebox firmware for the M-VAVE FM-1, with Nine Inch Nails
inside: a drum kit for every song, NIN sounds on the synth tracks, and 27 factory patterns cut from the songs
themselves.**

Everything SLOOP does is still here: three synth tracks and a drum track, twelve engines, parameter locks, fills,
song mode, the web editor. NIN-VAVE swaps SLOOP's CC0 samples for Nine Inch Nails ones and adds what SLOOP leaves
out on purpose: patterns to start from.

> **Status: 1.0 (dev).** Builds on SLOOP 2.8.1 and passes its host tests; not yet run on an FM-1.

## It boots as NIN-VAVE

- The boot screen says **NIN-VAVE / SLOOP N' SLIP**.
- **The first power-on** (coming from SLOOP, or a fresh FM-1) loads **HLAH A**: the Head Like a Hole kit and drums,
  its bass line on track 1 (HLAH BASS), **LETU STAB** on track 2 and **DISC PIANO** on track 3, empty to play over,
  at 115 BPM, the drum track selected. Press **PLAY**.
- The NIN sounds become your first **favourites**, so **PRESETS** lists them first on every synth track (your own
  favourites stay, after them). On the drum track, PRESETS goes **HLAH, TLIE, SANC, ONLY, DISC, ECHO, LETU, DEMN,
  CORO, 999999**, then HLAH's treatments, then SLOOP's kits (808 ... SYN4).
- After that it resumes what you left, as SLOOP does. A **NEW** project starts on the NIN sounds and the HLAH kit.
- (Remove every NIN sound from your favourites and the next power-on is a "first" one again.)

## What's NIN in it

**Ten drum kits**, one per song: the drum track's **KIT** (PRESETS on the drum track).

| KIT | Song | Album |
| --- | --- | --- |
| HLAH, HLAH DP, HLAH TGT, HLAH BRT, HLAH DST | Head Like a Hole (and SLOOP's four treatments of it) | Pretty Hate Machine |
| TLIE | Terrible Lie | Pretty Hate Machine |
| SANC | Sanctified | Pretty Hate Machine |
| ONLY | The Only Time | Pretty Hate Machine |
| DISC | Discipline | The Slip |
| ECHO | Echoplex | The Slip |
| LETU | Letting You | The Slip |
| DEMN | Demon Seed | The Slip |
| CORO | Corona Radiata | The Slip |
| 999999 | 999,999 | The Slip |

Each kit has the song's kick (and a lower KICK 2), snare, a second snare or the clap, closed and open hats, two
percussion hits on the rim, conga and tom lanes, and the song's noise on ride and cowbell. SLOOP's synthesised kits
(808, 909, INDUSTR ...) and your USR / SYN kits are all still there, after the NIN ones on PRESETS.

**NIN sounds** on the synth tracks (PRESETS, SAMPLE engine), played in tune across the keys:

| Preset | From | Was in SLOOP |
| --- | --- | --- |
| DISC PIANO | Discipline, piano | GRAND PNO |
| ECHO BASS | Echoplex, bass | UP BASS |
| DISC MRMBA | Discipline, marimba | VIBES |
| LETU STAB | Letting You, stab synth | HORN STAB |
| DEMN STRGS | Demon Seed, strings | STRING STB |
| CORO DRONE | Corona Radiata, drone (held, looped) | LOFI FLUTE |
| HLAH BASS | Head Like a Hole, bass guitar | SCRATCH |
| HLAH KIT | the Head Like a Hole kit on a synth track | GM KIT |

DUSTY PNO, LOFI KEYS and DEEP BASS are the same sounds, treated.

**27 factory patterns**, the bars that repeat most in each song (or in each named section of The Slip's songs:
V1, CH2, RIFF ...). Loading one sets the drum track to the song's kit and writes its steps, puts the song's bass line
on track 1 with HLAH BASS or ECHO BASS, and sets the length and the tempo. Tracks 2 and 3 are yours.

| Song | Patterns |
| --- | --- |
| Head Like a Hole | HLAH A, B, C |
| Terrible Lie | TLIE A, B, C |
| Sanctified | SANC A, B, C |
| The Only Time | ONLY A, B, C |
| Discipline | DISC INTR, GTR, A1, A2, PIAN, FADE |
| Echoplex | ECHO INTR, GTRI, V1, CH2, MORE |
| Letting You | LETU INTR, MODU, V1, M8, OUTR |
| Demon Seed | DEMN STAR, RIFF, GTRA, HITO, MID, THER (6/4: 24 steps) |
| Corona Radiata | CORO POSS, PRIN |
| 999,999 | 9999 INSE |

(Which patterns there are depends on the extraction: `build/nin/report.txt` lists them with their steps.)
Discipline's and Sanctified's snares could not be told apart from the kick in their mixed drum stems: their
patterns have kick and hats; tap the snare in on the STEP page.

## Load a NIN pattern and jam

1. Hold **HOME** (0.7 s): the menu opens.
2. **SELECT** to the **SEQ** section.
3. **KNOB 3** picks the pattern (**NIN PATTERN**: HLAH A, TLIE B, ECHO V1 ...).
4. **PRESETS** moves the cursor to NIN PATTERN, **OCT+** loads it.
5. Hold **HOME** again to leave the menu, and press **PLAY**.

Then it is SLOOP: play track 2 or 3 over it (DISC PIANO, LETU STAB, DEMN STRGS on PRESETS), mute and solo, change
the kit (KIT USR, SYN, 808 ...), record, punch in the effects (hold FX), save the section (SAVE).

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
