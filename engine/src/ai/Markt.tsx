import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from "remotion";
import { font, zacht, inUit } from "../theme";
import { K, Foto, Kop, Rubriek, Paneel, Bron, Pijl, Overgang } from "./Delen";
import W_ from "./data/woorden-md.json";
import Z_ from "./data/zinnen-md.json";
import MD from "./data/md.json";

// PROEF 3 MIN (22 nov 2026): inhoud van Market Doodle video 1 (AI-uitverkoop) in de filmische stijl. Alleen de stem, geen muziek/effecten.
// Elk beeld start op zijn kernwoord (Whisper-woordtijden). Feiten: kanalen/marketdoodle/video1/bronnen.md (slotkoersen Yahoo).
const Z = Z_ as [number, number, string, string][];
const WD = W_ as [number, string, number, number][];
const F = (s: number) => Math.round(s * 30);
const kw = (zin: number, woord: string, na = 0) => {
  const w = WD.find((x) => x[0] === zin && x[1].toLowerCase().replace(/[^\w$%.]/g, "").startsWith(woord.toLowerCase()));
  return F((w ? w[2] : Z[zin][0]) + na);
};
const start = (zin: number) => F(Z[zin][0] - 0.5);
export const MARKT_DUUR = F(Z[Z.length - 1][1] + 2.6);
const GRENS = [0, start(5), start(10), start(15), start(20), start(23), start(26), start(30), start(36), start(42), MARKT_DUUR];
const OVERLAP = 14;
type D = [string, number][];
const MAAND = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const dag = (s: string) => { const d = new Date(s + "T12:00"); return `${MAAND[d.getMonth()]} ${d.getDate()}`; };
const getal = (v: number, dec = 0) => v.toLocaleString("en-US", { maximumFractionDigits: dec, minimumFractionDigits: dec });

