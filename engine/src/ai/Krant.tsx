import React from "react";
import { AbsoluteFill, Audio, Img, staticFile, useCurrentFrame, interpolate } from "remotion";
import { inUit, zacht } from "../theme";
import W_ from "./data/woorden-krant.json";
import Z_ from "./data/zinnen-krant.json";
import MD from "./data/md.json";

// PROEF "LEVENDE KRANT" (22 nov 2026): het nieuws als voorpagina die tot leven komt. Zwart drukwerk + één rode inktkleur,
// foto's in krantenraster, grafieken als in een krant. Camera schuift rustig van artikel naar artikel. Alleen stem.
// Feiten: kanalen/marketdoodle/video1/bronnen.md (slotkoersen Yahoo).
const Z = Z_ as [number, number, string, string][];
const WD = W_ as [number, string, number, number][];
const kw = (zin: number, woord: string, na = 0) => {
  const w = WD.find((x) => x[0] === zin && x[1].toLowerCase().replace(/[^\w$%.]/g, "").startsWith(woord.toLowerCase()));
  return (w ? w[2] : Z[zin][0]) + na;
};
export const KRANT_DUUR = Math.round((Z[Z.length - 1][1] + 2.6) * 30);
type D = [string, number][];

const INKT = "#1b1712", ROOD = "#b3261e", PAPIER = "#efe8d8", GRIJS = "#5d554a";
const SERIF = "Georgia, 'Times New Roman', serif";
const GOTISCH = "'Old English Text MT', 'Times New Roman', serif";
const PW = 2600, PH = 3300;

