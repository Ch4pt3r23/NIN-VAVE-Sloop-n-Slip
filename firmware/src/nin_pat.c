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

/* NIN-VAVE boots as itself. Its first power-on (no NIN sound among the favourites: coming from SLOOP, or a fresh
 * FM-1): the NIN sounds become the first favourites (PRESETS lists them first; the user's own after them, 16 in
 * all), and HLAH A plays on the HLAH kit with LETU STAB and DISC PIANO on tracks 2 and 3, empty, to play over.
 * The favourites are saved with the settings at once, so later power-ons resume the autosave as SLOOP does */
static const char *const NIN_FAVS[] = {"HLAH BASS", "ECHO BASS", "DISC PIANO", "LETU STAB", "DEMN STRGS",
                                       "CORO DRONE", "DISC MRMBA", "HLAH KIT"};
#define NIN_NFAV (sizeof NIN_FAVS / sizeof NIN_FAVS[0])

UI_SMALL static uint32_t nin_bank(const char *name)   /* the BANK index of a factory sound, NBANK = none */
{
    uint32_t i;
    for (i = 0; i < NBANK; i++)
        if (str_eq(BANK[i].name, name))
            return i;
    return NBANK;
}

UI_SMALL static void nin_boot(void)
{
    uint16_t keep[FAV_N];
    uint32_t i, k, n = 0;
    if (!bank_ready)
        bank_resolve();
    for (i = 0; i < NIN_NFAV; i++)
        if (fav_has(nin_bank(NIN_FAVS[i])))
            return;                                  /* been here before */
    memcpy(keep, fav, sizeof keep);
    for (i = 0; i < NIN_NFAV; i++)
        if ((k = nin_bank(NIN_FAVS[i])) < NBANK)
            fav[n++] = (uint16_t)k;
    for (i = 0; i < FAV_N && n < FAV_N; i++)         /* the user's favourites after them */
        if (keep[i] != FAV_NONE)
            fav[n++] = keep[i];
    while (n < FAV_N)
        fav[n++] = FAV_NONE;
    fav_dirty = 1;
    nin_pattern_load(0);                             /* HLAH A: the kit, the drums, the bass on track 1 */
    for (i = 1; i < NPART; i++) {                    /* tracks 2, 3: a NIN sound, nothing programmed */
        preset_go_to(&trk[i], nin_bank(i == 1u ? "LETU STAB" : "DISC PIANO"));
        track_defaults_steps(&trk[i]);
    }
    for (i = 0; i < NPART; i++)
        trk[i].engine = trk[i].eng_req;              /* (power-on: nothing sounds, no fade) */
    song.sel = TRK_DRUM;
    settings_save();                                 /* the favourites now (once): a power-off may come next */
}