// ---------- grote koersgrafiek (broadcast): tekent zich, top + nu (+ optioneel laagste, beginlijn, tweede lijn) ----------
const Grafiek: React.FC<{ data: D; van: number; duur: number; x: number; y: number; w: number; h: number; titel: string; eenheid?: string; kleur?: string;
  toon?: ("top" | "nu" | "laag" | "begin")[]; tweede?: (number | null)[]; tweedeNaam?: string; jaren?: boolean; topI?: number; markeer?: { i: number; tekst: string; op: number }[] }> =
  ({ data, van, duur, x, y, w, h, titel, eenheid = "", kleur = K.red, toon = ["top", "nu"], tweede, tweedeNaam, jaren, topI, markeer = [] }) => {
  const f = useCurrentFrame() - van;
  if (f < 0) return null;
  const v = data.map((d) => d[1]); const t2 = (tweede ?? []).filter((q): q is number => q !== null);
  const lo = Math.min(...v, ...t2), hi = Math.max(...v, ...t2), m = (hi - lo) * 0.1;
  const X = (i: number) => x + 90 + (i / (data.length - 1)) * (w - 210); const Y = (b: number) => y + 110 + ((hi + m - b) / (hi - lo + 2 * m)) * (h - 190);
  const p = inUit(f / duur); const n = Math.max(2, Math.floor(data.length * p));
  const pts = data.slice(0, n).map((d, i) => `${X(i)},${Y(d[1])}`).join(" ");
  const iTop = topI ?? v.indexOf(Math.max(...v)); const iLaag = v.indexOf(Math.min(...v)); const a = zacht(f / 14);
  const stap = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000].find((s) => (hi - lo) / s <= 5) ?? 5000;
  const grid: number[] = []; for (let g = Math.ceil((lo - m) / stap) * stap; g <= hi + m; g += stap) grid.push(g);
  const lab = (i: number, tekst: string, k: string, onder?: boolean) => {
    const px = X(i), py = Y(data[i][1]); const bw = tekst.length * 17 + 40; const links = px > x + w * 0.6;
    const bx = links ? px - bw - 24 : px + 24; const by = onder ? py + 18 : py - 70;
    return (<g key={tekst}><circle cx={px} cy={py} r={12} fill={K.bg} stroke={k} strokeWidth={6} />
      <rect x={bx} y={by} width={bw} height={52} rx={26} fill={k === K.red ? K.red : "#1d2c48"} stroke={K.line} />
      <text x={bx + bw / 2} y={by + 35} textAnchor="middle" style={{ font: `800 27px ${font.kop}`, fill: "#fff" }}>{tekst}</text></g>);
  };
  const labels: Record<string, string> = {};
  return (
    <div style={{ position: "absolute", left: 0, top: 0, opacity: a }}>
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, background: "rgba(6,11,22,0.88)", border: `1px solid ${K.line}`, borderTop: `6px solid ${kleur}`, boxShadow: "0 40px 100px rgba(0,0,0,0.55)" }}>
        <div style={{ position: "absolute", left: 36, top: 22, font: `800 38px ${font.kop}`, color: K.ink }}>{titel}</div>
        <div style={{ position: "absolute", left: 38, top: 70, font: `500 23px ${font.tekst}`, color: K.soft }}>Closing prices{eenheid ? ` · ${eenheid}` : ""}</div>
        {tweedeNaam && <div style={{ position: "absolute", right: 36, top: 30, display: "flex", gap: 24, font: `600 24px ${font.kop}`, color: K.soft }}>
          <span><span style={{ display: "inline-block", width: 26, height: 5, background: kleur, marginRight: 10, verticalAlign: "middle" }} />Price</span>
          <span><span style={{ display: "inline-block", width: 26, height: 5, background: K.amber, marginRight: 10, verticalAlign: "middle" }} />{tweedeNaam}</span></div>}
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
        <defs><linearGradient id={`v${van}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={kleur} stopOpacity={0.32} /><stop offset="1" stopColor={kleur} stopOpacity={0} /></linearGradient></defs>
        {grid.map((g) => (<g key={g}><line x1={x + 90} x2={x + w - 120} y1={Y(g)} y2={Y(g)} stroke={K.line} strokeDasharray="6 10" />
          <text x={x + w - 108} y={Y(g) + 8} style={{ font: `500 22px ${font.cijfer}`, fill: K.soft }}>{getal(g)}</text></g>))}
        {(() => { const seen = new Set<string>(); let lastX = -999; return data.map((d, i) => { const k = jaren ? d[0].slice(0, 4) : d[0].slice(0, 7);
          if (seen.has(k) || (jaren && Number(k) % 3 !== 0 && i > 0)) return null; seen.add(k); if (X(i) - lastX < 90) return null; lastX = X(i);
          return <text key={k} x={X(i)} y={y + h - 40} textAnchor="middle" style={{ font: `500 22px ${font.cijfer}`, fill: K.soft }}>{jaren ? k : MAAND[Number(d[0].slice(5, 7)) - 1]}</text>; }); })()}
        {toon.includes("begin") && <g><line x1={X(0)} x2={x + w - 120} y1={Y(data[0][1])} y2={Y(data[0][1])} stroke={K.ink} strokeWidth={2} strokeDasharray="4 6" />
          <text x={X(0) + 10} y={Y(data[0][1]) - 12} style={{ font: `700 24px ${font.kop}`, fill: K.ink }}>Start of 2026</text></g>}
        <polygon points={`${X(0)},${y + h - 80} ${pts} ${X(n - 1)},${y + h - 80}`} fill={`url(#v${van})`} />
        <polyline points={pts} fill="none" stroke={kleur} strokeWidth={5} strokeLinejoin="round" />
        {tweede && <polyline points={tweede.slice(0, n).map((q, i) => (q === null ? null : `${X(i)},${Y(q)}`)).filter(Boolean).join(" ")} fill="none" stroke={K.amber} strokeWidth={4} strokeDasharray="10 6" />}
        {toon.includes("top") && n > iTop && lab(iTop, `Top ${eenheid === "US dollars" ? "$" : ""}${getal(v[iTop])} · ${dag(data[iTop][0])}`, K.ink)}
        {toon.includes("laag") && n > iLaag && iLaag !== data.length - 1 && lab(iLaag, `Low ${getal(v[iLaag])} · ${data[iLaag][0].slice(0, 4)}`, K.red, true)}
        {toon.includes("nu") && n >= data.length && lab(data.length - 1, `Now ${eenheid === "US dollars" ? "$" : ""}${getal(v[v.length - 1], eenheid === "US dollars" ? 2 : 0)} · ${dag(data[data.length - 1][0])}`, K.red, true)}
        {markeer.map((mk) => { const b = zacht((f - mk.op) / 12); if (b <= 0 || n <= mk.i) return null; const px = X(mk.i), py = Y(data[mk.i][1]); return (
          <g key={mk.tekst} opacity={b}><circle cx={px} cy={py} r={16 + 8 * Math.sin(f / 5)} fill="none" stroke={K.amber} strokeWidth={4} />
            <rect x={px - 300} y={py - 110} width={280} height={54} rx={10} fill={K.amber} /><text x={px - 160} y={py - 74} textAnchor="middle" style={{ font: `800 28px ${font.kop}`, fill: "#111" }}>{mk.tekst}</text></g>); })}
        {labels && null}
      </svg>
    </div>
  );
};

