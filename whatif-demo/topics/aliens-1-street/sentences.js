// Documentary pace (owner, 10 okt 2026): every sentence its own line with a pause after it; a step marker
// (HOUR 1., DAY 1., WEEK 1.) gets a long pause. split(lines) keeps the original ids for the first sentence and
// adds id_2, id_3 ...; group(at, lines) gives an original id the span of all its sentences.
export function split(lines) {
  const out = [];
  for (const [id, text, pause] of lines) {
    const parts = text.match(/[^.?!]+(?:[.?!]+|$)(?:\s+|$)/g).map(s => s.trim()).filter(Boolean);
    parts.forEach((s, i) => {
      const last = i === parts.length - 1, marker = /^(HOUR|DAY|WEEK) \d+\.$/.test(s);
      out.push([i ? `${id}_${i + 1}` : id, s, marker ? 'long' : last ? pause : 'pause']);
    });
  }
  return out;
}
export function group(at, lines) {
  const n = {}; for (const [id] of lines) { const m = id.match(/^(.*)_(\d+)$/); if (m) n[m[1]] = Math.max(n[m[1]] || 1, +m[2]); }
  return id => { const a = at(id); return n[id] ? { s: a.s, e: at(`${id}_${n[id]}`).e } : a; };
}
