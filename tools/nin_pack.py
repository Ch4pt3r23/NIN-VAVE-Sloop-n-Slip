#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""NIN-VAVE packs: Nine Inch Nails sounds for the FM-1's four user sample slots (USR1..USR4), a pack at a time.

    python3 tools/nin_pack.py list
    python3 tools/nin_pack.py build [PACK ...]    -> build/nin/packs/<PACK>/: each slot's WAVs (to audition), and the
                                                    slot images fm1_sample_upload.py makes from them (sizes checked)
    python3 tools/nin_pack.py load PACK           -> the four slots into the FM-1 over USB (fm1_sample_upload.py)

A slot is a drum KIT (16 sounds on the 16 pads: KIT USR1..USR4 on the drum track) or an instrument (up to four notes
of one NIN part, keys split between them: SAMPLE, SET USR1..USR4). 80 KiB each: about 7.4 s at 22050 Hz.
The stems: ~/.cache/ninvave/stems (tools/nin_kits.py). Sources and credits: SOURCES.md.
"""
import json
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nin_kits as nk  # noqa: E402

nk.STEMS = Path.home() / ".cache/ninvave/stems"      # (nin_kits takes its own argv[1] as the stems: not ours)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build/nin/packs"
RATE = 22050                                     # the slots' rate
LANE_NOTE = [36, 35, 38, 39, 42, 46, 44, 37, 40, 43, 48, 49, 51, 70, 63, 56]   # drums.c (KIT USR: zone = the lane's note)
# the 16 pads: (lane's role, the test its hit must pass, seconds, dB)
PADS = [("kick", "kick", 0.50, 0), ("kick2", "kick", 0.50, -1), ("snare", "snare", 0.60, 0), ("clap", "snare", 0.50, -1),
        ("chh", "chh", 0.12, -7), ("ohh", "ohh", 0.60, -8), ("pedal", "chh", 0.12, -9), ("rim", "perc", 0.30, -4),
        ("snare2", "snare", 0.50, -2), ("tomlo", "tom", 0.60, -2), ("tomhi", "tom", 0.50, -2), ("crash", "crash", 1.60, -8),
        ("ride", "ohh", 1.00, -9), ("shaker", "chh", 0.20, -9), ("conga", "perc", 0.40, -4), ("bell", "perc", 0.70, -5)]
# (a slot holds ~7.4 s; each sound is cut where it has died away, so these are ceilings: the tails ring as recorded)
TESTS = dict(nk.ROLE_TEST)
TESTS.update(tom=lambda F: 0.15 < F["share"]["low"] < 0.75 and F["cen"] < 1200 and F["decay"] > 0.12,
             crash=lambda F: F["share"]["high"] > 0.25 and F["decay"] > 0.35, perc=lambda F: True)
ND, SLIP, HLAH = nk.ND, nk.SLIP, nk.HLAH
PACKS = {
    "TDS": dict(title="The Downward Spiral", slots=[
        dict(name="NIN.CLSR", kit=dict(drums=[ND + "Multitrack.Closer/Audio files/drums_1.wav",
                                              ND + "Multitrack.Closer/Audio files/drums_2.wav",
                                              ND + "Multitrack.Closer/Audio files/drums_3.wav"],
                                       perc=[ND + "Multitrack.Closer/Audio files/song.wav"])),
        dict(name="NIN.MOTP", kit=dict(drums=[ND + "Multitrack.MOTP/Audio Files/march of the pigs - drums.flac.WAV"],
                                       perc=[ND + "Multitrack.MOTP/Audio Files/march of the pigs - bg sounds.flac.WAV"])),
        dict(name="CLSR BS", inst=dict(stem=ND + "Multitrack.Closer/Audio files/rhythm.wav", kind="bass")),
        dict(name="MOTP SYN", inst=dict(stem=ND + "Multitrack.MOTP/Audio Files/march of the pigs - bass synth.flac.WAV",
                                        kind="bass")),
    ]),
}


def hits(rels, test, n):
    """up to n different hits that pass test: well apart from their neighbours, loud, of different brightness"""
    cands = []
    for rel in rels:
        y = nk.load(rel)
        on = nk.onsets(y)
        for i, o in enumerate(on[:5000]):
            gap = (on[i + 1] if i + 1 < len(on) else len(y)) - o
            if gap < 0.08 * nk.SR:
                continue
            F = nk.features(y, o)
            if F and F["peak"] > 0.03 and TESTS[test](F):
                cands.append((F["peak"], F["cen"], rel, o, gap))
    cands.sort(key=lambda c: -c[0])
    out, cens = [], []
    for q in (0.15, 0.35, 0.55, 0.05, 0.75, 0.25, 0.45):    # loud ones first, not only the loudest
        if len(out) >= n or not cands:
            break
        p, cen, rel, o, gap = cands[min(len(cands) - 1, int(len(cands) * q))]
        if all(abs(cen - c) > 250 for c in cens):
            out.append(nk.load(rel)[o:o + gap])
            cens.append(cen)
    return out


def kit_slot(spec):
    """16 pads: [(samples at RATE, root, lo, hi)], each pad on its lane's note"""
    used, zones, pool = {}, [], {}
    for role, test, secs, db in PADS:
        key = (test, tuple(spec["perc"] if test == "perc" else spec["drums"]))
        if key not in pool:
            pool[key] = hits(list(key[1]), test, 4)
        k = used.get(key, 0)
        cand = pool[key][k % len(pool[key])] if pool[key] else None
        used[key] = k + 1
        if cand is None:                              # nothing of that kind: the kick or the snare, pitched
            cand = pool.get(("kick", tuple(spec["drums"])), [np.zeros(1000)])[0]
        x = librosa.resample(nk.trim(cand, secs, db).astype(np.float32), orig_sr=nk.SR, target_sr=RATE)
        note = LANE_NOTE[[r for r, *_ in PADS].index(role)]
        zones.append((x, note, note, note, role))
    return zones