// ---------- groot getal met uitleg (kinetisch) ----------
const Getal: React.FC<{ tekst: string; sub: string; van: number; x: number; y: number; k?: string; maat?: number }> = ({ tekst, sub, van, x, y, k = K.red, maat = 130 }) => {
  const f = useCurrentFrame() - van; if (f < 0) return null; const a = zacht(f / 14);
  return (<div style={{ position: "absolute", left: x, top: y, opacity: a, transform: `translateY(${(1 - a) * 30}px)` }}>
    <div style={{ font: `900 ${maat}px ${font.cijfer}`, color: k, lineHeight: 1, textShadow: `0 0 40px ${k}55` }}>{tekst}</div>
    <div style={{ font: `600 34px ${font.kop}`, color: K.ink, marginTop: 10 }}>{sub}</div></div>);
};

// ---------- vijf redenen (routekaart) ----------
const REDENEN = ["Nvidia", "A giant debut", "The chips", "The price of money", "The computers"];
const Route: React.FC<{ actief: number; van: number }> = ({ actief, van }) => {
  const f = useCurrentFrame() - van; if (f < 0) return null;
  return (<div style={{ position: "absolute", right: 60, top: 60, display: "flex", gap: 10, opacity: zacht(f / 12) }}>
    {REDENEN.map((r, i) => (<div key={i} style={{ width: 56, height: 56, borderRadius: 28, display: "flex", alignItems: "center", justifyContent: "center", font: `900 28px ${font.cijfer}`,
      background: i === actief ? K.amber : i < actief ? "rgba(255,181,71,0.25)" : "rgba(255,255,255,0.08)", color: i === actief ? "#111" : K.ink, border: `2px solid ${i === actief ? K.amber : K.line}` }}>{i + 1}</div>))}
  </div>);
};
const RedenKop: React.FC<{ nr: number; tekst: string; van: number }> = ({ nr, tekst, van }) => (<>
  <Route actief={nr - 1} van={van} />
  <Rubriek tekst={`REASON ${nr} OF 5`} van={van} x={90} y={64} kleur={K.amber} />
  <Kop tekst={tekst} van={van + 4} x={84} y={110} maat={86} />
</>);

// ================= SCÈNES =================
const s0 = (z: number) => (x: number) => x - GRENS[z];

const Haak: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(0);
  return (<AbsoluteFill>
    <Foto src="ai/nasdaq.jpg" duur={GRENS[1]} zoom={[1.2, 1.05]} pan={[20, 0, -20, 0]} donker={0.5} />
    <div style={{ opacity: 1 - zacht((f - t(kw(2, "every", -0.2))) / 10) }}>
    <Rubriek tekst="MARKETS · NOVEMBER 20, 2026" van={0} x={90} y={70} />
    <Kop tekst="THE NASDAQ" van={4} x={84} y={120} maat={150} />
    <Kop tekst="JUST ERASED 2026" van={14} x={84} y={270} maat={150} kleur={K.red} />
    <Getal tekst="−5.3%" sub="Friday, in one day" van={t(kw(0, "fell"))} x={90} y={480} />
    <Getal tekst="−10%" sub="this week" van={t(kw(1, "lost"))} x={560} y={480} />
    <Getal tekst="2020" sub="worst week since March" van={t(kw(1, "worst"))} x={980} y={480} k={K.amber} />
    </div>
    {f >= t(kw(2, "every")) && <Grafiek data={MD.ixic26 as D} van={t(kw(2, "every", -0.2))} duur={50} x={60} y={60} w={1800} h={960} titel="Nasdaq Composite · 2026" eenheid="index points" toon={["begin", "nu"]} />}
    <div style={{ position: "absolute", left: 0, right: 0, top: 860, textAlign: "center", opacity: zacht((f - t(kw(4, "dot"))) / 12) * (f >= t(kw(4, "dot")) ? 1 : 0), font: `900 72px ${font.zwaar}`, color: K.ink, textShadow: "0 6px 30px #000" }}>The dot-com crash all over again?</div>
    <Bron tekst="Photo: Luca Marfè (CC BY 2.0)" />
  </AbsoluteFill>);
};

