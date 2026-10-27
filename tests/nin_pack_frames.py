#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""NIN-VAVE: the requests tools/fm1_sample_upload.py sends to write a slot, as JSON ([cmd, args] each), for
web/test_nin_packs.mjs to check the browser's installer (web/nin_packs.js) against.
    python3 tests/nin_pack_frames.py SLOT slot.hdr slot.bin"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import fm1_sample_upload as up  # noqa: E402
import sampleio as sio  # noqa: E402

slot, hdr, data = int(sys.argv[1]), Path(sys.argv[2]).read_bytes(), Path(sys.argv[3]).read_bytes()
frames = [[11, [slot]]]
for off in range(0, len(data), 256):                 # (as fm1_sample_upload.main's load)
    a = sio.SLOT_DATA_OFF + off
    frames.append([12, [slot, a & 0x7F, (a >> 7) & 0x7F, (a >> 14) & 0x7F] + up.pack7(data[off:off + 256])])
frames.append([13, [slot] + up.pack7(hdr)])
print(json.dumps(frames))