// drukken: tekst verschijnt als inkt (vaag -> scherp)
const Druk: React.FC<{ op: number; t: number; children: React.ReactNode; stijl?: React.CSSProperties }> = ({ op, t, children, stijl }) => {
  const a = zacht((t - op) / 0.45); if (a <= 0) return null;
  return <div style={{ position: "absolute", opacity: a, filter: `blur(${(1 - a) * 6}px)`, ...stijl }}>{children}</div>;
};
// foto in krantenraster
const RasterFoto: React.FC<{ src: string; x: number; y: number; w: number; h: number; pos?: string; op: number; t: number; onder: string }> = ({ src, x, y, w, h, pos = "50% 50%", op, t, onder }) => (
  <Druk op={op} t={t} stijl={{ left: x, top: y, width: w }}>
    <div style={{ position: "relative", width: w, height: h, overflow: "hidden", border: `2px solid ${INKT}` }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: pos, filter: "grayscale(1) contrast(1.35) brightness(1.08) sepia(0.15)" }} />
      <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle, rgba(20,16,10,0.42) 1.1px, transparent 1.8px)", backgroundSize: "6px 6px", mixBlendMode: "multiply" }} />
    </div>
    <div style={{ font: `italic 22px ${SERIF}`, color: GRIJS, marginTop: 8 }}>{onder}</div>
  </Druk>
);
// krantengrafiek: dunne zwarte lijn, het laatste (dalende) stuk in rode inkt
const KGrafiek: React.FC<{ data: D; x: number; y: number; w: number; h: number; op: number; duur: number; t: number; titel: string; nu: string; begin?: boolean }> = ({ data, x, y, w, h, op, duur, t, titel, nu, begin }) => {
  if (t < op) return null;
  const v = data.map((d) => d[1]); const lo = Math.min(...v), hi = Math.max(...v), m = (hi - lo) * 0.12;
  const X = (i: number) => 70 + (i / (data.length - 1)) * (w - 150); const Y = (b: number) => 90 + ((hi + m - b) / (hi - lo + 2 * m)) * (h - 160);
  const n = Math.max(2, Math.floor(data.length * inUit((t - op) / duur))); const iTop = v.indexOf(hi);
  const zwart = data.slice(0, Math.min(n, iTop + 1)).map((d, i) => `${X(i)},${Y(d[1])}`).join(" ");
  const rood = n > iTop ? data.slice(iTop, n).map((d, i) => `${X(i + iTop)},${Y(d[1])}`).join(" ") : "";
  const maanden = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]; let vorige = "";
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: zacht((t - op) / 0.4) }}>
      <svg width={w} height={h}>
        <line x1={0} x2={w} y1={2} y2={2} stroke={INKT} strokeWidth={4} />
        <text x={0} y={52} style={{ font: `bold 36px ${SERIF}`, fill: INKT }}>{titel}</text>
        {[0.25, 0.5, 0.75].map((q) => <line key={q} x1={70} x2={w - 80} y1={90 + q * (h - 160)} y2={90 + q * (h - 160)} stroke="#b9ae98" strokeWidth={1.5} strokeDasharray="3 6" />)}
        {begin && <g><line x1={70} x2={w - 80} y1={Y(data[0][1])} y2={Y(data[0][1])} stroke={GRIJS} strokeWidth={2} strokeDasharray="8 6" /><text x={78} y={Y(data[0][1]) - 10} style={{ font: `italic 24px ${SERIF}`, fill: GRIJS }}>start of 2026</text></g>}
        <polyline points={zwart} fill="none" stroke={INKT} strokeWidth={4} strokeLinejoin="round" />
        {rood && <polyline points={rood} fill="none" stroke={ROOD} strokeWidth={5} strokeLinejoin="round" />}
        {data.map((d, i) => { const mm = d[0].slice(5, 7); if (mm === vorige) return null; vorige = mm; return <text key={i} x={X(i)} y={h - 30} textAnchor="middle" style={{ font: `22px ${SERIF}`, fill: GRIJS }}>{maanden[Number(mm) - 1]}</text>; })}
        <line x1={70} x2={w - 80} y1={h - 60} y2={h - 60} stroke={INKT} strokeWidth={2} />
        {n >= data.length && <g><circle cx={X(data.length - 1)} cy={Y(v[v.length - 1])} r={9} fill={ROOD} />
          <text x={X(data.length - 1) - 16} y={Y(v[v.length - 1]) + 46} textAnchor="end" style={{ font: `bold 30px ${SERIF}`, fill: ROOD }}>{nu}</text></g>}
      </svg>
    </div>
  );
};
// rode stempel
const Stempel: React.FC<{ tekst: string; op: number; t: number; x: number; y: number; maat?: number; hoek?: number; papier?: boolean }> = ({ tekst, op, t, x, y, maat = 64, hoek = -6, papier }) => {
  const a = zacht((t - op) / 0.3); if (a <= 0) return null;
  return <div style={{ position: "absolute", left: x, top: y, transform: `rotate(${hoek}deg) scale(${1.25 - 0.25 * a})`, opacity: a * 0.92, border: `6px solid ${ROOD}`, color: ROOD, font: `900 ${maat}px ${SERIF}`, padding: "6px 22px", letterSpacing: 2, whiteSpace: "nowrap", mixBlendMode: papier ? "normal" : "multiply", background: papier ? PAPIER : "transparent", boxShadow: papier ? "0 20px 60px rgba(0,0,0,0.5)" : "none" }}>{tekst}</div>;
};
const Tekst: React.FC<{ x: number; y: number; w: number; op: number; t: number; children: React.ReactNode }> = ({ x, y, w, op, t, children }) => (
  <Druk op={op} t={t} stijl={{ left: x, top: y, width: w, font: `26px/1.45 ${SERIF}`, color: INKT, textAlign: "justify", columnCount: 2, columnGap: 36 }}>{children}</Druk>
);

// camera: (tijd, midden x, midden y, schaal)
const CAM: [number, number, number, number][] = [
  [0, 1300, 700, 0.78],
  [kw(1, "nasdaq", -0.3), 1150, 820, 0.9],
  [kw(2, "every", -0.3), 1590, 860, 0.95],
  [kw(3, "biggest", -0.5), 990, 1790, 0.98],
  [kw(5, "about", -0.3), 1000, 1880, 1.04],
  [kw(6, "inside", -0.5), 1640, 1790, 1.0],
  [kw(10, "money", -0.6), 1300, 2680, 0.88],
  [kw(13, "so", -0.5), 1300, 1650, 0.315],
];