const Schade: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(1);
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 40%, #0f1e38 0%, #04070d 75%)" }}>
    <Rubriek tekst="THE DAMAGE" van={0} x={90} y={64} />
    <Kop tekst="FROM RECORD TO CORRECTION" van={4} x={84} y={110} maat={80} />
    <Grafiek data={(MD.ixic26 as D).filter((d) => d[0] >= "2026-06-01")} van={t(kw(5, "october", -0.4))} duur={70} x={60} y={230} w={1180} h={790} titel="Nasdaq Composite" eenheid="index points" toon={["top", "nu"]} />
    <Getal tekst="−18%" sub="Nasdaq, since the Oct 6 record" van={t(kw(6, "fallen"))} x={1300} y={260} />
    <Getal tekst="−11.6%" sub="S&P 500, below its top" van={t(kw(7, "11", -0.2))} x={1300} y={500} maat={110} k={K.amber} />
    <Paneel van={t(kw(8, "correction", -0.3))} x={1300} y={740} w={560} kleur={K.amber} titel="What is a correction?" tekst="A fall of more than 10% from the top." />
    {f >= t(kw(9, "five", -0.2)) && <AbsoluteFill style={{ background: `rgba(4,7,13,${0.85 * zacht((f - t(kw(9, "five", -0.2))) / 12)})` }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 260, textAlign: "center", font: `900 96px ${font.zwaar}`, color: K.ink }}>FIVE REASONS</div>
      {REDENEN.map((r, i) => { const a = zacht((f - t(kw(9, "five")) - i * 5) / 10); return (
        <div key={i} style={{ position: "absolute", left: 140 + i * 340, top: 470, width: 300, opacity: a, transform: `translateY(${(1 - a) * 30}px)`, textAlign: "center" }}>
          <div style={{ width: 120, height: 120, borderRadius: 60, margin: "0 auto", background: K.amber, color: "#111", font: `900 64px ${font.cijfer}`, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
          <div style={{ font: `800 36px ${font.kop}`, color: K.ink, marginTop: 24 }}>{r}</div></div>); })}
    </AbsoluteFill>}
  </AbsoluteFill>);
};

const Nvidia: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(2);
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 40%, #0f1e38 0%, #04070d 75%)" }}>
    <RedenKop nr={1} tekst="NVIDIA" van={0} />
    <Grafiek data={MD.nvda6m as D} van={t(kw(11, "friday", -0.3))} duur={60} x={60} y={230} w={1160} h={790} titel="NVIDIA share price" eenheid="US dollars" kleur={K.green} toon={["top", "nu"]} />
    <Getal tekst="−14%" sub="Friday · 7th drop in a row" van={t(kw(11, "14", -0.1))} x={1280} y={250} />
    <Getal tekst="−47.5%" sub="since the October top" van={t(kw(12, "half", -0.3))} x={1280} y={470} maat={110} k={K.amber} />
    {f >= t(kw(13, "jensen", -0.4)) && (() => { const a = zacht((f - t(kw(13, "jensen", -0.4))) / 16); return (
      <div style={{ position: "absolute", left: 1280, top: 660, width: 580, opacity: a, transform: `translateX(${(1 - a) * 60}px)` }}>
        <div style={{ position: "relative", height: 240, overflow: "hidden", border: `1px solid ${K.line}` }}><Img src={staticFile("ai/jensen-gtc.jpg")} style={{ width: 580, height: 240, objectFit: "cover", objectPosition: "50% 35%" }} /></div>
        <div style={{ background: K.panel, padding: "12px 18px", font: `800 30px ${font.kop}`, color: K.ink }}>Jensen Huang stepped down · Nov 12</div>
        <div style={{ font: `400 15px ${font.tekst}`, color: K.soft, marginTop: 4 }}>Photo: NVIDIA Taiwan (CC BY 2.0)</div></div>); })()}
    {f >= t(kw(14, "reuters", -0.3)) && (() => { const a = zacht((f - t(kw(14, "reuters", -0.3))) / 14); const st = zacht((f - t(kw(14, "nothing", -0.2))) / 10); return (
      <AbsoluteFill style={{ background: `rgba(4,7,13,${0.8 * a})` }}>
        <div style={{ position: "absolute", left: 260, top: 330, width: 1400, opacity: a, background: K.panel, borderLeft: `10px solid ${K.red}`, padding: "40px 50px" }}>
          <div style={{ font: `700 30px ${font.kop}`, color: K.soft, letterSpacing: 4 }}>REUTERS REPORTED</div>
          <div style={{ font: `900 64px ${font.zwaar}`, color: K.ink, marginTop: 14, lineHeight: 1.1 }}>The SEC is looking at possible accounting problems at Nvidia</div></div>
        {st > 0 && <div style={{ position: "absolute", left: 1150, top: 640, transform: `rotate(-6deg) scale(${1.4 - 0.4 * st})`, opacity: st, border: `6px solid ${K.amber}`, color: K.amber, font: `900 54px ${font.zwaar}`, padding: "10px 24px", letterSpacing: 2 }}>NOTHING PROVEN</div>}
      </AbsoluteFill>); })()}
  </AbsoluteFill>);
};

