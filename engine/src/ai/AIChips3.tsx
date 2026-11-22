import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, interpolate } from "remotion";
import { font, zacht, inUit } from "../theme";
import { K, sec, clamp, Foto, Kop, Rubriek, Paneel, Bron, Pijl, Overgang } from "./Delen";
import { Chip3D } from "./Chip3D";

// v2 (22 nov 2026): grotere beelden (60-80% van het scherm), duidelijkere uitleg, geen ticker, geen zwart eerste beeld,
// elke scène loopt logisch door naar de volgende: datacenter -> chipbord -> inzoomen op de chip -> wie maakt hem -> waar draait hij -> waarom belangrijk.
export const AI3_DUUR = 1677;   // v3: rustiger, ± 56 s
const B = [0, sec(8.1), sec(14.45), sec(21.0), sec(27.6), sec(46.9), AI3_DUUR];
const OVERLAP = 16;

// ---------- 1. INTRO: datacenter -> het chipbord groeit tot bijna het hele beeld -> inzoomen op de chip ----------
const Intro: React.FC<{ d: number; s: number }> = ({ d }) => {
  const f = useCurrentFrame();
  const bord = zacht((f - sec(4.3)) / 30);                 // chipbord komt in beeld op "breakthrough"
  const kopWeg = zacht((f - sec(4.3)) / 20);
  const mark = zacht((f - sec(6.6)) / 16);                  // markering op "technology"
  const inzoom = inUit((f - sec(7.3)) / (d - sec(7.3)));  // naar de chip toe, overgang naar scène 2
  const bx = 1920 - 90 - 1360 * bord - 0 * (1 - bord), bw = 1360, bh = 765;
  return (
    <AbsoluteFill>
      <Foto src="ai/dc.jpg" duur={d} zoom={[1.18, 1.04]} pan={[-30, 10, 20, -10]} donker={0.4} />
      <div style={{ opacity: 1 - kopWeg, transform: `translateY(${-kopWeg * 40}px)` }}>
        <Rubriek tekst="AI SPECIAL REPORT" van={0} x={110} y={170} />
        <Kop tekst="THE AI" van={sec(0.4)} x={104} y={240} maat={200} />
        <Kop tekst="REVOLUTION" van={sec(0.9)} x={104} y={445} maat={200} kleur={K.cyan} />
        <Kop tekst="How AI chips power the future" van={sec(1.9)} x={110} y={690} maat={58} gewicht={600} kleur={K.soft} />
      </div>
      {bord > 0 && (
        <div style={{ position: "absolute", left: bx, top: 160, width: bw, height: bh, overflow: "hidden", boxShadow: "0 40px 100px rgba(0,0,0,0.8)", border: `2px solid ${K.line}`, opacity: bord,
                      transform: `scale(${1 + inzoom * 1.6})`, transformOrigin: "26% 30%" }}>
          <Img src={staticFile("ai/gb200.jpg")} style={{ width: bw, height: bh, objectFit: "cover", transform: `scale(${1.08 - 0.08 * bord})` }} />
          {/* markering: de AI-chips zitten onder de koelplaten */}
          <div style={{ position: "absolute", left: bw * 0.18, top: bh * 0.15, width: bw * 0.15, height: bh * 0.18, border: `6px solid ${K.amber}`, borderRadius: 12, opacity: mark, boxShadow: `0 0 40px ${K.amber}` }} />
          <div style={{ position: "absolute", left: bw * 0.40, top: bh * 0.25, width: bw * 0.11, height: bh * 0.14, border: `6px solid ${K.amber}`, borderRadius: 12, opacity: mark, boxShadow: `0 0 40px ${K.amber}` }} />
        </div>
      )}
      {bord > 0 && <div style={{ position: "absolute", left: 110, top: 70, opacity: bord * (1 - inzoom), font: `900 64px ${font.zwaar}`, color: K.ink }}>Behind every AI breakthrough</div>}
      {mark > 0 && (
        <div style={{ position: "absolute", left: 110, top: 940, opacity: mark * (1 - inzoom), display: "flex", gap: 18, alignItems: "center" }}>
          <div style={{ width: 22, height: 22, borderRadius: 11, background: K.amber, boxShadow: `0 0 20px ${K.amber}` }} />
          <div style={{ font: `800 44px ${font.kop}`, color: K.ink }}>The AI chips sit under these liquid-cooled plates</div>
        </div>
      )}
      <Bron tekst="Photos: G. Rocher / IFREMER (CC BY 4.0) · NVIDIA GB200 boards: Geekerwan (CC BY 3.0)" />
    </AbsoluteFill>
  );
};

