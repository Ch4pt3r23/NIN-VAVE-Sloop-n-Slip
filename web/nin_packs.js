// SPDX-License-Identifier: GPL-3.0-only
// NIN-VAVE: install a NIN pack (the FM-1's user sample slots USR1..USR4) from the browser over Web MIDI, frame for
// frame as tools/fm1_sample_upload.py does (web/EDITOR_PROTOCOL.md: SMP_BEGIN 11, SMP_WRITE 12, SMP_END 13). A slot
// image is the pair tools/nin_pack.py builds: its header (512 B) and its IMA ADPCM data. Checked against the Python
// uploader by web/test_nin_packs.mjs.

export const HDR = [0x7D, 0x46, 0x4C];
export const CMD = { HELLO: 1, SMP_BEGIN: 11, SMP_WRITE: 12, SMP_END: 13, SMP_INFO: 15 };
export const DATA_OFF = 512;                     // the slot's data starts after its 512-byte header
export const CHUNK = 256;                        // data bytes per SMP_WRITE
// the FM-1 running NIN-VAVE (its USB port is named after Felucca); never the update loader's port ("ota"), never
// other gear
export const PORT = /felucca|sloop|nin-vave/i;

/** groups of up to 7 bytes, each preceded by one byte holding their top bits */
export function pack7(b) {
  const out = [];
  for (let i = 0; i < b.length; i += 7) {
    const g = b.slice(i, i + 7);
    let top = 0;
    g.forEach((x, j) => { top |= ((x >> 7) & 1) << j; });
    out.push(top, ...Array.from(g, (x) => x & 0x7F));
  }
  return out;
}

/** the requests that write slot (0..3): [cmd, args] in order */
export function slotFrames(slot, hdr, data) {
  const f = [[CMD.SMP_BEGIN, [slot]]];
  for (let off = 0; off < data.length; off += CHUNK) {
    const a = DATA_OFF + off;
    f.push([CMD.SMP_WRITE, [slot, a & 0x7F, (a >> 7) & 0x7F, (a >> 14) & 0x7F, ...pack7(data.subarray(off, off + CHUNK))]]);
  }
  f.push([CMD.SMP_END, [slot, ...pack7(hdr)]]);
  return f;
}

const RC = { 1: "size", 2: "header", 3: "data CRC", 4: "flash", 5: "zones" };

export class Link {
  constructor(input, output) {
    this.input = input;
    this.output = output;
    this.wait = null;
    input.onmidimessage = (e) => {
      const d = e.data;
      if (!this.wait || d[0] !== 0xF0 || d[1] !== HDR[0] || d[2] !== HDR[1] || d[3] !== HDR[2] || d[4] !== this.wait.cmd) return;
      const w = this.wait;
      this.wait = null;
      clearTimeout(w.timer);
      w.resolve(Array.from(d.slice(5, d[d.length - 1] === 0xF7 ? d.length - 1 : d.length)));
    };
  }

  /** the FM-1's ports, or null: Web MIDI with SysEx (Chrome, Edge, Opera on a computer or Android) */
  static async open() {
    if (!navigator.requestMIDIAccess) throw new Error("This browser has no Web MIDI: use Chrome or Edge.");
    const access = await navigator.requestMIDIAccess({ sysex: true });
    const pick = (ports) => [...ports.values()].find((p) => PORT.test(p.name || "") && !/ota/i.test(p.name || ""));
    const input = pick(access.inputs), output = pick(access.outputs);
    if (!input || !output) return null;
    const link = new Link(input, output);
    for (let i = 0; i < 3; i++) {                // the first frame after opening the port can be lost
      try { await link.req(CMD.HELLO, [], 1000); break; } catch (e) { if (i === 2) throw e; }
    }
    return link;
  }

  req(cmd, args, timeout = 3000) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.wait = null; reject(new Error(`no reply to command ${cmd}`)); }, timeout);
      this.wait = { cmd, resolve, timer };
      this.output.send([0xF0, ...HDR, cmd, ...args, 0xF7]);
    });
  }

  /** the slots: [{nz, name, kib}] (SMP_INFO) */
  async slots() {
    const r = await this.req(CMD.SMP_INFO, []);
    const out = [];
    let i = 2;
    for (let k = 0; k < r[0]; k++) {
      const nz = r[i], j = r.indexOf(0, i + 1);
      out.push({ nz, name: String.fromCharCode(...r.slice(i + 1, j)), kib: r[j + 1] });
      i = j + 2;
    }
    return out;
  }

  /** write one slot: progress(done, total) per frame */
  async writeSlot(slot, hdr, data, progress = () => {}) {
    const frames = slotFrames(slot, hdr, data);
    for (let n = 0; n < frames.length; n++) {
      const [cmd, args] = frames[n];
      const r = await this.req(cmd, args, cmd === CMD.SMP_END ? 5000 : 3000);
      const rc = cmd === CMD.SMP_WRITE ? r[4] : r[1];
      if (rc) {
        const what = cmd === CMD.SMP_BEGIN ? "start" : cmd === CMD.SMP_END ? "finish" : "write";
        throw new Error(`USR${slot + 1}: the FM-1 refused to ${what} (${rc}${RC[rc] ? ", " + RC[rc] : ""})`);
      }
      progress(n + 1, frames.length);
    }
  }
}