const Anthropic: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(3);
  const stap = [{ l: "IPO price", v: 83, tx: "$83", op: kw(16, "$83", -0.2), k: K.cyan }, { l: "Day 1 high", v: 115, tx: ">$115", op: kw(17, "jumped"), k: K.green }, { l: "Friday close", v: 88.91, tx: "$88.91", op: kw(18, "back"), k: K.red }];
  const base = 900, H = 520;
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 40%, #0f1e38 0%, #04070d 75%)" }}>
    <RedenKop nr={2} tekst="A GIANT DEBUT" van={0} />
    <div style={{ position: "absolute", left: 90, top: 250, opacity: zacht((f - t(kw(16, "anthropic", -0.3))) / 12), background: "#fff", padding: "22px 28px" }}><Img src={staticFile("ai/anthropic-logo.png")} style={{ height: 44 }} /></div>
    <Getal tekst="$81B" sub="raised on Thursday, Nov 19" van={t(kw(16, "$81", -0.1))} x={90} y={370} k={K.green} />
    <div style={{ position: "absolute", left: 760, top: 250, width: 1100, height: 770, opacity: zacht((f - t(kw(16, "$83", -0.6))) / 12), background: "rgba(6,11,22,0.88)", border: `1px solid ${K.line}`, borderTop: `6px solid ${K.cyan}` }}>
      <div style={{ position: "absolute", left: 36, top: 22, font: `800 38px ${font.kop}`, color: K.ink }}>Anthropic share price</div>
      <div style={{ position: "absolute", left: 38, top: 70, font: `500 23px ${font.tekst}`, color: K.soft }}>US dollars · first two days of trading</div>
    </div>
    <svg width={1920} height={1080} style={{ position: "absolute" }}>
      {stap.map((s, i) => { const g = zacht((f - t(s.op)) / 20); if (g <= 0) return null; const h = (s.v / 120) * H * g; const x = 860 + i * 330; return (
        <g key={i}><rect x={x} y={base - h} width={230} height={h} rx={10} fill={s.k} />
          {g > 0.9 && <text x={x + 115} y={base - h - 20} textAnchor="middle" style={{ font: `900 54px ${font.cijfer}`, fill: K.ink }}>{s.tx}</text>}
          <text x={x + 115} y={base + 46} textAnchor="middle" style={{ font: `800 30px ${font.kop}`, fill: K.ink }}>{s.l}</text></g>); })}
    </svg>
    <Paneel van={t(kw(19, "sell", -0.6))} x={90} y={700} w={600} kleur={K.amber} titel="“Sell the news”" tekst="Some investors used the big day to cash in." />
  </AbsoluteFill>);
};

const Chips: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(4);
  const rijen = [{ n: "Broadcom", logo: "ai/broadcom-logo.png", v: 12.2, tx: "−12.2%", op: kw(21, "broadcom", -0.2), sub: "Friday" }, { n: "AMD", logo: "ai/amd-logo.png", v: 13.25, tx: "−13.3%", op: kw(21, "amd", -0.2), sub: "Friday" },
                 { n: "Chip-maker fund", logo: "", v: 15, tx: "≈ −15%", op: kw(22, "fund", -0.2), sub: "in one week" }];
  return (<AbsoluteFill>
    <Foto src="ai/chip.jpg" duur={GRENS[5] - GRENS[4]} zoom={[1.0, 1.15]} donker={0.82} links={false} />
    <RedenKop nr={3} tekst="THE CHIPS THEMSELVES" van={0} />
    {rijen.map((r, i) => { const a = zacht((f - t(r.op)) / 14); const w = (r.v / 16) * 1000 * zacht((f - t(r.op) - 6) / 22); const y = 300 + i * 230; return (
      <div key={i} style={{ position: "absolute", left: 90, top: y, opacity: a }}>
        <div style={{ width: 420, height: 150, background: "#fff", display: "flex", alignItems: "center", justifyContent: "center" }}>
          {r.logo ? <Img src={staticFile(r.logo)} style={{ maxWidth: 340, maxHeight: 80 }} /> : <div style={{ font: `900 40px ${font.zwaar}`, color: "#111", textAlign: "center" }}>Chip-maker<br />fund</div>}</div>
        <div style={{ position: "absolute", left: 460, top: 20, height: 110, width: w, background: `linear-gradient(90deg, ${K.red}, #ff7a7f)`, borderRadius: 8 }} />
        <div style={{ position: "absolute", left: 480 + w, top: 22, font: `900 70px ${font.cijfer}`, color: K.ink, whiteSpace: "nowrap" }}>{r.tx}<span style={{ font: `600 30px ${font.kop}`, color: K.soft, marginLeft: 18 }}>{r.sub}</span></div>
      </div>); })}
    <Bron tekst="Photo: Fritzchens Fritz (CC0) · Logos: Wikimedia Commons" />
  </AbsoluteFill>);
};

