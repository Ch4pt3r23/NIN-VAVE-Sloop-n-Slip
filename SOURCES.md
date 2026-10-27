# Sources

NIN-VAVE's drum kits, its NIN sample sounds and its factory patterns are cut by `tools/nin_kits.py` from Nine Inch
Nails multitracks (`assets/nin-kits/`, the NIN files in `assets/samples-cc0/`, `firmware/src/nin_patterns.h`). The
recordings are Nine Inch Nails'. The GPL covers NIN-VAVE's code, not these excerpts. Nine Inch Nails is not affiliated
with NIN-VAVE, and neither is SLOOP.

## Where the multitracks came from

- **remix.nin.com** (2007-2016): the official Nine Inch Nails remix site. It offered multitracks "for download and
  remixing" (all of *The Slip*, five tracks of *Ghosts I-IV*, songs from *With Teeth* and *Year Zero*, and others),
  and prohibited remixes using other artists' material. It closed in November 2016. History:
  <https://www.nin.wiki/Remix.nin.com>.
- **[nindestruct.com](https://nindestruct.com)** (remix page: <https://nindestruct.com/remix.html>): a fan archive
  (est. 2014, Pyract), not an official site, with no licence stated. It hosts the remix.nin.com multitracks, marked
  "Sourced from remix.nin.com", and the Pretty Hate Machine ones. Its Pretty Hate Machine section credits the
  *Pretty Hate Pack* to "Fine Finch Tails", and marks the Head Like a Hole, Terrible Lie, Sanctified and The Only
  Time multitracks as **"Ripped from Rock Band 3"**. They were not released through remix.nin.com.
- **[archive.org: REMIX.NIN.COM - Nine Inch Nails Remixes](https://archive.org/details/remix-nin-com-collection)**
  (uploaded 2018-06-17): the remixes fans submitted to remix.nin.com. No licence stated. Not used here.

The multitracks' own Readme files give only the song, tempo and time signature, no licence. No licence text was found
on any of the pages above (checked 2026-10-26).

## The Slip (2008), from remix.nin.com

| Song | Tempo | Kit and patterns from |
| --- | --- | --- |
| Discipline | 122, 4/4 | Drums, Perc, Bass; Piano and Marimba as the PIANO and VIBES sounds |
| Echoplex | 124, 4/4 | Drums, Clap, Perc, Bass (also the BASS sound) |
| Letting You | 91, 4/4 | Drums, Stabsynth (also the HORNS sound), Bass |
| Demon Seed | 132, 6/4 | Drums, Breakdown, Bass; Strings as the STRGS sound |
| Corona Radiata | 55, 4/4 | Drums, Noise, Drone (also the FLUTE sound) |
| 999,999 | 91, 4/4 | Slip, Andromeda, Bass |

Tempos, time signatures and the section names of the patterns (V1, CH1, RIFF ...) come from each multitrack's
"Markers and Tempo" MIDI file. The grid's start is measured from the drums.

## NIN-VAVE 1.1: The Downward Spiral, With Teeth, Year Zero

From nindestruct.com's remix page (kept on the maintainer's NAS: `NIN-Multitracks/nindestruct`), as it describes them:

| Song | Album | Multitrack (nindestruct.com) | Kit, patterns, pack from |
| --- | --- | --- | --- |
| Closer | The Downward Spiral (1994) | `Multitrack.Closer.zip`, ripped from Rock Band 3 | drums_1 (kick), drums_2 (snare), drums_3 (cymbals), song, rhythm (bass) |
| March of the Pigs | The Downward Spiral | `Multitrack.MOTP.zip`, ripped from Rock Band | drums, bg sounds, bass synth |
| The Hand That Feeds | With Teeth (2005) | `Multitrack.THTF.zip`: the multitrack NIN released as a GarageBand session in 2005 | Drum comp, Synthetic Perc, Percussion, Bass |
| Survivalism | Year Zero (2007) | `Multitrack.Survivalism.zip`, "Sourced from Y34RZ3R0R3M1X3D" (Year Zero Remixed's multitracks) | Drm, Noiz+Nord Perc, Bass |

Their tempos have no markers file: Closer's comes from its kick and snare, the others' from the tempo near a first
estimate where the drums sit tightest on the 16th grid (The Hand That Feeds 128.0, Survivalism 130.0).

The NIN packs (`tools/nin_pack.py`, built into `build/nin/packs/`, not checked in) cut their kits and instruments
from the same multitracks.

## Pretty Hate Machine (1989), ripped from Rock Band 3

| Song | Multitrack | Kit and patterns from |
| --- | --- | --- |
| Head Like a Hole | `Multitrack.HLAH.zip` (8 stems, 115 BPM) | Kick, Snare, Cymbals & Toms, Extras, Bass Guitar (also the SCRCH sound, HLAH BASS); the Pretty Hate Pack's *Vocal & Percussive Loops* |
| Terrible Lie | `pretty.hate.pack.zip`, folder 3 | Kick, Snare, Drums Other, Other Synths & FX, Bass |
| Sanctified | `pretty.hate.pack.zip`, folder 1 | Kick, Drums Other, Percussion FX & Chants, Bass |
| The Only Time | `pretty.hate.pack.zip`, folder 2 | Kick, Snare, Drums Other, Other Synths & FX, Bass |

The Pretty Hate Pack's folders carry no song names. They were matched by length and tempo: folder 4 is Head Like a
Hole, with the same length and tempo as its own multitrack. Tempos are the bpm at which each song's bars repeat
most: Head Like a Hole 115, Terrible Lie 87.6, Sanctified 107.7, The Only Time 94.

The originals are kept on the maintainer's NAS; `tools/nin_kits.py` lists every stem it reads.

## What NIN-VAVE replaced in SLOOP

SLOOP's CC0 sample sets (CREDITS.txt in `assets/samples-cc0/`) made room for the NIN material. The CC0 acoustic kit's
files stay in `assets/samples-cc0/KIT/`: a build without `assets/nin-kits/HLAH` uses them as the GM kit again.