// ---------- 2. DE CHIP: groot 3D-model, lagen uit elkaar, onderdeel voor onderdeel uitgelegd ----------
const DeChip: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 35% 55%, #12284a 0%, #05080F 72%)" }}>
      <Chip3D dx={-250} duur={d} zoomVan={135} zoomTot={175} openOp={t(10.4)} labelsOp={[t(10.8), t(11.3), t(11.8), t(12.3), t(12.8)]} stroomOp={t(12.55)} />
      <Rubriek tekst="INSIDE THE PROCESSOR" van={0} x={110} y={90} kleur={K.cyan} />
      <Kop tekst="ONE CHIP, MANY LAYERS" van={4} x={104} y={135} maat={82} />
      <Paneel van={t(12.9)} x={110} y={820} w={780} kleur={K.amber} titel="Billions of calculations" tekst="Memory feeds data to thousands of cores, which work on it at the same time." />
    </AbsoluteFill>
  );
};

// ---------- 3. DE INDUSTRIE: wie ontwerpt, wie maakt ----------
const Industrie: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const split = zacht(f / 14);
  const stappen = [
    { naam: "Chip design", wie: "NVIDIA", op: t(15.8), k: K.green },
    { naam: "Wafer fabrication", wie: "TSMC", op: t(17.5), k: K.red },
    { naam: "Advanced packaging", wie: "TSMC", op: t(19.1), k: K.red },
    { naam: "AI servers", wie: "Data centers", op: t(20.0), k: K.cyan },
  ];
  const bolU = Math.max(0, Math.min(3, (f - t(16.0)) / sec(1.35)));   // lichtpunt reist langs de keten
  return (
    <AbsoluteFill style={{ background: K.bg }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 960 * split, height: 760, overflow: "hidden" }}>
        <Foto src="ai/dgx.jpg" duur={d} zoom={[1.18, 1.0]} donker={0.45} links={false} stijl={{ width: 960 }} />
      </div>
      <div style={{ position: "absolute", right: 0, top: 0, width: 960 * split, height: 760, overflow: "hidden" }}>
        <Foto src="ai/fab.jpg" duur={d} zoom={[1.0, 1.18]} donker={0.45} links={false} stijl={{ width: 960, left: "auto", right: 0 }} />
      </div>
      <div style={{ position: "absolute", left: 957, top: 0, width: 6, height: 760, background: K.ink, opacity: split }} />
      <div style={{ position: "absolute", left: 90, top: 90, opacity: zacht((f - t(15.2)) / 14) }}>
        <div style={{ background: "#fff", padding: "16px 26px", display: "inline-block", boxShadow: "0 10px 40px rgba(0,0,0,0.5)" }}><Img src={staticFile("ai/nvidia-logo.png")} style={{ height: 150 }} /></div>
        <div style={{ font: `900 120px ${font.zwaar}`, color: K.ink, marginTop: 24, lineHeight: 1 }}>DESIGNS</div>
        <div style={{ font: `600 40px ${font.kop}`, color: K.soft, marginTop: 10 }}>the AI chips</div>
      </div>
      <div style={{ position: "absolute", left: 1050, top: 90, opacity: zacht((f - t(18.2)) / 14) }}>
        <div style={{ background: "#fff", padding: "38px 40px", display: "inline-block", boxShadow: "0 10px 40px rgba(0,0,0,0.5)" }}><Img src={staticFile("ai/tsmc-logo.png")} style={{ height: 96 }} /></div>
        <div style={{ font: `900 120px ${font.zwaar}`, color: K.ink, marginTop: 24, lineHeight: 1 }}>MAKES</div>
        <div style={{ font: `600 40px ${font.kop}`, color: K.soft, marginTop: 10 }}>the advanced chips</div>
      </div>
      {/* ontwerp gaat van NVIDIA naar de fabriek van TSMC */}
      <Pijl d="M 700 610 C 860 560, 1060 560, 1220 610" van={t(17.3)} duur={20} kleur={K.amber} dik={8} lengte={600} />
      {f > t(17.8) && <div style={{ position: "absolute", left: 760, top: 500, opacity: zacht((f - t(17.8)) / 12), background: K.amber, color: "#111", font: `800 30px ${font.kop}`, padding: "8px 18px" }}>chip designs → factory</div>}
      {/* keten onderaan */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 760, bottom: 0, background: "linear-gradient(#0b1426, #05080F)", borderTop: `2px solid ${K.line}` }} />
      <div style={{ position: "absolute", left: 90, top: 782, font: `800 26px ${font.kop}`, color: K.soft, letterSpacing: 5 }}>HOW AN AI CHIP IS MADE</div>
      {stappen.map((st, i) => {
        const a = zacht((f - st.op) / 10); const x = 90 + i * 445;
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: x, top: 830, width: 375, height: 200, opacity: a, transform: `translateY(${(1 - a) * 24}px)`, background: K.panel, border: `1px solid ${K.line}`, borderTop: `6px solid ${st.k}`, padding: "18px 24px", boxSizing: "border-box" }}>
              <div style={{ font: `700 24px ${font.kop}`, color: st.k, letterSpacing: 2 }}>STEP {i + 1}</div>
              <div style={{ font: `800 40px ${font.kop}`, color: K.ink, marginTop: 6, lineHeight: 1.05 }}>{st.naam}</div>
              <div style={{ font: `600 28px ${font.kop}`, color: K.soft, marginTop: 8 }}>{st.wie}</div>
            </div>
            {i < 3 && <Pijl d={`M ${x + 382} 930 L ${x + 438} 930`} van={stappen[i + 1].op - 5} duur={6} kleur={K.ink} dik={6} lengte={70} />}
          </React.Fragment>
        );
      })}
      {f > t(16.0) && <div style={{ position: "absolute", left: 90 + 187 + bolU * 445 - 12, top: 1018, width: 24, height: 24, borderRadius: 12, background: K.amber, boxShadow: `0 0 24px ${K.amber}` }} />}
      <Bron tekst="Photos: Pokiiri (CC BY-SA 4.0) · TSMC Fab 14B: 4300streetcar (CC BY 4.0)" />
    </AbsoluteFill>
  );
};

