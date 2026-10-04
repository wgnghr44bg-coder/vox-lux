// Scenario + measured voice timing -> TL (all times in VIDEO seconds).
// timing.json comes from make_whatif.py: { VO_OFFSET, lines: { id: [start, end] } } in voice seconds.
// Without it (first preview) the times are estimated from the word count.
export const PAUSE = { none: 0, '': .3, pause: .5, long: 1.0 };

export function estimateTiming(lines, wps = 2.55) {
  let t = 0; const out = {};
  for (const [id, text, pause] of lines) {
    const words = text.replace(/\[[^\]]+\]/g, ' ').split(/\s+/).filter(Boolean).length;
    const inner = (text.match(/[.!?](\s|$)/g) || []).length - 1;
    const d = words / wps + Math.max(0, inner) * .3 + (text.match(/,/g) || []).length * .35;
    out[id] = [t, t + d];
    t += d + (typeof pause === 'number' ? pause : PAUSE[pause ?? ''] ?? .3);
  }
  return { VO_OFFSET: .8, lines: out, estimated: true };
}

export function buildTL(scen, timing, o = {}) {
  const lines = scen.lines;
  timing = timing || estimateTiming(lines);
  const off = timing.VO_OFFSET ?? .8;
  const at = id => {
    const r = timing.lines[id];
    if (!r) throw new Error('unknown line id ' + id);
    return { s: r[0] + off, e: r[1] + off };
  };
  const cfg = scen.default(at, o);
  const topic = scen.topic || {};
  const TL = {
    VO_OFFSET: off, titleIn: .3, titleOut: 6.4, dim: .6, events: [],
    place: o.place || topic.place, force: o.force || topic.force,
    title: topic.title, ...cfg,
  };
  // clean ending (default): no end card, no text; the picture fades out under the last lines
  TL.beats.fade = TL.beats.fade ?? (TL.endStyle === 'card' ? TL.T_END - 1.6 : (TL.beats.end ?? TL.T_END - 4) - .3);
  TL.beats.end = TL.beats.end ?? 1e9;          // no end card unless the scenario asks for one
  TL.beats.end = TL.beats.end ?? 1e9;          // no end card unless the scenario asks for one
  TL.estimated = !!timing.estimated;
  return TL;
}
