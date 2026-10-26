/* SPDX-License-Identifier: GPL-3.0-only */
/* NIN-VAVE: the factory patterns, cut from the Nine Inch Nails multitracks by tools/nin_kits.py (nin_patterns.h).
 * Loading one (menu SEQ > NIN PATTERN, OCT+) sets the drum track to the song's kit and writes its steps, puts the
 * song's bass line on part 1 with a NIN bass sound, and sets the length (16 steps, or 24 in 6/4) and the tempo.
 * Parts 2 and 3 are left as they are: play over it. The drum lanes are drums.c's LANE_NOTE order. */
#include "nin_patterns.h"

static uint8_t nin_pick;                        /* the menu's choice, NIN_PAT index */

UI_SMALL static void nin_pattern_load(uint32_t i)
{
    const nin_pat_t *p = &NIN_PAT[i % NIN_NPAT];
    track_t *d = TDRUM, *b = &trk[0];
    const char *bass = p->song < 4u ? "HLAH BASS" : "ECHO BASS";   /* (Pretty Hate Machine, The Slip) */
    uint32_t s, l, n = p->steps < NSTEP ? p->steps : NSTEP;
    d->p[P_E0] = (int16_t)(p->song ? DRUM_NIN + p->song - 1u : 0u);  /* HLAH: the GM kit (PERC) */
    memset(d->dstep, 0, sizeof d->dstep);
    memset(d->micro, 0, sizeof d->micro);
    memset(d->fill, 0, sizeof d->fill);
    for (l = 0; l < NLOCK; l++)
        d->lock[l].step = LOCK_FREE;
    for (l = 0; l < 5u; l++)
        if (p->lane[l] < DRUM_LANES)
            for (s = 0; s < n; s++)
                if (p->mask[l] >> s & 1u)
                    d->dstep[s].on[p->lane[l] >> 3] |= (uint8_t)(1u << (p->lane[l] & 7u));
    d->p[P_SLEN] = (int16_t)n;
    d->seq_active = 1;
    for (l = 0; l < NBANK; l++)                     /* part 1: the bass sound, then its line */
        if (str_eq(BANK[l].name, bass)) {
            preset_go_to(b, l);
            break;
        }
    memset(b->step, 0, sizeof b->step);
    memset(b->micro, 0, sizeof b->micro);
    memset(b->fill, 0, sizeof b->fill);
    for (l = 0; l < NLOCK; l++)
        b->lock[l].step = LOCK_FREE;
    for (s = 0; s < n && s < 24u; s++)
        if (p->bass[s]) {
            b->step[s].note[0] = p->bass[s];
            b->step[s].n = 1;
            b->step[s].time = ST_NOTE;
            b->step[s].vel = 100;
        }
    b->p[P_SLEN] = (int16_t)n;
    b->seq_active = 1;
    song.g[G_BPM] = (int16_t)clamp(((int32_t)p->bpm10 + 5) / 10, 40, 240);
    ui.force = 1;
}
