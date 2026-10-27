// SPDX-License-Identifier: GPL-3.0-only
// NIN-VAVE: the browser's pack installer (nin_packs.js) sends what tools/fm1_sample_upload.py sends, frame for frame,
// for every slot of every built pack; and a slot written through a mock FM-1 lands byte for byte.
//   node web/test_nin_packs.mjs SITE_DIR      (after tools/make_nin_site.py)
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { slotFrames, Link, CMD, DATA_OFF } from "./nin_packs.js";

const site = process.argv[2];
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const index = JSON.parse(readFileSync(join(site, "packs/index.json"), "utf8"));
let fails = 0, slots = 0;
const check = (ok, what) => { console.log(`nin-packs: ${what.padEnd(70)} ${ok ? "ok" : "FAIL"}`); fails += !ok; };

for (const p of index.packs) {
  for (const s of p.slots) {
    const hdrPath = join(site, s.hdr), binPath = join(site, s.bin);
    const hdr = new Uint8Array(readFileSync(hdrPath)), data = new Uint8Array(readFileSync(binPath));
    const want = execFileSync("python3", [join(root, "tests/nin_pack_frames.py"), String(s.slot - 1), hdrPath, binPath],
      { maxBuffer: 1 << 26 }).toString();
    const got = JSON.stringify(slotFrames(s.slot - 1, hdr, data));
    check(got === JSON.stringify(JSON.parse(want)), `${p.id} USR${s.slot} ${s.name}: ${data.length} B, frames as fm1_sample_upload.py`);
    slots++;
  }
}

// a mock FM-1 (as the editor's: SMP_BEGIN / WRITE / END, replies with the same command): the slot it ends up with
{
  const p = index.packs[0], s = p.slots[0];
  const hdr = new Uint8Array(readFileSync(join(site, s.hdr))), data = new Uint8Array(readFileSync(join(site, s.bin)));
  const flash = new Uint8Array(0x14000).fill(0xFF);
  const unpack7 = (a) => { const o = []; for (let i = 0; i < a.length; i += 8) { const t = a[i]; for (let j = 1; j < 8 && i + j < a.length; j++) o.push(a[i + j] | (((t >> (j - 1)) & 1) << 7)); } return o; };
  const input = { onmidimessage: null };
  const output = {
    send(m) {
      const cmd = m[4], a = m.slice(5, m.length - 1);
      let reply;
      if (cmd === CMD.HELLO) reply = [1];
      else if (cmd === CMD.SMP_BEGIN) reply = [a[0], 0];
      else if (cmd === CMD.SMP_WRITE) {
        const at = a[1] | (a[2] << 7) | (a[3] << 14);
        flash.set(unpack7(a.slice(4)), at);
        reply = [a[0], a[1], a[2], a[3], 0];
      } else if (cmd === CMD.SMP_END) { flash.set(unpack7(a.slice(1)), 0); reply = [a[0], 0]; }
      setTimeout(() => input.onmidimessage({ data: Uint8Array.from([0xF0, 0x7D, 0x46, 0x4C, cmd, ...reply, 0xF7]) }), 0);
    },
  };
  const link = new Link(input, output);
  let last = 0;
  await link.writeSlot(0, hdr, data, (d, t) => { last = d / t; });
  const same = flash.subarray(0, hdr.length).every((v, i) => v === hdr[i]) &&
    flash.subarray(DATA_OFF, DATA_OFF + data.length).every((v, i) => v === data[i]);
  check(same && last === 1, `mock FM-1: ${p.id} USR1 written byte for byte, progress to 100 %`);
}

console.log(fails ? `nin-packs: ${fails} FAILED` : `nin-packs: ${slots} slots: PASS`);
process.exit(fails ? 1 : 0);