const Geld: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(5);
  const kant = zacht((f - t(kw(25, "when", -0.2))) / 30) * 12;   // weegschaal kantelt naar de veilige obligatie
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #102240 0%, #04070d 75%)" }}>
    <RedenKop nr={4} tekst="THE PRICE OF MONEY" van={0} />
    <Getal tekst="> 5%" sub="10-year US interest rate" van={t(kw(24, "10", -0.2))} x={90} y={300} k={K.amber} maat={180} />
    <div style={{ position: "absolute", left: 90, top: 610, width: 620, font: `500 34px ${font.tekst}`, color: K.soft, lineHeight: 1.35, opacity: zacht((f - t(kw(25, "profits"))) / 14) }}>
      Tech stocks are valued on profits far in the future. A safe 5% today makes those look less attractive.</div>
    <svg width={1920} height={1080} style={{ position: "absolute", opacity: zacht((f - t(kw(25, "when", -0.4))) / 14) }}>
      <g transform="translate(1290 520)">
        <polygon points="-40,330 40,330 0,40" fill="#2a3a5c" />
        <g transform={`rotate(${kant})`}>
          <rect x={-420} y={30} width={840} height={16} rx={8} fill={K.soft} />
          <line x1={-360} y1={38} x2={-360} y2={150} stroke={K.soft} strokeWidth={4} /><line x1={360} y1={38} x2={360} y2={150} stroke={K.soft} strokeWidth={4} />
          <g transform={`translate(-360 150) rotate(${-kant})`}><rect x={-150} y={0} width={300} height={170} rx={14} fill={K.amber} />
            <text x={0} y={70} textAnchor="middle" style={{ font: `900 44px ${font.zwaar}`, fill: "#111" }}>SAFE BOND</text><text x={0} y={125} textAnchor="middle" style={{ font: `800 40px ${font.cijfer}`, fill: "#111" }}>5% today</text></g>
          <g transform={`translate(360 150) rotate(${-kant})`}><rect x={-150} y={0} width={300} height={170} rx={14} fill="#1d2c48" stroke={K.cyan} strokeWidth={3} />
            <text x={0} y={70} textAnchor="middle" style={{ font: `900 40px ${font.zwaar}`, fill: K.ink }}>TECH PROFITS</text><text x={0} y={125} textAnchor="middle" style={{ font: `700 34px ${font.kop}`, fill: K.cyan }}>years away</text></g>
        </g>
      </g>
    </svg>
  </AbsoluteFill>);
};

const Computers: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(6);
  const sp = MD.sp200 as [string, number, number | null][];
  const kruis = sp.findIndex((r) => r[2] !== null && r[1] < (r[2] as number));
  const lus = zacht((f - t(kw(29, "selling", -0.3))) / 16);
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 40%, #0f1e38 0%, #04070d 75%)" }}>
    <RedenKop nr={5} tekst="THE COMPUTERS" van={0} />
    <Grafiek data={sp.map((r) => [r[0], r[1]]) as D} tweede={sp.map((r) => r[2])} tweedeNaam="200-day average" van={t(kw(27, "s", -0.4))} duur={60} x={60} y={230} w={1240} h={790} titel="S&P 500" eenheid="index points" kleur={K.cyan} toon={["top", "nu"]}
      markeer={[{ i: kruis, tekst: "Sell signal", op: t(kw(28, "automatic", -0.2)) }]} />
    <Paneel van={t(kw(28, "trend", -0.3))} x={1360} y={250} w={500} kleur={K.amber} titel="Trend-following funds" tekst="Computer programs that sell when prices fall below their long-term average." />
    {lus > 0 && <svg width={1920} height={1080} style={{ position: "absolute", opacity: lus }}>
      <g transform="translate(1610 760)">
        {["Selling", "Lower prices", "More selling"].map((w, i) => { const hk = -Math.PI / 2 + (i * 2 * Math.PI) / 3 + f * 0.01; const x = Math.cos(hk) * 150, y = Math.sin(hk) * 150; return (
          <g key={i}><circle cx={x} cy={y} r={80} fill={K.panel} stroke={K.red} strokeWidth={3} /><text x={x} y={y + 9} textAnchor="middle" style={{ font: `800 24px ${font.kop}`, fill: K.ink }}>{w}</text></g>); })}
        <circle r={150} fill="none" stroke={K.red} strokeWidth={4} strokeDasharray="20 16" strokeDashoffset={-f * 2} opacity={0.7} />
      </g></svg>}
  </AbsoluteFill>);
};