export const Krant: React.FC = () => {
  const f = useCurrentFrame(); const t = f / 30;
  let k = 0; while (k < CAM.length - 1 && t >= CAM[k + 1][0]) k++;
  const vorig = CAM[Math.max(0, k - 1)], nu = CAM[k];
  const p = k === 0 ? 1 : inUit(Math.min(1, (t - nu[0]) / (k === CAM.length - 1 ? 2.2 : 1.5)));
  const drift = 1 + 0.006 * Math.max(0, t - nu[0] - 1.5);   // heel langzaam verder inzoomen: geen stilstaand beeld
  const cx = vorig[1] + (nu[1] - vorig[1]) * p, cy = vorig[2] + (nu[2] - vorig[2]) * p, s = (vorig[3] + (nu[3] - vorig[3]) * p) * (k === CAM.length - 1 ? 1 + 0.004 * Math.max(0, t - nu[0] - 2.2) : drift);

  const vraag1 = kw(13, "is", -0.2), vraag2 = kw(14, "sale", -0.3);
  return (
    <AbsoluteFill style={{ background: "#2a241e" }}>
      <div style={{ position: "absolute", left: 960 - cx * s, top: 540 - cy * s, width: PW, height: PH, transform: `scale(${s})`, transformOrigin: "0 0", background: PAPIER, boxShadow: "0 30px 120px rgba(0,0,0,0.7)", overflow: "hidden" }}>
        {/* papierstructuur */}
        <svg width={PW} height={PH} style={{ position: "absolute", opacity: 0.22 }}><filter id="ruis"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={4} /><feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.3  0 0 0 0 0.22  0 0 0 0.6 0" /></filter><rect width={PW} height={PH} filter="url(#ruis)" /></svg>
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 40%, transparent 60%, rgba(120,95,60,0.18) 100%)" }} />

        {/* KOP VAN DE KRANT */}
        <div style={{ position: "absolute", left: 0, right: 0, top: 40, textAlign: "center", font: `190px ${GOTISCH}`, color: INKT }}>The Market Daily</div>
        <div style={{ position: "absolute", left: 80, right: 80, top: 268, height: 0, borderTop: `3px solid ${INKT}` }} />
        <div style={{ position: "absolute", left: 80, right: 80, top: 282, display: "flex", justifyContent: "space-between", font: `bold 28px ${SERIF}`, color: INKT, letterSpacing: 3 }}>
          <span>FRIDAY, NOVEMBER 20, 2026</span><span>LATE EDITION</span><span>MARKETS · MONEY · COMPANIES</span></div>
        <div style={{ position: "absolute", left: 80, right: 80, top: 330, height: 6, borderTop: `3px solid ${INKT}`, borderBottom: `1.5px solid ${INKT}` }} />

        {/* OPENINGSVERHAAL: Nasdaq */}
        <Druk op={0.2} t={t} stijl={{ left: 80, top: 380, font: `bold 30px ${SERIF}`, color: ROOD, letterSpacing: 4 }}>MARKETS</Druk>
        <Druk op={kw(0, "front", -0.4)} t={t} stijl={{ left: 80, top: 420, width: 1150, font: `900 128px/1.0 ${SERIF}`, color: INKT, letterSpacing: -2 }}>NASDAQ WIPES OUT 2026</Druk>
        <Druk op={kw(1, "lost", -0.2)} t={t} stijl={{ left: 80, top: 700, width: 1150, font: `italic 46px/1.25 ${SERIF}`, color: INKT }}>Tech index loses 10% in one week, its worst week since March 2020</Druk>
        <Tekst x={80} y={850} w={1150} op={kw(2, "every", -0.4)} t={t}>
          The Nasdaq Composite closed at 22,617.73 on Friday, down 5.3% on the day. It now stands below where it started the year. Since its record close on October 6, the index has fallen 18%. The S&amp;P 500 is more than 11% below its top, in what Wall Street calls a correction. Chip makers led the fall.
        </Tekst>
        <KGrafiek data={MD.ixic26 as D} x={1300} y={400} w={1220} h={820} op={kw(2, "every", -0.3)} duur={2.4} t={t} titel="Nasdaq Composite, 2026 · daily close" nu="22,618" begin />
        <Stempel tekst="−10% IN A WEEK" op={kw(1, "week", -0.1)} t={t} x={1390} y={470} maat={62} hoek={-4} />
        <div style={{ position: "absolute", left: 80, right: 80, top: 1262, borderTop: `3px solid ${INKT}` }} />

        {/* HOOFDVERHAAL: Nvidia */}
        <Druk op={kw(3, "biggest", -0.4)} t={t} stijl={{ left: 80, top: 1300, font: `bold 30px ${SERIF}`, color: ROOD, letterSpacing: 4 }}>LEAD STORY</Druk>
        <Druk op={kw(3, "nvidia", -0.3)} t={t} stijl={{ left: 80, top: 1340, width: 1400, font: `900 104px/1.0 ${SERIF}`, color: INKT, letterSpacing: -2 }}>NVIDIA'S $2.5 TRILLION FALL</Druk>
        <RasterFoto src="ai/jensen-gtc.jpg" x={80} y={1580} w={700} h={430} pos="50% 30%" op={kw(4, "stock", -0.3)} t={t} onder="Jensen Huang, who stepped down on Nov. 12. Photo: NVIDIA Taiwan (CC BY 2.0)" />
        <KGrafiek data={MD.nvda6m as D} x={820} y={1580} w={660} h={500} op={kw(4, "fell", -0.2)} duur={2.2} t={t} titel="NVIDIA, share price ($)" nu="$125.53" />
        <Stempel tekst="−14% IN ONE DAY" op={kw(4, "14", -0.1)} t={t} x={850} y={1790} maat={44} hoek={-4} />
        <Stempel tekst="−47.5% SINCE OCT." op={kw(4, "half", -0.2)} t={t} x={850} y={1890} maat={44} hoek={2} />
        <Tekst x={80} y={2090} w={1400} op={kw(5, "about", -0.3)} t={t}>
          Nvidia fell 14% on Friday, its seventh drop in a row, and closed at $125.53. At its October top the stock was $239.24. About $2.5 trillion in market value has disappeared in six weeks. Reuters reported that the SEC is looking at possible accounting problems; nothing has been proven.
        </Tekst>
        <div style={{ position: "absolute", left: 1520, top: 1300, height: 1000, borderLeft: `2px solid ${INKT}` }} />

        {/* BINNENIN: Anthropic */}
        <Druk op={kw(6, "inside", -0.3)} t={t} stijl={{ left: 1560, top: 1300, font: `bold 30px ${SERIF}`, color: ROOD, letterSpacing: 4 }}>INSIDE · IPO</Druk>
        <Druk op={kw(6, "giant", -0.3)} t={t} stijl={{ left: 1560, top: 1340, width: 960, font: `900 104px/1.0 ${SERIF}`, color: INKT, letterSpacing: -2 }}>A GIANT DEBUT</Druk>
        <Druk op={kw(7, "anthropic", -0.3)} t={t} stijl={{ left: 1560, top: 1470 }}><Img src={staticFile("ai/anthropic-logo.png")} style={{ height: 54, filter: "grayscale(1) contrast(1.4)" }} /></Druk>
        <Druk op={kw(7, "anthropic", 0.2)} t={t} stijl={{ left: 1560, top: 1545, width: 960, font: `italic 34px/1.3 ${SERIF}`, color: INKT }}>Went public on Thursday, Nov. 19, raising more than $81 billion.</Druk>
        <svg width={960} height={600} style={{ position: "absolute", left: 1560, top: 1660 }}>
          <defs><pattern id="arc" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke={INKT} strokeWidth="3" /></pattern></defs>
          <line x1={20} x2={940} y1={520} y2={520} stroke={INKT} strokeWidth={3} />
          {[{ l: "IPO price", v: 83, tx: "$83", op: kw(7, "$83", -0.2), rood: false }, { l: "Day 1", v: 115, tx: "above $115", op: kw(8, "jumped"), rood: false }, { l: "Friday close", v: 88.91, tx: "$88.91", op: kw(9, "back"), rood: true }].map((b, i) => {
            const g = inUit((t - b.op) / 0.8); if (g <= 0) return null; const h = (b.v / 120) * 420 * g; const x = 60 + i * 300;
            return (<g key={i}><rect x={x} y={520 - h} width={200} height={h} fill={b.rood ? ROOD : "url(#arc)"} stroke={INKT} strokeWidth={3} />
              <text x={x + 100} y={520 - h - 18} textAnchor="middle" style={{ font: `bold 40px ${SERIF}`, fill: b.rood ? ROOD : INKT, opacity: g }}>{b.tx}</text>
              <text x={x + 100} y={565} textAnchor="middle" style={{ font: `italic 28px ${SERIF}`, fill: INKT }}>{b.l}</text></g>);
          })}
        </svg>
        <div style={{ position: "absolute", left: 80, right: 80, top: 2330, borderTop: `3px solid ${INKT}` }} />

        {/* GELD: rente */}
        <Druk op={kw(10, "money", -0.4)} t={t} stijl={{ left: 80, top: 2370, font: `bold 30px ${SERIF}`, color: ROOD, letterSpacing: 4 }}>MONEY</Druk>
        <Druk op={kw(10, "interest", -0.3)} t={t} stijl={{ left: 80, top: 2410, width: 2440, font: `900 112px/1.0 ${SERIF}`, color: INKT, letterSpacing: -2 }}>INTEREST RATES CLIMB ABOVE 5%</Druk>
        <RasterFoto src="ai/fed.jpg" x={80} y={2570} w={1000} h={560} op={kw(10, "interest", 0.2)} t={t} onder="The Federal Reserve in Washington. Photo: AgnosticPreachersKid (CC BY-SA 3.0)" />
        <Druk op={kw(11, "10", -0.2)} t={t} stijl={{ left: 1160, top: 2570, font: `900 230px/1 ${SERIF}`, color: ROOD }}>5%+</Druk>
        <Druk op={kw(11, "america", -0.2)} t={t} stijl={{ left: 1170, top: 2810, font: `italic 40px ${SERIF}`, color: INKT }}>10-year U.S. interest rate</Druk>
        <Druk op={kw(12, "makes", -0.2)} t={t} stijl={{ left: 1170, top: 2900, width: 1300, borderLeft: `8px solid ${ROOD}`, paddingLeft: 30, font: `bold 46px/1.25 ${SERIF}`, color: INKT }}>
          “When a safe bond pays 5%, profits far in the future look less exciting.”</Druk>
      </div>

      {/* slotvraag als grote rode stempels over de hele krant */}
      {t >= vraag1 - 0.1 && <AbsoluteFill style={{ background: `rgba(30,24,18,${0.35 * zacht((t - vraag1) / 0.5)})` }} />}
      <Stempel tekst="IS THE AI BOOM OVER?" op={vraag1} t={t} x={300} y={300} maat={100} hoek={-4} papier />
      <Stempel tekst="OR THE SALE OF THE YEAR?" op={vraag2} t={t} x={230} y={560} maat={100} hoek={2} papier />
      <AbsoluteFill style={{ background: "#000", opacity: interpolate(f, [KRANT_DUUR - 24, KRANT_DUUR], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }} />
      <Audio src={staticFile("ai/stem-krant.wav")} />
    </AbsoluteFill>
  );
};
