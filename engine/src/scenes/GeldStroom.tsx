import React from "react";
import { useCurrentFrame } from "remotion";
import { kleur, font, zacht } from "../theme";

// SCÈNE B — GELDSTROOM: knooppunten (bedrijven/beleggers) met gebogen banen waarover "munten" stromen.
// Richting en kleur zeggen wat er gebeurt: groen naar binnen = omzet, rood naar buiten = verkoop.
export type Knoop = { id: string; naam: string; x: number; y: number; sub?: string; groot?: boolean; k?: string };
export type Stroom = { van: string; naar: string; start: number; k?: string; dichtheid?: number; label?: string };

const pad = (a: Knoop, b: Knoop) => {
  const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2 - Math.abs(a.x - b.x) * 0.18 - 40;
  return { d: `M ${a.x} ${a.y} Q ${mx} ${my} ${b.x} ${b.y}`, punt: (t: number) => ({
    x: (1 - t) * (1 - t) * a.x + 2 * (1 - t) * t * mx + t * t * b.x,
    y: (1 - t) * (1 - t) * a.y + 2 * (1 - t) * t * my + t * t * b.y }) };
};

export const GeldStroom: React.FC<{ knopen: Knoop[]; stromen: Stroom[]; knoopStart?: number }> = ({ knopen, stromen, knoopStart = 0 }) => {
  const f = useCurrentFrame();
  const byId = Object.fromEntries(knopen.map((k) => [k.id, k]));
  return (
    <svg width={1920} height={1080} style={{ position: "absolute" }}>
      <defs>
        <filter id="gloed" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
      </defs>
      {stromen.map((s, i) => {
        const a = byId[s.van], b = byId[s.naar]; const p = pad(a, b); const k = s.k ?? kleur.groen;
        const t = f - s.start; if (t < 0) return null;
        const teken = zacht(t / 25);
        const n = s.dichtheid ?? 9;
        return (
          <g key={i}>
            <path d={p.d} stroke={k} strokeOpacity={0.22} strokeWidth={6} fill="none" strokeDasharray={2000} strokeDashoffset={2000 * (1 - teken)} />
            {teken >= 1 && Array.from({ length: n }).map((_, j) => {
              const u = ((t - 25) / 70 + j / n) % 1; const q = p.punt(u);
              return <circle key={j} cx={q.x} cy={q.y} r={9} fill={k} filter="url(#gloed)" opacity={Math.sin(u * Math.PI)} />;
            })}
            {s.label && teken >= 1 && (() => { const m = p.punt(0.5); return (
              <text x={m.x} y={m.y - 26} textAnchor="middle" style={{ font: `700 30px ${font.cijfer}`, fill: k }} opacity={zacht((t - 25) / 15)}>{s.label}</text>); })()}
          </g>
        );
      })}
      {knopen.map((k, i) => {
        const a = zacht((f - knoopStart - i * 5) / 16); const r = k.groot ? 110 : 78; const c = k.k ?? kleur.cyaan;
        return (
          <g key={k.id} transform={`translate(${k.x} ${k.y}) scale(${0.6 + 0.4 * a})`} opacity={a}>
            <circle r={r + 18} fill={c} opacity={0.08} />
            <circle r={r} fill={kleur.paneel} stroke={c} strokeWidth={3} />
            <text y={k.sub ? -6 : 10} textAnchor="middle" style={{ font: `700 ${k.groot ? 40 : k.naam.length > 8 ? 24 : 30}px ${font.kop}`, fill: kleur.tekst }}>{k.naam}</text>
            {k.sub && <text y={30} textAnchor="middle" style={{ font: `400 22px ${font.tekst}`, fill: kleur.zacht }}>{k.sub}</text>}
          </g>
        );
      })}
    </svg>
  );
};
