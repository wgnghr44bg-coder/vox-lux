// Shared part of every force: the counter from the scenario, its 0..1 level, and "when does
// this force first reach strength s" (used to schedule what breaks, falls or floats).
import { monotone, clamp } from '../util.js';

export function baseForce(E, TL, kind, mk) {
  const STOP = TL.beats.stop;
  const counter = monotone(TL.counter);
  const vals = TL.counter.map(c => c[1]);
  const [r0, r1] = TL.range || [vals[0], vals.reduce((m, v) => Math.abs(v - vals[0]) > Math.abs(m - vals[0]) ? v : m, vals[0])];
  const level = t => clamp((counter(Math.min(t, STOP)) - r0) / ((r1 - r0) || 1));
  const phys = mk ? mk({ level, counter }) : level;
  // table of the physical quantity, to answer timeOf(s) quickly
  const DT = 1 / 60; let tab = null;     // built on first use (after the place has set E.waterBase etc.)
  const F = {
    kind, level, counter, STOP,
    phys,
    timeOf(s) { if (!tab) { tab = []; for (let t = 0; t <= STOP + DT; t += DT) tab.push(phys(t)); } for (let i = 0; i < tab.length; i++) if (tab[i] >= s) return i * DT; return 1e9; },
    lateral: () => ({ a: 0, dx: 0, dz: 1 }),
    droop: () => 0,
    field: () => ({ g: 9.8, air: [0, 0, 0], waterY: E.waterBase ?? -1e9 }),
    fallMode: 'pancake',
    wobble: null,
    rumble: () => 0,
    dark: () => 0,
    freeze: () => 0,
  };
  return F;
}