const Dotcom: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(7);
  const meta = MD.dotcom_meta as unknown as { top: [string, number]; low: [string, number]; terug: [string, number] };
  const vgl = zacht((f - t(kw(32, "big", -0.3))) / 16);
  const per = Math.floor(30 * Math.max(0, f - t(kw(34, "earns"))) / 30);
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 40%, #0f1e38 0%, #04070d 75%)" }}>
    <Rubriek tekst="THE BIG QUESTION" van={0} x={90} y={64} kleur={K.cyan} />
    <Kop tekst="IS THIS 2000 AGAIN?" van={4} x={84} y={110} maat={86} />
    <div style={{ opacity: 1 - vgl }}>
      <Grafiek data={MD.dotcom as D} van={t(kw(31, "back", -0.3))} duur={80} x={60} y={230} w={1800} h={790} titel="Nasdaq Composite · 1998 – 2015" eenheid="index points" kleur={K.red} toon={["top", "laag"]} jaren topI={(MD.dotcom as D).findIndex((d) => d[0] === meta.top[0])} />
      <Getal tekst="−78%" sub="Mar 2000 → Oct 2002" van={t(kw(31, "78", -0.2))} x={980} y={330} />
      <Getal tekst="15 years" sub={`back above the 2000 top (${meta.terug[0].slice(0, 4)})`} van={t(kw(31, "15", -0.2))} x={1300} y={560} k={K.amber} maat={100} />
    </div>
    {vgl > 0 && <div style={{ position: "absolute", left: 90, top: 260, right: 90, bottom: 60, display: "flex", gap: 40, opacity: vgl }}>
      <div style={{ flex: 1, background: K.panel, borderTop: `8px solid ${K.red}`, padding: "40px 46px" }}>
        <div style={{ font: `900 110px ${font.cijfer}`, color: K.red }}>2000</div>
        <div style={{ font: `800 46px ${font.kop}`, color: K.ink, marginTop: 20, lineHeight: 1.2, opacity: zacht((f - t(kw(33, "many"))) / 12) }}>Many internet companies had almost no profits</div></div>
      <div style={{ flex: 1, background: K.panel, borderTop: `8px solid ${K.green}`, padding: "40px 46px" }}>
        <div style={{ font: `900 110px ${font.cijfer}`, color: K.green }}>2026</div>
        <div style={{ font: `800 46px ${font.kop}`, color: K.ink, marginTop: 20, lineHeight: 1.2, opacity: zacht((f - t(kw(34, "nvidia", -0.2))) / 12) }}>Nvidia earns more than</div>
        <div style={{ font: `900 120px ${font.cijfer}`, color: K.green, marginTop: 10, opacity: zacht((f - t(kw(34, "$1", -0.2))) / 12) }}>$1 billion</div>
        <div style={{ font: `800 46px ${font.kop}`, color: K.ink, opacity: zacht((f - t(kw(34, "every", -0.2))) / 12) }}>every single day</div></div>
    </div>}
    {f >= t(kw(35, "question", -0.3)) && <div style={{ position: "absolute", left: 90, right: 90, bottom: 60, background: K.amber, color: "#111", padding: "22px 34px", font: `800 42px ${font.kop}`, opacity: zacht((f - t(kw(35, "question", -0.3))) / 12) }}>
      The money is real. The question: how much of the future is already in the price?</div>}
    {per < 0 && null}
  </AbsoluteFill>);
};