def inst_slot(spec):
    """up to four steady notes of one part, the keyboard split between them"""
    y = nk.load(spec["stem"])
    fmin, fmax = (30, 400) if spec["kind"] == "bass" else (60, 1500)
    on = nk.onsets(y)
    pk = np.array([np.abs(y[o:o + 4096]).max() for o in on])
    best = {}
    for i in np.argsort(-pk)[:300]:
        seg = y[on[i]:on[i] + int(1.6 * nk.SR)]
        if len(seg) < int(0.3 * nk.SR):
            continue
        f0 = librosa.yin(seg[:int(0.6 * nk.SR)], fmin=fmin, fmax=fmax, sr=nk.SR, frame_length=4096, hop_length=512)
        steady = float(np.mean(np.abs(1200 * np.log2(f0 / np.median(f0))) < 35))
        if steady < 0.5:
            continue                                  # (a slide, a chord, noise: not a note to play in tune)
        note = int(round(librosa.hz_to_midi(np.median(f0))))
        if steady * pk[i] > best.get(note, (0,))[0]:
            best[note] = (steady * pk[i], seg)
    notes = sorted(n for n in best if best[n][0] > 0.12 * max(v[0] for v in best.values()))
    pick = [notes[round(i * (len(notes) - 1) / 3)] for i in range(4)] if len(notes) >= 4 else notes
    zones = []
    for n in dict.fromkeys(pick):
        x = librosa.resample(nk.trim(best[n][1], 1.6).astype(np.float32), orig_sr=nk.SR, target_sr=RATE)
        zones.append((x, n, None, None, f"m{n}"))
    return zones


def build(name):
    pack = PACKS[name]
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    manifest = dict(pack=name, title=pack["title"], slots=[])
    for si, slot in enumerate(pack["slots"]):
        zones = kit_slot(slot["kit"]) if "kit" in slot else inst_slot(slot["inst"])
        sd = d / f"usr{si + 1}"
        sd.mkdir(exist_ok=True)
        for p in sd.glob("*.wav"):
            p.unlink()
        args = []
        for k, (x, root, lo, hi, label) in enumerate(zones):
            f = sd / f"{k:02d}_{label}.wav"
            sf.write(f, x, RATE, subtype="PCM_16")
            args.append(f"{f}:{root}" + (f":{lo}-{hi}" if lo is not None else ""))
        secs = sum(len(z[0]) for z in zones) / RATE
        r = subprocess.run([sys.executable, str(ROOT / "tools/fm1_sample_upload.py"), "build", slot["name"],
                            str(sd / "slot"), *args], capture_output=True, text=True)
        ok = r.returncode == 0
        manifest["slots"].append(dict(slot=si + 1, name=slot["name"], kind="kit" if "kit" in slot else "inst",
                                      zones=len(zones), seconds=round(secs, 2), files=args, ok=ok))
        print(f"{name} USR{si + 1} {slot['name']:9s} {'KIT ' if 'kit' in slot else 'INST'} {len(zones):2d} zones "
              f"{secs:4.1f} s  {'ok' if ok else 'TOO BIG: ' + r.stderr.strip()[-120:]}", flush=True)
    (d / "pack.json").write_text(json.dumps(manifest, indent=1))


def load(name):
    m = json.loads((OUT / name / "pack.json").read_text())
    for s in m["slots"]:
        if not s["ok"]:
            raise SystemExit(f"USR{s['slot']} {s['name']}: not built (too big)")
        print(f"USR{s['slot']} <- {s['name']}", flush=True)
        subprocess.run([sys.executable, str(ROOT / "tools/fm1_sample_upload.py"), "load", str(s["slot"]), s["name"],
                        *s["files"]], check=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["list"]:
        for k, v in PACKS.items():
            print(f"{k:8s} {v['title']}: " + ", ".join(s["name"] for s in v["slots"]))
    elif a[:1] == ["build"]:
        for k in a[1:] or list(PACKS):
            build(k)
    elif a[:1] == ["load"] and len(a) == 2:
        load(a[1])
    else:
        sys.exit(__doc__)