// ---------- 4. WERELDKAART: van de fabrieken in Taiwan naar datacenters over de hele wereld ----------
const MW = 2300, MH = MW / 2;
const plek = (lat: number, lon: number) => ({ x: ((lon + 180) / 360) * MW, y: ((90 - lat) / 180) * MH });
const TAIWAN = plek(24.8, 121.0);
const HUBS = [
  { naam: "Northern Virginia, USA", ...plek(39.0, -77.5), kant: 1 }, { naam: "Oregon, USA", ...plek(45.6, -121.2), kant: 1 },
  { naam: "Dublin, Ireland", ...plek(53.3, -6.3), kant: -1 }, { naam: "Amsterdam, Netherlands", ...plek(52.4, 4.9), kant: 1 },
  { naam: "Mumbai, India", ...plek(19.1, 72.9), kant: -1 }, { naam: "Singapore", ...plek(1.35, 103.8), kant: 1 }, { naam: "Tokyo, Japan", ...plek(35.7, 139.7), kant: -1 },
];
const Wereld: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const p = inUit(f / d);
  const camX = -160 - 150 * p, camY = 95 - 20 * p, sc = 0.98 + 0.06 * p;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 60% 40%, #0e1f3b 0%, #04070d 75%)", overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: MW, height: MH, transform: `translate(${camX}px, ${camY}px) scale(${sc})`, transformOrigin: "0 0" }}>
        <Img src={staticFile("ai/wereld-stijl.png")} style={{ width: MW, height: MH }} />
        <svg width={MW} height={MH} style={{ position: "absolute", left: 0, top: 0 }}>
          <defs><filter id="g4"><feGaussianBlur stdDeviation="5" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter></defs>
          {HUBS.map((h, i) => {
            const st = t(21.9) + i * 7; const a = zacht((f - st) / 16); if (a <= 0) return null;
            const mx = (TAIWAN.x + h.x) / 2, my = Math.min(TAIWAN.y, h.y) - Math.abs(TAIWAN.x - h.x) * 0.2;
            const q = (u: number) => ({ x: (1 - u) ** 2 * TAIWAN.x + 2 * (1 - u) * u * mx + u * u * h.x, y: (1 - u) ** 2 * TAIWAN.y + 2 * (1 - u) * u * my + u * u * h.y });
            const lab = h.naam; const lw = lab.length * 17 + 30; const lx = h.kant > 0 ? h.x + 22 : h.x - 22 - lw;
            return (
              <g key={i}>
                <path d={`M ${TAIWAN.x} ${TAIWAN.y} Q ${mx} ${my} ${h.x} ${h.y}`} stroke={K.cyan} strokeWidth={6} fill="none" strokeDasharray={3000} strokeDashoffset={3000 * (1 - a)} opacity={0.9} filter="url(#g4)" />
                {a >= 1 && [0, 0.33, 0.66].map((o, j) => { const pt = q(((f - st) / 40 + o) % 1); return <circle key={j} cx={pt.x} cy={pt.y} r={8} fill="#fff" filter="url(#g4)" />; })}
                {a >= 1 && <circle cx={h.x} cy={h.y} r={14} fill={K.cyan} stroke="#fff" strokeWidth={4} />}
                {a >= 1 && <g opacity={zacht((f - st - 14) / 8)}><rect x={lx} y={h.y - 52} width={lw} height={46} rx={8} fill="rgba(5,10,20,0.85)" stroke={K.line} />
                  <text x={lx + 15} y={h.y - 20} style={{ font: `700 28px ${font.kop}`, fill: K.ink }}>{lab}</text></g>}
              </g>
            );
          })}
          <circle cx={TAIWAN.x} cy={TAIWAN.y} r={24 + 6 * Math.sin(f / 5)} fill={K.red} opacity={0.35} />
          <circle cx={TAIWAN.x} cy={TAIWAN.y} r={16} fill={K.red} stroke="#fff" strokeWidth={4} />
          <rect x={TAIWAN.x - 380} y={TAIWAN.y + 26} width={360} height={84} rx={10} fill={K.red} />
          <text x={TAIWAN.x - 362} y={TAIWAN.y + 62} style={{ font: `900 32px ${font.zwaar}`, fill: "#fff" }}>TAIWAN</text>
          <text x={TAIWAN.x - 362} y={TAIWAN.y + 96} style={{ font: `600 24px ${font.kop}`, fill: "#fff" }}>TSMC chip factories</text>
        </svg>
      </div>
      <Rubriek tekst="GLOBAL IMPACT" van={0} x={90} y={80} kleur={K.cyan} />
      <Kop tekst="FROM TAIWAN TO THE WORLD" van={4} x={84} y={124} maat={84} />
      <div style={{ position: "absolute", left: 90, top: 226, font: `600 30px ${font.kop}`, color: K.soft, opacity: zacht((f - t(22.0)) / 12) }}>Examples of major data center hubs</div>
      <Paneel van={t(22.4)} x={90} y={850} w={560} kleur={K.cyan} titel="Data centers" tekst="Huge halls of AI servers" />
      <Paneel van={t(23.4)} x={680} y={850} w={560} kleur={K.green} titel="AI systems" tekst="Train and run AI models" />
      <Paneel van={t(25.3)} x={1270} y={850} w={560} kleur={K.amber} titel="Technology worldwide" tekst="Cloud apps, search, phones, cars" />
      <Bron tekst="Map: public domain (CIA World Factbook)" />
    </AbsoluteFill>
  );
};

