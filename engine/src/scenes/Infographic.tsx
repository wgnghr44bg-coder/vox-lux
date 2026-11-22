import React from "react";
import { useCurrentFrame } from "remotion";
import { kleur, font, zacht, inUit } from "../theme";

// SCÈNE C — LEVENDE INFOGRAPHIC: data die zichzelf opbouwt. Drie vormen: koerslijn (met top en laagste), dagstaven, tijdlijn.
const MAAND = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export const KoersLijn: React.FC<{ data: [string, number][]; start: number; duur: number; x: number; y: number; w: number; h: number; titel: string }> = ({ data, start, duur, x, y, w, h, titel }) => {
  const f = useCurrentFrame() - start;
  if (f < 0) return null;
  const v = data.map((d) => d[1]); const lo = Math.min(...v), hi = Math.max(...v); const m = (hi - lo) * 0.12;
  const X = (i: number) => x + (i / (data.length - 1)) * w;
  const Y = (b: number) => y + ((hi + m - b) / (hi - lo + 2 * m)) * h;
  const p = inUit(f / duur); const n = Math.max(2, Math.floor(data.length * p));
  const pts = data.slice(0, n).map((d, i) => `${X(i)},${Y(d[1])}`).join(" ");
  const iTop = v.indexOf(hi); const iLaag = v.indexOf(lo);
  const dag = (s: string) => { const d = new Date(s + "T12:00"); return `${MAAND[d.getMonth()]} ${d.getDate()}`; };
  const a = zacht(f / 12);
  return (
    <svg width={1920} height={1080} style={{ position: "absolute" }} opacity={a}>
      <defs>
        <linearGradient id="vlak" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={kleur.rood} stopOpacity={0.35} /><stop offset="1" stopColor={kleur.rood} stopOpacity={0} /></linearGradient>
        <filter id="lg"><feGaussianBlur stdDeviation="5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
      </defs>
      <text x={x} y={y - 40} style={{ font: `600 28px ${font.kop}`, fill: kleur.zacht }}>{titel}</text>
      {[0, 0.25, 0.5, 0.75, 1].map((q, i) => { const b = lo + (hi - lo) * q; return (
        <g key={i}><line x1={x} x2={x + w} y1={Y(b)} y2={Y(b)} stroke={kleur.rand} strokeDasharray="6 10" />
          <text x={x + w + 16} y={Y(b) + 8} style={{ font: `400 22px ${font.cijfer}`, fill: kleur.zacht }}>${Math.round(b)}</text></g>); })}
      <polygon points={`${X(0)},${y + h} ${pts} ${X(n - 1)},${y + h}`} fill="url(#vlak)" />
      <polyline points={pts} fill="none" stroke={kleur.rood} strokeWidth={5} strokeLinejoin="round" filter="url(#lg)" />
      {n > iTop && <Pil x={X(iTop)} y={Y(hi)} tekst={`Top $${hi.toFixed(0)} · ${dag(data[iTop][0])}`} k={kleur.tekst} boven />}
      {n - 1 >= iLaag && <Pil x={X(iLaag)} y={Y(lo)} tekst={`Now $${lo.toFixed(0)} · ${dag(data[iLaag][0])}`} k={kleur.rood} />}
    </svg>
  );
};

const Pil: React.FC<{ x: number; y: number; tekst: string; k: string; boven?: boolean }> = ({ x, y, tekst, k, boven }) => {
  const b = tekst.length * 15 + 36; const links = x > 1100;
  const px = links ? x - b - 24 : x + 24; const py = boven ? y - 64 : y + 22;
  return (
    <g>
      <circle cx={x} cy={y} r={11} fill={kleur.achter1} stroke={k} strokeWidth={5} />
      <rect x={px} y={py} width={b} height={46} rx={23} fill={k === kleur.rood ? kleur.rood : "#1c2a46"} stroke={kleur.rand} />
      <text x={px + b / 2} y={py + 31} textAnchor="middle" style={{ font: `700 24px ${font.kop}`, fill: "#fff" }}>{tekst}</text>
    </g>
  );
};