const VoorJou: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(8);
  const kaarten = [
    { k: K.cyan, t1: "Corrections are normal", t2: "", op: kw(37, "corrections", -0.3) },
    { k: K.green, t1: "≈ 8–9% a year", t2: "long-run average, says Jeremy Siegel (Wharton) — never in a straight line", op: kw(38, "8", -0.4) },
    { k: K.amber, t1: "Falling price ≠ broken business", t2: "and a low price ≠ a bargain", op: kw(40, "falling", -0.3) },
  ];
  // zigzag-lijn omhoog: "nooit in een rechte lijn" (illustratie, geen echte koers)
  const zz = [0, 30, 10, 55, 35, 80, 50, 105, 70, 120, 95, 150]; const zp = zacht((f - t(kw(39, "never", -0.3))) / 30);
  return (<AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #102240 0%, #04070d 75%)" }}>
    <Rubriek tekst="WHAT IT MEANS FOR YOU" van={0} x={90} y={64} kleur={K.green} />
    <Kop tekst="KEEP CALM, LOOK CLOSER" van={4} x={84} y={110} maat={86} />
    {kaarten.map((c, i) => { const a = zacht((f - t(c.op)) / 14); return (
      <div key={i} style={{ position: "absolute", left: 90 + i * 590, top: 290, width: 550, height: 520, opacity: a, transform: `translateY(${(1 - a) * 30}px)`, background: K.panel, borderTop: `8px solid ${c.k}`, padding: "36px 38px", boxSizing: "border-box" }}>
        <div style={{ font: `900 64px ${font.cijfer}`, color: c.k }}>{i + 1}</div>
        <div style={{ font: `900 50px ${font.zwaar}`, color: K.ink, marginTop: 16, lineHeight: 1.1 }}>{c.t1}</div>
        {c.t2 && <div style={{ font: `500 30px ${font.tekst}`, color: K.soft, marginTop: 16, lineHeight: 1.3 }}>{c.t2}</div>}
        {i === 1 && <svg width={470} height={150} style={{ position: "absolute", left: 40, bottom: 30 }}>
          <polyline points={zz.slice(0, Math.max(2, Math.ceil(zz.length * zp))).map((v, j) => `${j * 42},${140 - v * 0.85}`).join(" ")} fill="none" stroke={K.green} strokeWidth={6} strokeLinejoin="round" /></svg>}
      </div>); })}
    <div style={{ position: "absolute", left: 90, bottom: 70, font: `500 26px ${font.tekst}`, color: K.soft }}>Not financial advice. The zigzag line is an illustration, not real data.</div>
  </AbsoluteFill>);
};

const Slot: React.FC = () => {
  const f = useCurrentFrame(); const t = s0(9);
  const vraag = zacht((f - t(kw(44, "is", -0.3))) / 16);
  return (<AbsoluteFill>
    <Foto src="ai/fed.jpg" duur={MARKT_DUUR - GRENS[9]} zoom={[1.05, 1.2]} donker={0.55 + 0.3 * vraag} />
    <Rubriek tekst="WHAT COMES NEXT" van={0} x={90} y={64} kleur={K.cyan} />
    <div style={{ opacity: 1 - vraag }}>
      <Getal tekst="December" sub="The Federal Reserve decides on interest rates" van={t(kw(42, "december", -0.2))} x={90} y={300} k={K.cyan} maat={140} />
    </div>
    <Kop tekst="IS THE AI BOOM OVER" van={t(kw(44, "is", -0.2))} x={0} y={330} maat={110} midden />
    <Kop tekst="OR THE SALE OF THE YEAR?" van={t(kw(44, "sale", -0.3))} x={0} y={480} maat={110} kleur={K.cyan} midden />
    <Bron tekst="Photo: AgnosticPreachersKid (CC BY-SA 3.0)" />
  </AbsoluteFill>);
};

// heel rustige camerabeweging per scène (geen stilstaand beeld), 2,5% over de hele scène
const Drift: React.FC<{ duur: number; children: React.ReactNode }> = ({ duur, children }) => {
  const f = useCurrentFrame(); const p = f / duur;
  return <AbsoluteFill style={{ transform: `scale(${1 + 0.025 * p}) translateX(${-8 * p}px)`, transformOrigin: "45% 50%" }}>{children}</AbsoluteFill>;
};

export const Markt: React.FC = () => {
  const scenes = [Haak, Schade, Nvidia, Anthropic, Chips, Geld, Computers, Dotcom, VoorJou, Slot];
  return (
    <AbsoluteFill style={{ background: K.bg }}>
      {scenes.map((S, i) => {
        const van = Math.max(0, GRENS[i] - (i ? OVERLAP : 0)); const tot = GRENS[i + 1]; const d = tot - van;
        return (<Sequence key={i} from={van} durationInFrames={d}><Overgang duur={d} eerste={i === 0} laatste={i === scenes.length - 1}><Drift duur={d}><S /></Drift></Overgang></Sequence>);
      })}
      <Audio src={staticFile("ai/stem-md.wav")} />
    </AbsoluteFill>
  );
};
