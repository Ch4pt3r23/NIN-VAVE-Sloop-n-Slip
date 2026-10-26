#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""NIN-VAVE: drum kits, melodic sounds and factory patterns cut from Nine Inch Nails multitracks.

    python3 tools/nin_kits.py [STEMS_DIR]        (default: ~/.cache/ninvave/stems; needs numpy, soundfile, librosa, mido)

Writes (all checked in, so the firmware builds without the stems):
  assets/nin-kits/<TAG>/*.wav + kit.json     a drum kit per song (gen_samples.py: NIN kits, GM-mapped)
  assets/samples-cc0/<SET>/00_NIN_*_m<n>.wav  the NIN sounds in SLOOP's melodic sample sets (PIANO, BASS, ...)
  firmware/src/nin_patterns.h                the factory patterns (project.c: NIN PATTERNS)
  build/nin/report.txt                       what was picked, and the patterns as text
Sources and credits: SOURCES.md.
"""
import json
import sys
from pathlib import Path

import librosa
import mido
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

ROOT = Path(__file__).resolve().parent.parent
STEMS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache/ninvave/stems"
KITS = ROOT / "assets/nin-kits"
CC0 = ROOT / "assets/samples-cc0"
OUT_H = ROOT / "firmware/src/nin_patterns.h"
REPORT = ROOT / "build/nin/report.txt"
SR = 44100                                       # analysis rate
KIT_RATE, HAT_RATE = 16000, 22050                # stored rates (gen_samples.py resamples): lo-fi, the metal keeps more top
PER_SONG = 3                                     # patterns per song

HLAH = "hlah-multitrack/Head Like a Hole (115 BPM)/"
PHP = "php-pack/Pretty Hate Pack/"
SLIP = "slip/"
# drums: stems the hits come from (a mixed stem is sorted by band); the first kick-ish stem gives the kick.
# perc: stems for the percussion / FX lanes. bass: the bass line of the patterns. grid: "track" finds the beats
# (bpm is a hint), "fixed" trusts bpm from the start of the file (The Slip's markers file says so).
SONGS = [
    dict(tag="HLAH", name="HEAD LIKE A HOLE", bpm=115.0, grid="track", bar=4,
         kick=HLAH + "01. Kick.wav", snare=HLAH + "02. Snare.wav", hats=HLAH + "03. Cymbals & Toms.wav",
         perc=[HLAH + "08. Extras.wav", PHP + "4/08 Vocal & Percussive Loops.flac"], bass=HLAH + "04. Bass Guitar.wav"),
    dict(tag="TLIE", name="TERRIBLE LIE", bpm=87.6, grid="track", bar=4,
         kick=PHP + "3/01 Kick.flac", snare=PHP + "3/02 Snare.flac", hats=PHP + "3/03 Drums Other.flac",
         perc=[PHP + "3/08 Other Synths & FX.flac"], bass=PHP + "3/04 Bass.flac"),
    dict(tag="SANC", name="SANCTIFIED", bpm=107.7, grid="track", bar=4,
         kick=PHP + "1/01 Kick.flac", snare=PHP + "1/02 Drums Other.flac", hats=PHP + "1/02 Drums Other.flac",
         perc=[PHP + "1/07 Percussion FX & Chants.flac"], bass=PHP + "1/03 Bass.flac"),
    dict(tag="ONLY", name="THE ONLY TIME", bpm=94.0, grid="track", bar=4,
         kick=PHP + "2/01 Kick.flac", snare=PHP + "2/02 Snare.flac", hats=PHP + "2/03 Drums Other.flac",
         perc=[PHP + "2/07 Other Synths & FX.flac"], bass=PHP + "2/04 Bass.flac"),
    dict(tag="DISC", name="DISCIPLINE", bpm=122.0, grid="fixed", bar=4,
         drums=SLIP + "Multitrack.Discipline/Audio Files/Discipline Drums.wav",
         perc=[SLIP + "Multitrack.Discipline/Audio Files/Discipline Perc.wav"],
         bass=SLIP + "Multitrack.Discipline/Audio Files/Discipline Bass.wav",
         markers=SLIP + "Multitrack.Discipline/Discipline Markers and Tempo.mid"),
    dict(tag="ECHO", name="ECHOPLEX", bpm=124.0, grid="fixed", bar=4,
         drums=SLIP + "Multitrack.Echoplex/Audio Files/Echoplex Drums.wav",
         clap=SLIP + "Multitrack.Echoplex/Audio Files/Echoplex Clap.wav",
         perc=[SLIP + "Multitrack.Echoplex/Audio Files/Echoplex Perc.wav"],
         bass=SLIP + "Multitrack.Echoplex/Audio Files/Echoplex Bass.wav",
         markers=SLIP + "Multitrack.Echoplex/Echoplex markers and Tempo.mid"),
    dict(tag="LETU", name="LETTING YOU", bpm=91.0, grid="fixed", bar=4,
         drums=SLIP + "Multitrack.Letting.You/Audio FIles/LettingU Drums.wav",
         perc=[SLIP + "Multitrack.Letting.You/Audio FIles/LettingU Stabsynth.wav"],
         bass=SLIP + "Multitrack.Letting.You/Audio FIles/LettingU Bass.wav",
         markers=SLIP + "Multitrack.Letting.You/Letting You Markers and Tempo.mid"),
    dict(tag="DEMN", name="DEMON SEED", bpm=132.0, grid="fixed", bar=6,
         drums=SLIP + "Multitrack.Demon.Seed/Audio Files/Demon Seed Drums.wav",
         perc=[SLIP + "Multitrack.Demon.Seed/Audio Files/Demon Seed Breakdown.wav"],
         bass=SLIP + "Multitrack.Demon.Seed/Audio Files/Demon Seed Bass.wav",
         markers=SLIP + "Multitrack.Demon.Seed/Demon Seed Markers and Tempo.mid"),
    dict(tag="CORO", name="CORONA RADIATA", bpm=55.0, grid="fixed", bar=4,
         drums=SLIP + "Multitrack.Corona.Radiata/Audio Files/Corona Radiata Drums.wav",
         perc=[SLIP + "Multitrack.Corona.Radiata/Audio Files/Corona Radiata Noise.wav"],
         bass=SLIP + "Multitrack.Corona.Radiata/Audio Files/Corona Radiata Drone.wav",
         markers=SLIP + "Multitrack.Corona.Radiata/Corona Radiata markers.mid"),
    dict(tag="9999", name="999,999", bpm=91.0, grid="fixed", bar=4,
         drums=SLIP + "Multitrack.999999/Audio Files/999,999 Slip.wav",
         perc=[SLIP + "Multitrack.999999/Audio Files/999,999 Andromeda.wav"],
         bass=SLIP + "Multitrack.999999/Audio Files/999,999 Bass.wav",
         markers=SLIP + "Multitrack.999999/999,999 markers and tempo.mid"),
]
# the NIN sounds in SLOOP's melodic sets (the set keeps its number: presets and projects still find it)
MELODIC = {
    "PIANO": ("DISC PIANO", SLIP + "Multitrack.Discipline/Audio Files/Discipline Piano.wav", "piano"),
    "BASS": ("ECHO BASS", SLIP + "Multitrack.Echoplex/Audio Files/Echoplex Bass.wav", "bass"),
    "VIBES": ("DISC MARIMBA", SLIP + "Multitrack.Discipline/Audio Files/Discipline Marimba.wav", "keys"),
    "HORNS": ("LETU STAB", SLIP + "Multitrack.Letting.You/Audio FIles/LettingU Stabsynth.wav", "keys"),
    "STRGS": ("DEMN STRINGS", SLIP + "Multitrack.Demon.Seed/Audio Files/Demon Seed Strings.wav", "keys"),
    "FLUTE": ("CORO DRONE", SLIP + "Multitrack.Corona.Radiata/Audio Files/Corona Radiata Drone.wav", "keys"),
    "SCRCH": ("HLAH BASS", HLAH + "04. Bass Guitar.wav", "bass"),
}
# a lane's GM notes (drums.c LANE_NOTE and the GM map) -> the kit's sound and its root (a zone pitched around it)
LANES = {   # sound: [(lo, hi, root)]
    "kick": [(36, 36, 36), (35, 35, 38)],                       # KICK 2: the kick two semitones down
    "snare": [(38, 38, 38)], "snare2": [(40, 40, 40)], "clap": [(39, 39, 39)],
    "chh": [(42, 42, 42), (44, 44, 44), (69, 70, 70)],          # (the shaker lane: the closed hat, higher)
    "ohh": [(46, 46, 46), (49, 49, 49), (52, 52, 52), (55, 55, 55), (57, 57, 57)],   # open hat; the crash a longer one
    "perc1": [(37, 37, 37), (62, 64, 63)],                      # rim, conga
    "perc2": [(41, 41, 43), (43, 43, 43), (45, 45, 43), (47, 48, 48), (50, 50, 48)],   # the toms: low and high
    "fx": [(51, 51, 51), (53, 53, 53), (59, 59, 59), (56, 56, 56)],   # ride, cowbell: the song's noise
}
SECONDS = dict(kick=0.30, snare=0.32, snare2=0.28, clap=0.28, chh=0.07, ohh=0.26, perc1=0.20, perc2=0.24, fx=0.34)
GAIN_DB = dict(chh=-7, ohh=-8, perc1=-3, perc2=-3, fx=-5)
LANE_NOTE = [36, 35, 38, 39, 42, 46, 44, 37, 40, 43, 48, 49, 51, 70, 63, 56]   # drums.c (the 16 lanes)
PAT_LANES = {"kick": 0, "snare": 2, "chh": 4, "ohh": 5, "perc": 7}          # pattern roles -> lanes

_cache = {}


def load(rel):
    if rel not in _cache:
        y, _ = librosa.load(STEMS / rel, sr=SR, mono=True)
        _cache[rel] = y.astype(np.float32)
    return _cache[rel]


BANDS = dict(low=(20, 150), mid=(300, 4000), high=(6000, 20000))


def features(y, o):
    """band shares of the first 60 ms, centroid, decay (s to -30 dB), peak"""
    seg = y[o:o + int(0.06 * SR)]
    if len(seg) < 256:
        return None
    spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    tot = spec.sum() + 1e-12
    share = {b: float(spec[(f >= lo) & (f < hi)].sum() / tot) for b, (lo, hi) in BANDS.items()}
    env = np.abs(y[o:o + int(0.8 * SR)])
    pk = env.max() + 1e-9
    w = 256
    env = np.array([env[i:i + w].max() for i in range(0, len(env), w)])
    below = np.where(env < pk * 0.0316)[0]
    decay = (below[0] * w / SR) if len(below) else 0.8
    cen = float((spec * f).sum() / tot)
    return dict(share=share, cen=cen, decay=decay, peak=float(pk))


def onsets(y):
    env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=512)
    return librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=512, units="samples", backtrack=True)


ROLE_TEST = {
    "kick": lambda F: F["share"]["low"] > 0.45,
    "snare": lambda F: F["share"]["low"] < 0.3 and F["share"]["mid"] > 0.35 and 1000 < F["cen"] < 6000 and F["decay"] > 0.06,
    "chh": lambda F: F["share"]["high"] > 0.35 and F["decay"] < 0.12 and F["share"]["low"] < 0.15,
    "ohh": lambda F: F["share"]["high"] > 0.3 and F["decay"] > 0.18 and F["share"]["low"] < 0.15,
    "any": lambda F: True,
}


def pick(rels, role, avoid=()):
    """a typical, clean hit of the role over the stems: well apart from the next onset, loud but not the loudest"""
    cands = []
    for rel in rels:
        y = load(rel)
        on = onsets(y)
        for i, o in enumerate(on[:4000]):
            gap = (on[i + 1] if i + 1 < len(on) else len(y)) - o
            if gap < 0.09 * SR:
                continue
            F = features(y, o)
            if F and F["peak"] > 0.03 and ROLE_TEST[role](F) and all(abs(F["cen"] - a) > 300 for a in avoid):
                cands.append((F["peak"], rel, o, gap, F["cen"]))
    if not cands:
        return None
    cands.sort(key=lambda c: c[0])
    p, rel, o, gap, cen = cands[int(len(cands) * 0.75)]
    return load(rel)[o:o + gap], cen


def trim(x, seconds, db=0):
    # the attack on time: 2 ms before the first sample at a quarter of the peak (an onset can sit on the bleed
    # before the hit: a snare 30 ms late on the FM-1's step otherwise)
    pk = np.abs(x).max() + 1e-9
    a = int(np.argmax(np.abs(x) > pk * 0.25))
    x = x[max(0, a - int(0.002 * SR)):][:int(seconds * SR)].astype(np.float64).copy()
    pk = np.abs(x).max() + 1e-9
    loud = np.where(np.abs(x) > pk * 0.004)[0]
    if len(loud):
        x = x[:loud[-1] + 64]
    fade = min(len(x) // 3, int(0.012 * SR))
    x[len(x) - fade:] *= np.linspace(1, 0, fade)
    return x / pk * 0.95 * 10 ** (db / 20)


def kit_of(song):
    """the kit's sounds: role -> samples (float, SR)"""
    sep = "kick" in song
    drums = [song["kick"], song["snare"], song["hats"]] if sep else [song["drums"]]
    perc = song["perc"]
    out, cens = {}, []
    for role, rels, test in [("kick", [song["kick"]] if sep else drums, "kick" if not sep else "any"),
                             ("snare", [song["snare"]] if sep else drums, "snare"),
                             ("chh", [song["hats"]] if sep else drums, "chh"),
                             ("ohh", [song["hats"]] if sep else drums, "ohh")]:
        r = pick(rels, test)
        if r is None and test != "any":
            r = pick(rels, "any")
        if r:
            out[role] = r[0]
            cens.append(r[1])
    r = pick([song["clap"]], "any") if "clap" in song else pick(drums, "snare", avoid=cens)
    if r:
        out["clap" if "clap" in song else "snare2"] = r[0]
    for role in ("perc1", "perc2", "fx"):
        r = pick(perc, "any", avoid=cens)
        if r:
            out[role] = r[0]
            cens.append(r[1])
    # the lanes a song has no sound for borrow the nearest one
    for want, have in [("snare2", "snare"), ("clap", "snare2"), ("ohh", "chh"), ("chh", "ohh"),
                       ("perc1", "snare"), ("perc2", "perc1"), ("fx", "perc2")]:
        if want not in out and have in out:
            out[want] = out[have]
    return {k: trim(v, SECONDS[k], GAIN_DB.get(k, 0)) for k, v in out.items()}


# ---- the beat grid and the patterns
def markers(song):
    """[(beat, name)] from The Slip's markers and tempo file"""
    m = mido.MidiFile(STEMS / song["markers"])
    t, out = 0, []
    for msg in mido.merge_tracks(m.tracks):
        t += msg.time
        if msg.type == "marker":
            out.append((t / m.ticks_per_beat, msg.text.strip()))
    return out


def grid_of(song, n):
    """16ths (samples) from the first downbeat, and [(step, section name)]"""
    if song["grid"] == "fixed":
        # the tempo is exact (the markers file), the start may not be: the grid goes where the kicks and snares
        # land (their circular mean phase on the 16th)
        step = SR * 60 / song["bpm"] / 4
        hits = np.concatenate([band_onsets(song["drums"], "low", 0.3), band_onsets(song["drums"], "mid", 0.3)])
        ph = 2 * np.pi * (hits % step) / step
        off = np.angle(np.exp(1j * ph).mean()) / (2 * np.pi) * step   # signed: -half .. +half a step
        song["offset_ms"] = off * 1000 / SR
        g = np.clip(np.arange(0, n, step) + off, 0, None).astype(int)   # (step k stays step k)
        return g, [(int(round(b * 4)), name) for b, name in markers(song)]
    k, s = load(song["kick"]), load(song["snare"])
    m = min(len(k), len(s))
    _, beats = librosa.beat.beat_track(y=k[:m] + s[:m], sr=SR, hop_length=512, units="samples", bpm=song["bpm"])
    ke, se = np.abs(k), np.abs(s)
    def energy(e, b): return sum(e[x:x + 2048].sum() for x in b if x + 2048 < m)
    ph = max(range(4), key=lambda p: energy(ke, beats[p::4]) + energy(ke, beats[p + 2::4])
             - energy(se, beats[p::4]) - energy(se, beats[p + 2::4]))
    beats = beats[ph:]
    g = []
    for a, b in zip(beats[:-1], beats[1:]):
        g += [a + (b - a) * q // 4 for q in range(4)]
    return np.array(g), []


_bands = {}
# a hit of a mixed drum stem, for the patterns: looser than ROLE_TEST (which wants one clean sample): processed
# snares carry low end. A kick: the lows rule; a snare: not a kick, and more mids than top (the hats: the high band)
PAT_TEST = {
    "kick": lambda F: F["share"]["low"] > 0.4,
    "snare": lambda F: F["share"]["low"] <= 0.4 and F["share"]["mid"] > F["share"]["high"],
}


def band_onsets(rel, band, thr):
    """the hits of a stem (samples): onsets of the stem filtered to the band when it is a mixed one (a whole kit,
    'Drums Other'), of the stem as it is when it holds one drum; those louder than thr x its 90th percentile"""
    key = (rel, band)
    if key not in _bands and mixed(rel) and band in ("low", "mid"):
        # a whole kit in one stem: each hit is a kick (the lows rule) or a snare (the mids, little low end) by its
        # own first 60 ms, as the kit's sounds are picked (ROLE_TEST); a filter alone hears the kick's click as a snare
        y = load(rel)
        on = onsets(y)
        keep, pk = [], []
        for o in on:
            F = features(y, o)
            if F and PAT_TEST["kick" if band == "low" else "snare"](F):
                keep.append(o)
                pk.append(np.abs(y[o:o + 4096]).max())
        _bands[key] = (np.array(keep, dtype=int), np.array(pk))
    if key not in _bands:
        y = load(rel)
        if mixed(rel):
            lo, hi = BANDS[band]
            sos = (butter(4, hi, btype="low", fs=SR, output="sos") if lo <= 20 else
                   butter(4, [lo, min(hi, SR / 2 - 200)], btype="band", fs=SR, output="sos"))
            y = sosfiltfilt(sos, y).astype(np.float32)
        on = onsets(y)
        pk = np.array([np.abs(y[o:o + 4096]).max() for o in on]) if len(on) else np.array([])   # (backtracked: ~90 ms)
        _bands[key] = (on, pk)
    on, pk = _bands[key]
    return on[pk >= np.percentile(pk, 90) * thr] if len(pk) else on


def mixed(rel):
    return any(w in rel for w in ("Drums", "Other", "Cymbals"))


def band_hits(rel, grid, band, thr):
    """per 16th: a hit of the band near the step"""
    pos = band_onsets(rel, band, thr)
    hits = np.zeros(len(grid), bool)
    half = np.median(np.diff(grid)) / 2
    for p in pos:
        j = int(np.argmin(np.abs(grid - p)))
        if abs(grid[j] - p) <= half:
            hits[j] = True
    return hits


def bass_notes(y, grid, a, n):
    """the MIDI note starting on each of n steps from step a (0 = none)"""
    idx = [grid[a + i] for i in range(n)] + [grid[a + n] if a + n < len(grid) else len(y)]
    seg = y[idx[0]:idx[n]]
    if len(seg) < 4096:
        return [0] * n
    f0 = librosa.yin(seg, fmin=30, fmax=400, sr=SR, frame_length=4096, hop_length=512)
    rms = np.array([np.sqrt(np.mean(y[idx[i]:idx[i + 1]] ** 2)) for i in range(n)])
    loud = rms > max(rms.max() * 0.3, 0.01)
    out, prev = [0] * n, 0
    for i in range(n):
        if not loud[i]:
            prev = 0
            continue
        fa, fb = (idx[i] - idx[0]) // 512 + 1, max((idx[i + 1] - idx[0]) // 512, (idx[i] - idx[0]) // 512 + 2)
        note = int(round(librosa.hz_to_midi(np.median(f0[fa:fb]))))
        if not prev or note != prev:
            out[i] = note
        prev = note
    return out


def patterns_of(song):
    if "kick" in song:
        tracks = dict(kick=(song["kick"], "low", 0.3), snare=(song["snare"], "mid", 0.3),
                      chh=(song["hats"], "high", 0.2))
    else:
        tracks = dict(kick=(song["drums"], "low", 0.25), snare=(song["drums"], "mid", 0.35),
                      chh=(song["drums"], "high", 0.2))
    tracks["perc"] = (song["perc"][0], "mid", 0.4)
    n = min(len(load(r)) for r, _, _ in tracks.values())
    grid, secs = grid_of(song, n)
    hits = {role: band_hits(rel, grid, band, thr) for role, (rel, band, thr) in tracks.items()}
    steps = song["bar"] * 4
    nbar = len(grid) // steps - 1
    def bar_key(b):
        return tuple(int(sum(1 << i for i in range(steps) if hits[r][b * steps + i])) for r in PAT_LANES if r in hits)
    pats = []
    if secs:                                    # a pattern per named section: its most common bar
        bounds = secs + [(nbar * steps, "")]
        for (s0, name), (s1, _) in zip(bounds[:-1], bounds[1:]):
            bars = [b for b in range(s0 // steps, min(s1 // steps, nbar)) if bar_key(b)[0] or bar_key(b)[1]]
            if len(bars) < 2:
                continue
            counts = {}
            for b in bars:
                counts.setdefault(bar_key(b), []).append(b)
            key, where = max(counts.items(), key=lambda kv: len(kv[1]))
            pats.append((name, key, where[0], len(where), len(bars)))
    else:
        counts = {}
        for b in range(nbar):
            k = bar_key(b)
            if k[0] or k[1]:
                counts.setdefault(k, []).append(b)
        for i, (key, where) in enumerate(sorted(counts.items(), key=lambda kv: -len(kv[1]))[:PER_SONG]):
            pats.append(("ABC"[i], key, where[0], len(where), nbar))
    seen, keep = set(), []
    for p in sorted(pats, key=lambda p: -p[3]):                 # the most played first, no repeats
        if p[1] not in seen:
            seen.add(p[1])
            keep.append(p)
    keep = sorted(keep[:PER_SONG], key=lambda p: p[2])          # in song order
    y = load(song["bass"])
    return [dict(name=p[0], masks=dict(zip([r for r in PAT_LANES if r in hits], p[1])), bar=p[2], rep=p[3],
                 bass=bass_notes(y, grid, p[2] * steps, steps), steps=steps) for p in keep]


def short(name):
    s = "".join(c for c in name.upper() if c.isalnum() or c == " ").replace(" ", "")
    return s[:4] or "A"


def melodic():
    out = []
    for setname, (desc, rel, kind) in MELODIC.items():
        y = load(rel)
        fmin, fmax = (30, 400) if kind == "bass" else (60, 1500)
        on = onsets(y)
        best = None
        pk = np.array([np.abs(y[o:o + 4096]).max() for o in on])
        for i in np.argsort(-pk)[:40]:
            o = on[i]
            seg = y[o:o + int(1.0 * SR)]
            if len(seg) < SR // 2:
                continue
            f0 = librosa.yin(seg, fmin=fmin, fmax=fmax, sr=SR, frame_length=4096, hop_length=512)
            cents = 1200 * np.log2(f0 / np.median(f0))
            score = float(np.mean(np.abs(cents) < 30)) * pk[i]
            if best is None or score > best[0]:
                best = (score, seg, int(round(librosa.hz_to_midi(np.median(f0)))))
        _, seg, root = best
        d = CC0 / setname
        for p in d.glob("*.wav"):
            p.unlink()
        name = desc.replace(" ", "_")
        MEL[desc] = (trim(seg, 1.0), root)
        sf.write(d / f"00_NIN_{name}_m{root}.wav", MEL[desc][0], SR, subtype="PCM_16")
        out.append(f"  {setname:6s} {desc:13s} root {root}")
    return out


MEL = {}                                         # desc -> (samples, root), for render()


def render(p, kit, bass):
    """a pattern twice over, as the FM-1 would play it (its kit, the bass sample pitched to each note): to audition"""
    spb = SR * 60 / p["bpm"] / 4
    steps, bars = p["steps"], 2
    out = np.zeros(int(spb * steps * bars) + SR)
    role_of = dict(kick="kick", snare="snare", chh="chh", ohh="ohh", perc="perc1")
    seg, root = bass
    for b in range(bars):
        for role, m in p["masks"].items():
            x = kit.get(role_of[role])
            if x is None:
                continue
            for s in range(steps):
                if m >> s & 1:
                    a = int((b * steps + s) * spb)
                    out[a:a + len(x)] += x
        for s, note in enumerate(p["bass"]):
            if note:
                ratio = 2 ** ((note - root) / 12)
                y = np.interp(np.arange(0, len(seg) - 1, ratio), np.arange(len(seg)), seg)[:int(spb * 2)]
                y[-min(len(y), 256):] *= np.linspace(1, 0, min(len(y), 256))
                a = int((b * steps + s) * spb)
                out[a:a + len(y)] += 0.7 * y
    return out / (np.abs(out).max() + 1e-9) * 0.9


def main():
    report = ["melodic:"] + melodic()
    KITS.mkdir(parents=True, exist_ok=True)
    pdir = REPORT.parent / "patterns"
    pdir.mkdir(parents=True, exist_ok=True)
    all_pats = []
    for si, song in enumerate(SONGS):
        print(f"== {song['name']}", flush=True)
        kit = kit_of(song)
        d = KITS / song["tag"]
        d.mkdir(exist_ok=True)
        for p in d.glob("*.wav"):
            p.unlink()
        entries = []
        for role, x in kit.items():
            sf.write(d / f"{role}.wav", x, SR, subtype="PCM_16")
            entries.append(dict(file=f"{role}.wav", rate=HAT_RATE if role in ("chh", "ohh") else KIT_RATE,
                                zones=LANES[role]))
        (d / "kit.json").write_text(json.dumps(dict(name=song["tag"], song=song["name"], sounds=entries), indent=1))
        secs = sum(len(x) for x in kit.values()) / SR
        pats = patterns_of(song)
        report.append(f"{song['name']}: kit {len(kit)} sounds, {secs:.2f} s"
                      + (f", grid offset {song['offset_ms']:.1f} ms" if "offset_ms" in song else ""))
        for p in pats:
            p.update(song=si, bpm=song["bpm"], label=f"{song['tag']} {short(p['name'])}")
            all_pats.append(p)
            sf.write(pdir / f"{p['label'].replace(' ', '_')}.wav",
                     render(p, kit, MEL["HLAH BASS" if si < 4 else "ECHO BASS"]), SR, subtype="PCM_16")
            report.append(f"  {p['label']:10s} bar {p['bar']:3d} x{p['rep']:<3d} " + "  ".join(
                "".join("x" if m >> i & 1 else "." for i in range(p["steps"])) for m in p["masks"].values())
                + "  bass " + " ".join(str(n) if n else "." for n in p["bass"]))

    # ---- the patterns' header
    L = ["/* SPDX-License-Identifier: GPL-3.0-only */",
         "/* Generated by tools/nin_kits.py from the Nine Inch Nails multitracks (SOURCES.md). Do not edit. */",
         "#pragma once", "#include <stdint.h>", "",
         f"#define NIN_NSONG {len(SONGS)}u", f"#define NIN_NPAT {len(all_pats)}u",
         "static const char *const NIN_SONG_NAME[NIN_NSONG] = {" + ", ".join(f'"{s["name"]}"' for s in SONGS) + "};",
         "static const char *const NIN_SONG_TAG[NIN_NSONG] = {" + ", ".join(f'"{s["tag"]}"' for s in SONGS) + "};",
         "/* a factory pattern: its song (the kit NIN<song>), tempo, length in 16ths (16, or 24 in 6/4), the drum lanes'",
         " * steps (bit s = step s; lanes as drums.c LANE_NOTE) and the bass line's MIDI notes (0 = rest) */",
         "typedef struct { char name[10]; uint8_t song, steps; uint16_t bpm10; uint8_t lane[5]; uint32_t mask[5]; uint8_t bass[24]; } nin_pat_t;",
         "static const nin_pat_t NIN_PAT[NIN_NPAT] = {"]
    for p in all_pats:
        lanes = [PAT_LANES[r] for r in p["masks"]] + [255] * (5 - len(p["masks"]))
        masks = list(p["masks"].values()) + [0] * (5 - len(p["masks"]))
        bass = p["bass"] + [0] * (24 - len(p["bass"]))
        L.append(f'    {{"{p["label"]}", {p["song"]}, {p["steps"]}, {int(round(p["bpm"] * 10))}u, {{{", ".join(map(str, lanes))}}}, '
                 f'{{{", ".join(f"0x{m:06X}u" for m in masks)}}}, {{{", ".join(map(str, bass))}}}}},')
    L += ["};", ""]
    OUT_H.write_text("\n".join(L))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(report) + "\n")
    print("\n".join(report))
    print(f"-> {OUT_H}, {KITS}")


if __name__ == "__main__":
    main()