// ---------- 5. FINANCIEEL: de vraag explodeert (alleen geverifieerde cijfers van NVIDIA zelf) ----------
// Q3 fiscaal 2027 (aug-okt 2026): omzet $115,8 mld (+103%); jaar eerder (Q3 fiscaal 2026): $57,0 mld; datacenter $107,6 mld;
// verwachting volgend kwartaal ± $130 mld (NVIDIA, 17 nov 2026).
const Financieel: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const kaart = zacht(f / 18);
  const base = 830, H = 470, maxV = 130;
  const hoog = (v: number, op: number) => (v / maxV) * H * zacht((f - op) / 26);
  const staaf = [
    { x: 230, v: 57.0, op: t(36.1), k: "#62738f", tx: "$57.0B", l: "A year earlier", m: "Q3 fiscal 2026 · Aug–Oct 2025" },
    { x: 560, v: 115.8, op: t(32.9), k: K.green, tx: "$115.8B", l: "Latest quarter", m: "Q3 fiscal 2027 · Aug–Oct 2026" },
  ];
  const dcA = zacht((f - t(39.4)) / 24);            // datacenter-deel kleurt in
  const dcH = (107.6 / maxV) * H * dcA;
  const verw = zacht((f - t(44.1)) / 26);           // verwachting volgend kwartaal
  const plus = zacht((f - t(36.6)) / 16);
  const donut = zacht((f - t(39.4)) / 30); const paneel = zacht((f - 10) / 18);
  const R = 120, omtrek = 2 * Math.PI * R, deel = 107.6 / 115.8;
  return (
    <AbsoluteFill>
      <Foto src="ai/chip.jpg" duur={d} zoom={[1.1, 1.25]} pan={[0, 0, -30, -20]} donker={0.82} links={false} />
      <Rubriek tekst="FOLLOW THE MONEY" van={0} x={90} y={56} kleur={K.green} />
      <Kop tekst="DEMAND IS EXPLODING" van={t(28.0)} x={84} y={96} maat={86} />
      <Pijl d="M 1080 190 C 1130 170, 1170 120, 1220 70" van={t(28.9)} duur={30} kleur={K.green} dik={12} lengte={200} />
      <div style={{ position: "absolute", left: 90, top: 210, width: 1180, height: 820, opacity: kaart, background: "rgba(6,11,22,0.9)", border: `1px solid ${K.line}`, borderTop: `6px solid ${K.green}`, boxShadow: "0 40px 100px rgba(0,0,0,0.6)" }}>
        <div style={{ position: "absolute", left: 40, top: 22, font: `800 40px ${font.kop}`, color: K.ink }}>NVIDIA revenue per quarter</div>
        <div style={{ position: "absolute", left: 42, top: 74, font: `500 26px ${font.tekst}`, color: K.soft }}>US dollars · source: NVIDIA quarterly results</div>
        <div style={{ position: "absolute", left: 560, top: 18, background: "#fff", padding: "8px 14px", opacity: zacht((f - t(31.5)) / 14), transform: `scale(${0.8 + 0.2 * zacht((f - t(31.5)) / 14)})` }}><Img src={staticFile("ai/nvidia-rij.png")} style={{ height: 40 }} /></div>
        <svg width={1180} height={820} style={{ position: "absolute", left: 0, top: 0 }}>
          {[0, 50, 100].map((v) => { const y = base - 210 - (v / maxV) * H + 210 - 210; const yy = 830 - 210 - (v / maxV) * H; return (
            <g key={v}><line x1={150} x2={1140} y1={yy} y2={yy} stroke={K.line} strokeDasharray="6 10" /><text x={132} y={yy + 8} textAnchor="end" style={{ font: `500 24px ${font.cijfer}`, fill: K.soft }}>${v}B</text></g>); })}
          {[230, 560].map((x, i) => { const a = zacht((f - t(i ? 30.4 : 35.7)) / 14); return a > 0 ? <rect key={"p" + i} x={x} y={620 - 470 * 0.9} width={240} height={470 * 0.9} rx={10} fill="none" stroke={K.line} strokeWidth={3} strokeDasharray="10 10" strokeDashoffset={-f} opacity={a} /> : null; })}
          {staaf.map((b, i) => { const h = hoog(b.v, b.op); const y = 620 - h; const klaar = f - b.op > 20; return (
            <g key={i}>
              <rect x={b.x} y={y} width={240} height={h} rx={10} fill={b.k} />
              {i === 1 && dcA > 0 && <rect x={b.x} y={620 - dcH} width={240} height={dcH} rx={10} fill="#2f9e4a" stroke="#d8ff9a" strokeWidth={3} />}
              {klaar && <text x={b.x + 120} y={y - 20} textAnchor="middle" style={{ font: `900 56px ${font.cijfer}`, fill: K.ink }}>{b.tx}</text>}
              <text x={b.x + 120} y={662} textAnchor="middle" style={{ font: `800 30px ${font.kop}`, fill: K.ink }}>{b.l}</text>
              <text x={b.x + 120} y={694} textAnchor="middle" style={{ font: `500 22px ${font.tekst}`, fill: K.soft }}>{b.m}</text>
            </g>); })}
          {dcA > 0.6 && <g opacity={zacht((f - t(39.9)) / 14)}>
            <text x={680} y={620 - dcH / 2 - 8} textAnchor="middle" style={{ font: `800 28px ${font.kop}`, fill: "#fff" }}>Data center</text>
            <text x={680} y={620 - dcH / 2 + 32} textAnchor="middle" style={{ font: `900 38px ${font.cijfer}`, fill: "#fff" }}>$107.6B</text>
          </g>}
          {plus > 0 && <g opacity={plus}>
            <defs><marker id="pp3" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill={K.amber} /></marker></defs>
            <path d={`M 350 ${620 - hoog(57, staaf[0].op) - 80} Q 430 ${620 - hoog(115.8, staaf[1].op) - 10} ${540} ${620 - hoog(115.8, staaf[1].op) + 30}`} stroke={K.amber} strokeWidth={7} fill="none" markerEnd="url(#pp3)" />
            <rect x={300} y={620 - hoog(115.8, staaf[1].op) - 30} width={200} height={62} rx={31} fill={K.amber} />
            <text x={400} y={620 - hoog(115.8, staaf[1].op) + 12} textAnchor="middle" style={{ font: `900 38px ${font.cijfer}`, fill: "#111" }}>+103%</text>
          </g>}
          {/* verwachting: gestippelde staaf */}
          {verw > 0 && (() => { const h = (130 / maxV) * H * verw; return (
            <g>
              <rect x={890} y={620 - h} width={240} height={h} rx={10} fill={`rgba(255,181,71,${0.12 + 0.06 * Math.sin(f / 8)})`} stroke={K.amber} strokeWidth={4} strokeDasharray="14 10" strokeDashoffset={-f * 1.5} />
              {verw > 0.95 && <text x={1010} y={620 - h - 20} textAnchor="middle" style={{ font: `900 56px ${font.cijfer}`, fill: K.amber }}>~$130B</text>}
              <text x={1010} y={662} textAnchor="middle" style={{ font: `800 30px ${font.kop}`, fill: K.ink }}>Next quarter</text>
              <text x={1010} y={694} textAnchor="middle" style={{ font: `500 22px ${font.tekst}`, fill: K.soft }}>NVIDIA's own forecast</text>
            </g>); })()}
        </svg>
        <div style={{ position: "absolute", left: 42, bottom: 22, font: `400 20px ${font.tekst}`, color: K.soft }}>Source: NVIDIA results for Q3 fiscal 2026 (Nov 2025) and Q3 fiscal 2027 (Nov 17, 2026). Forecast = NVIDIA outlook, not a result.</div>
      </div>
      {/* rechts: welk deel komt uit datacenters */}
      <div style={{ position: "absolute", left: 1330, top: 210, width: 500, height: 820, opacity: paneel, background: "rgba(6,11,22,0.9)", border: `1px solid ${K.line}`, borderTop: `6px solid #2f9e4a` }}>
        <div style={{ position: "absolute", left: 34, top: 24, font: `800 36px ${font.kop}`, color: K.ink }}>Where the money</div>
        <div style={{ position: "absolute", left: 34, top: 66, font: `800 36px ${font.kop}`, color: K.ink }}>comes from</div>
        <svg width={500} height={520} style={{ position: "absolute", left: 0, top: 130 }}>
          <circle cx={250} cy={220} r={R} fill="none" stroke="#2a3550" strokeWidth={56} />
          <circle cx={250} cy={220} r={R} fill="none" stroke="#2f9e4a" strokeWidth={56} strokeDasharray={`${omtrek * deel * donut} ${omtrek}`} transform="rotate(-90 250 220)" />
          <text x={250} y={236} textAnchor="middle" opacity={donut} style={{ font: `900 64px ${font.cijfer}`, fill: K.ink }}>≈93%</text>
          <text x={250} y={410} textAnchor="middle" opacity={donut} style={{ font: `700 30px ${font.kop}`, fill: "#d8ff9a" }}>Data center chips</text>
          <text x={250} y={448} textAnchor="middle" opacity={donut} style={{ font: `500 24px ${font.tekst}`, fill: K.soft }}>$107.6B of $115.8B</text>
        </svg>
        <div style={{ position: "absolute", left: 34, bottom: 30, right: 30, opacity: donut, font: `500 24px ${font.tekst}`, color: K.soft, lineHeight: 1.35 }}>The other ≈7% includes chips for gaming, cars and other uses.</div>
      </div>
      <Bron tekst="Photo: Fritzchens Fritz (CC0)" />
    </AbsoluteFill>
  );
};

