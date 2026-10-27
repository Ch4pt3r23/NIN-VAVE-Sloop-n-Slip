#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""NIN-VAVE's site (nin.chapter23.uk): install the firmware and the NIN packs on a connected FM-1 from the browser.

    python3 tools/make_nin_site.py FIRMWARE.fwsc VERSION OUT_DIR [PACK_DIR ...]

  index.html                  the NIN-VAVE page (web/nin_index.html): the firmware, the packs (web/nin_packs.js)
  webapp/installer/           SLOOP's installer (web/make_site.py) for this package, NIN-VAVE's name on it
  webapp/editor/              SLOOP's web editor
  firmware/nin-vave-VER.fwsc  the package
  packs/index.json            the firmware and every pack: its slots, their names, sizes, files
  packs/<PACK>/usrN.hdr .bin  a slot image (tools/nin_pack.py build: build/nin/packs/<PACK>)
  _headers                    Cloudflare Pages: no stale index, firmware or packs
PACK_DIR: a built pack (its pack.json, usr1..usr4/slot.hdr and slot.bin); default: every one in build/nin/packs.
"""
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
import make_site  # noqa: E402

LEAD = """<h1>Nine Inch Nails on the M-VAVE FM-1</h1>
  <p class="lead">NIN-VAVE is SLOOP, the live groovebox firmware, turned into a Nine Inch Nails instrument: drum kits
  cut from the songs' own multitracks, NIN sounds on the synth tracks, factory patterns from the records, and NIN packs
  for the four user sample slots. Everything SLOOP does is still there.</p>
  <p><a href="../../">&larr; NIN-VAVE: firmware and packs</a></p>
"""


def installer_text(html):
    """SLOOP's installer page with NIN-VAVE's name and words on it (the code is SLOOP's, unchanged). First SLOOP's
    own words, where its name means this firmware (not inside the logo); then NIN-VAVE's, which name SLOOP itself"""
    html = html.replace("SLOOP is based on Felucca by Leo Kuroshita", "@@BASED@@")
    html = html.replace("SLOOP is not affiliated with them.", "@@AFFIL@@")
    parts = re.split(r"(<svg.*?</svg>)", html, flags=re.S)
    html = "".join(p if p.startswith("<svg") else re.sub(r"\bSLOOP\b", "NIN-VAVE", p) for p in parts)
    a, b = html.index("<h1>"), html.index('<p data-t="intro">')
    html = html[:a] + LEAD + "  " + html[b:]
    html = html.replace(
        "@@BASED@@",
        'NIN-VAVE is <a href="https://github.com/isod89/sloop-fm1" target="_blank" rel="noopener">SLOOP</a> '
        "(isod89) with Nine Inch Nails inside; SLOOP is based on Felucca by Leo Kuroshita")
    html = re.sub(r"Samples: Versilian Studios.*?not CC0\)\.",
                  'Sounds: excerpts of Nine Inch Nails multitracks, which stay theirs: '
                  '<a href="https://github.com/Ch4pt3r23/NIN-VAVE-Sloop-n-Slip/blob/main/SOURCES.md" target="_blank" '
                  'rel="noopener">where each comes from</a>.', html, flags=re.S)
    html = html.replace("@@AFFIL@@", "NIN-VAVE is not affiliated with them, nor with Nine Inch Nails or SLOOP.")
    return html.replace("</head>", "<style>button#go:not(:disabled) { background: #e02020; color: #fff; }\n"
                        "progress::-webkit-progress-value { background: #e02020; }\n"
                        '@font-face { font-family: "Special Elite"; font-display: swap; '
                        "src: url(../../fonts/special-elite-latin.woff2) format('woff2'); }\n"
                        'h1, button#go, .lead { font-family: "Special Elite", "Courier New", monospace; }</style>\n</head>',
                        1)


def main(fw, version, out, pack_dirs):
    fw, out = Path(fw), Path(out)
    make_site.main(fw, version, out)
    inst = out / "webapp/installer/index.html"
    inst.write_text(installer_text(inst.read_text(encoding="utf-8")), encoding="utf-8")
    man = out / "webapp/sloop.webmanifest"
    if man.exists():
        m = json.loads(man.read_text())
        m.update(name="NIN-VAVE", short_name="NIN-VAVE")
        man.write_text(json.dumps(m, indent=1) + "\n")
    raw = fw.read_bytes()
    name = f"nin-vave-{re.sub(r'[^A-Za-z0-9.-]', '-', version)}.fwsc"
    index = dict(firmware=dict(version=version, product=make_site.product_of(raw), file="firmware/" + name,
                               bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                               built=time.strftime("%Y-%m-%d", time.gmtime(fw.stat().st_mtime))),
                 packs=[])
    shutil.rmtree(out / "packs", ignore_errors=True)
    for d in pack_dirs:
        d = Path(d)
        p = json.loads((d / "pack.json").read_text())
        pd = out / "packs" / p["pack"]
        pd.mkdir(parents=True, exist_ok=True)
        slots = []
        for s in p["slots"]:
            src = d / f"usr{s['slot']}"
            if not s.get("ok", True) or not (src / "slot.hdr").exists():
                raise SystemExit(f"{d}: USR{s['slot']} not built (tools/nin_pack.py build {p['pack']})")
            for ext in ("hdr", "bin"):
                shutil.copy(src / f"slot.{ext}", pd / f"usr{s['slot']}.{ext}")
            slots.append(dict(slot=s["slot"], name=s["name"], kind=s["kind"], zones=s["zones"], seconds=s["seconds"],
                              hdr=f"packs/{p['pack']}/usr{s['slot']}.hdr", bin=f"packs/{p['pack']}/usr{s['slot']}.bin",
                              bytes=(src / "slot.bin").stat().st_size))
        index["packs"].append(dict(id=p["pack"], title=p["title"], about=p.get("about", ""), slots=slots))
        print(f"site: pack {p['pack']} ({p['title']}): " + ", ".join(f"USR{s['slot']} {s['name']}" for s in slots))
    (out / "packs/index.json").write_text(json.dumps(index, indent=1) + "\n")
    shutil.copy(ROOT / "web/nin_index.html", out / "index.html")
    shutil.copy(ROOT / "web/nin_packs.js", out / "nin_packs.js")
    shutil.copy(ROOT / "assets/logo/nin-vave-logo.svg", out / "nin-vave-logo.svg")
    shutil.copytree(ROOT / "web/fonts", out / "fonts", dirs_exist_ok=True)   # Special Elite and its licence
    (out / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n"
                                  "/\n  Cache-Control: no-cache\n/index.html\n  Cache-Control: no-cache\n"
                                  "/packs/*\n  Cache-Control: no-cache\n/firmware/*\n  Cache-Control: no-cache\n"
                                  "/webapp/*\n  Cache-Control: no-cache\n")
    print(f"site: {out}: index.html, {len(index['packs'])} pack(s), firmware {version} ({index['firmware']['product']})")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    dirs = sys.argv[4:] or sorted(str(p.parent) for p in (ROOT / "build/nin/packs").glob("*/pack.json"))
    main(sys.argv[1], sys.argv[2], sys.argv[3], dirs)