export const DagStaven: React.FC<{ data: [string, number][]; n: number; start: number; per: number; x: number; y: number; w: number; h: number }> = ({ data, n, start, per, x, y, w, h }) => {
  const f = useCurrentFrame() - start;
  if (f < 0) return null;
  const d = data.slice(-n - 1); const pct = d.slice(1).map((v, i) => [v[0], (v[1] / d[i][1] - 1) * 100] as [string, number]);
  const mx = Math.max(...pct.map((q) => Math.abs(q[1]))); const slot = w / n; const bw = slot * 0.58;
  return (
    <svg width={1920} height={1080} style={{ position: "absolute" }}>
      <line x1={x} x2={x + w * zacht(f / 12)} y1={y} y2={y} stroke={kleur.zacht} strokeWidth={3} />
      {pct.map(([dag, p], i) => {
        const g = zacht((f - 8 - i * per) / 12); if (g <= 0) return null;
        const bh = (h * Math.abs(p)) / mx * g; const cx = x + slot * (i + 0.5); const laatste = i === n - 1;
        const dt = new Date(dag + "T12:00");
        return (
          <g key={i}>
            <text x={cx} y={y - 18} textAnchor="middle" style={{ font: `400 22px ${font.cijfer}`, fill: kleur.zacht }}>{MAAND[dt.getMonth()]} {dt.getDate()}</text>
            <rect x={cx - bw / 2} y={y + 3} width={bw} height={bh} rx={8} fill={laatste ? "#c81d25" : kleur.rood} opacity={laatste ? 1 : 0.85} />
            {g >= 1 && <text x={cx} y={y + bh + 40} textAnchor="middle" style={{ font: `800 ${laatste ? 34 : 26}px ${font.cijfer}`, fill: laatste ? "#fff" : kleur.rood }}>{p.toFixed(1)}%</text>}
          </g>
        );
      })}
    </svg>
  );
};

export const TijdLijn: React.FC<{ van: number; tot: number; start: number; punten: { jaar: number; tekst: string; op: number; k?: string }[]; x: number; y: number; w: number }> = ({ van, tot, start, punten, x, y, w }) => {
  const f = useCurrentFrame() - start;
  if (f < 0) return null;
  const X = (j: number) => x + ((j - van) / (tot - van)) * w;
  const lijn = inUit(f / 50);
  return (
    <svg width={1920} height={1080} style={{ position: "absolute" }}>
      <line x1={x} x2={x + w * lijn} y1={y} y2={y} stroke={kleur.cyaan} strokeWidth={4} strokeOpacity={0.7} />
      {Array.from({ length: tot - van + 1 }).map((_, i) => { const j = van + i; const zichtbaar = X(j) <= x + w * lijn; return zichtbaar && ((j % 5 === 0 && tot - j >= 3 && j - van >= 3) || j === van || j === tot) ? (
        <g key={j}><line x1={X(j)} x2={X(j)} y1={y - 10} y2={y + 10} stroke={kleur.zacht} strokeWidth={2} />
          <text x={X(j)} y={y + 44} textAnchor="middle" style={{ font: `400 22px ${font.cijfer}`, fill: kleur.zacht }}>{j}</text></g>) : null; })}
      {punten.map((p, i) => { const a = zacht((f - p.op) / 14); if (a <= 0) return null; const k = p.k ?? kleur.amber; return (
        <g key={i} opacity={a}>
          <circle cx={X(p.jaar)} cy={y} r={14} fill={k} />
          <line x1={X(p.jaar)} x2={X(p.jaar)} y1={y - 16} y2={y - 90} stroke={k} strokeWidth={2} />
          <text x={X(p.jaar)} y={y - 104} textAnchor={X(p.jaar) < x + 300 ? "start" : X(p.jaar) > x + w - 300 ? "end" : "middle"} style={{ font: `700 34px ${font.kop}`, fill: kleur.tekst }}>{p.tekst}</text>
        </g>); })}
    </svg>
  );
};