// ---------- 6. SLOT ----------
const Slot: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const tekst = zacht((f - t(47.3)) / 24);
  const kop = zacht((f - t(51.9)) / 16);
  return (
    <AbsoluteFill>
      <Foto src="ai/chip.jpg" duur={d} zoom={[1.0, 1.25]} pan={[0, 0, -50, -25]} donker={0.66} links={false} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 230, textAlign: "center", opacity: tekst * (1 - kop), font: `800 64px ${font.kop}`, color: K.ink }}>The companies behind these chips</div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 330, textAlign: "center", opacity: tekst * (1 - kop), font: `900 110px ${font.zwaar}`, color: K.cyan }}>matter more and more</div>
      <Kop tekst="THE FUTURE" van={t(51.9)} x={0} y={330} maat={190} midden />
      <Kop tekst="RUNS ON CHIPS" van={t(52.3)} x={0} y={530} maat={190} kleur={K.cyan} midden />
      <Bron tekst="Photo: Fritzchens Fritz (CC0)" />
    </AbsoluteFill>
  );
};

export const AIChips3: React.FC = () => {
  const scenes = [Intro, DeChip, Industrie, Wereld, Financieel, Slot];
  return (
    <AbsoluteFill style={{ background: K.bg }}>
      {scenes.map((S, i) => {
        const van = Math.max(0, B[i] - (i ? OVERLAP : 0)); const tot = B[i + 1]; const d = tot - van;
        return (
          <Sequence key={i} from={van} durationInFrames={d}>
            <Overgang duur={d} eerste={i === 0} laatste={i === scenes.length - 1}><S d={d} s={van} /></Overgang>
          </Sequence>
        );
      })}
      <Audio src={staticFile("ai/stem3.wav")} />
    </AbsoluteFill>
  );
};
