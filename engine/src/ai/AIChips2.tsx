import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, interpolate } from "remotion";
import { font, zacht, inUit } from "../theme";
import { K, sec, clamp, Foto, Kop, Rubriek, Paneel, Bron, Pijl, Overgang } from "./Delen";
import { Chip3D } from "./Chip3D";

// v2 (22 nov 2026): grotere beelden (60-80% van het scherm), duidelijkere uitleg, geen ticker, geen zwart eerste beeld,
// elke scène loopt logisch door naar de volgende: datacenter -> chipbord -> inzoomen op de chip -> wie maakt hem -> waar draait hij -> waarom belangrijk.
export const AI2_DUUR = 900;
const B = [0, sec(6.85), sec(12.27), sec(17.87), sec(23.49), AI2_DUUR];
const OVERLAP = 10;

// ---------- 1. INTRO: datacenter -> het chipbord groeit tot bijna het hele beeld -> inzoomen op de chip ----------
const Intro: React.FC<{ d: number; s: number }> = ({ d }) => {
  const f = useCurrentFrame();
  const bord = zacht((f - sec(3.2)) / 22);                 // chipbord komt in beeld op "breakthrough"
  const kopWeg = zacht((f - sec(3.2)) / 14);
  const mark = zacht((f - sec(5.6)) / 12);                  // markering op "technology"
  const inzoom = inUit((f - sec(6.15)) / (d - sec(6.15)));  // naar de chip toe, overgang naar scène 2
  const bx = 1920 - 90 - 1360 * bord - 0 * (1 - bord), bw = 1360, bh = 765;
  return (
    <AbsoluteFill>
      <Foto src="ai/dc.jpg" duur={d} zoom={[1.18, 1.04]} pan={[-30, 10, 20, -10]} donker={0.4} />
      <div style={{ opacity: 1 - kopWeg, transform: `translateY(${-kopWeg * 40}px)` }}>
        <Rubriek tekst="AI SPECIAL REPORT" van={0} x={110} y={170} />
        <Kop tekst="THE AI" van={sec(0.3)} x={104} y={240} maat={200} />
        <Kop tekst="REVOLUTION" van={sec(0.65)} x={104} y={445} maat={200} kleur={K.cyan} />
        <Kop tekst="How AI chips power the future" van={sec(1.4)} x={110} y={690} maat={58} gewicht={600} kleur={K.soft} />
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
      <Chip3D dx={-250} duur={d} zoomVan={135} zoomTot={175} openOp={t(8.6)} labelsOp={[t(8.9), t(9.3), t(9.7), t(10.1), t(10.5)]} stroomOp={t(10.6)} />
      <Rubriek tekst="INSIDE THE PROCESSOR" van={0} x={110} y={90} kleur={K.cyan} />
      <Kop tekst="ONE CHIP, MANY LAYERS" van={4} x={104} y={135} maat={82} />
      <Paneel van={t(10.8)} x={110} y={820} w={780} kleur={K.amber} titel="Billions of calculations" tekst="Memory feeds data to thousands of cores, which work on it at the same time." />
    </AbsoluteFill>
  );
};

// ---------- 3. DE INDUSTRIE: wie ontwerpt, wie maakt ----------
const Industrie: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const split = zacht(f / 14);
  const stappen = [
    { naam: "Chip design", wie: "NVIDIA", op: t(13.4), k: K.green },
    { naam: "Wafer fabrication", wie: "TSMC", op: t(15.0), k: K.red },
    { naam: "Advanced packaging", wie: "TSMC", op: t(16.3), k: K.red },
    { naam: "AI servers", wie: "Data centers", op: t(17.1), k: K.cyan },
  ];
  const bolU = Math.max(0, Math.min(3, (f - t(13.6)) / sec(1.2)));   // lichtpunt reist langs de keten
  return (
    <AbsoluteFill style={{ background: K.bg }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 960 * split, height: 760, overflow: "hidden" }}>
        <Foto src="ai/dgx.jpg" duur={d} zoom={[1.18, 1.0]} donker={0.45} links={false} stijl={{ width: 960 }} />
      </div>
      <div style={{ position: "absolute", right: 0, top: 0, width: 960 * split, height: 760, overflow: "hidden" }}>
        <Foto src="ai/fab.jpg" duur={d} zoom={[1.0, 1.18]} donker={0.45} links={false} stijl={{ width: 960, left: "auto", right: 0 }} />
      </div>
      <div style={{ position: "absolute", left: 957, top: 0, width: 6, height: 760, background: K.ink, opacity: split }} />
      <div style={{ position: "absolute", left: 90, top: 90, opacity: zacht((f - t(12.9)) / 10) }}>
        <div style={{ background: "#fff", padding: "16px 26px", display: "inline-block", boxShadow: "0 10px 40px rgba(0,0,0,0.5)" }}><Img src={staticFile("ai/nvidia-logo.png")} style={{ height: 150 }} /></div>
        <div style={{ font: `900 120px ${font.zwaar}`, color: K.ink, marginTop: 24, lineHeight: 1 }}>DESIGNS</div>
        <div style={{ font: `600 40px ${font.kop}`, color: K.soft, marginTop: 10 }}>the AI chips</div>
      </div>
      <div style={{ position: "absolute", left: 1050, top: 90, opacity: zacht((f - t(15.5)) / 10) }}>
        <div style={{ background: "#fff", padding: "38px 40px", display: "inline-block", boxShadow: "0 10px 40px rgba(0,0,0,0.5)" }}><Img src={staticFile("ai/tsmc-logo.png")} style={{ height: 96 }} /></div>
        <div style={{ font: `900 120px ${font.zwaar}`, color: K.ink, marginTop: 24, lineHeight: 1 }}>MAKES</div>
        <div style={{ font: `600 40px ${font.kop}`, color: K.soft, marginTop: 10 }}>the advanced chips</div>
      </div>
      {/* ontwerp gaat van NVIDIA naar de fabriek van TSMC */}
      <Pijl d="M 700 610 C 860 560, 1060 560, 1220 610" van={t(14.7)} duur={14} kleur={K.amber} dik={8} lengte={600} />
      {f > t(15.1) && <div style={{ position: "absolute", left: 760, top: 500, opacity: zacht((f - t(15.1)) / 10), background: K.amber, color: "#111", font: `800 30px ${font.kop}`, padding: "8px 18px" }}>chip designs → factory</div>}
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
      {f > t(13.6) && <div style={{ position: "absolute", left: 90 + 187 + bolU * 445 - 12, top: 1018, width: 24, height: 24, borderRadius: 12, background: K.amber, boxShadow: `0 0 24px ${K.amber}` }} />}
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
            const st = t(18.3) + i * 5; const a = zacht((f - st) / 16); if (a <= 0) return null;
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
      <div style={{ position: "absolute", left: 90, top: 226, font: `600 30px ${font.kop}`, color: K.soft, opacity: zacht((f - t(18.4)) / 10) }}>Examples of major data center hubs</div>
      <Paneel van={t(18.9)} x={90} y={850} w={560} kleur={K.cyan} titel="Data centers" tekst="Huge halls of AI servers" />
      <Paneel van={t(19.8)} x={680} y={850} w={560} kleur={K.green} titel="AI systems" tekst="Train and run AI models" />
      <Paneel van={t(21.4)} x={1270} y={850} w={560} kleur={K.amber} titel="Technology worldwide" tekst="Cloud apps, search, phones, cars" />
      <Bron tekst="Map: public domain (CIA World Factbook)" />
    </AbsoluteFill>
  );
};

// ---------- 5. CONCLUSIE: de vraag groeit -> omzet verdubbeld (geverifieerd) -> slotkop ----------
const Slot: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const kaart = zacht((f - t(23.8)) / 14);
  const eind = zacht((f - t(27.85)) / 8);                   // grafiek eerst weg, dan pas de slotkop
  const bars = [
    { l: "Q3 fiscal 2026", m: "Aug – Oct 2025", v: 57.0, k: "#62738f", tx: "$57.0B", op: t(25.4) },
    { l: "Q3 fiscal 2027", m: "Aug – Oct 2026", v: 115.8, k: K.green, tx: "$115.8B", op: t(26.3) },
  ];
  const H = 430, base = 790, maxV = 115.8;
  const top = (b: typeof bars[0]) => base - (b.v / maxV) * H * zacht((f - b.op) / 18);
  const groei = zacht((f - t(27.4)) / 14);
  return (
    <AbsoluteFill>
      <Foto src="ai/chip.jpg" duur={d} zoom={[1.05, 1.3]} pan={[0, 0, -60, -30]} donker={0.74 - 0.2 * eind} links={false} />
      <div style={{ position: "absolute", left: 90, top: 70, width: 1240, height: 940, opacity: kaart * (1 - eind), transform: `translateY(${(1 - kaart) * 30}px)`, background: "rgba(6,11,22,0.88)", border: `1px solid ${K.line}`, borderTop: `6px solid ${K.green}`, boxShadow: "0 40px 100px rgba(0,0,0,0.6)" }}>
        <div style={{ position: "absolute", left: 44, top: 30, font: `900 54px ${font.zwaar}`, color: K.ink }}>Demand for AI chips is booming</div>
        <div style={{ position: "absolute", left: 46, top: 102, font: `500 32px ${font.tekst}`, color: K.soft }}>NVIDIA revenue in one quarter, in US dollars</div>
        <div style={{ position: "absolute", left: 46, top: 152, display: "flex", gap: 28, font: `600 24px ${font.kop}`, color: K.soft }}>
          <span><span style={{ display: "inline-block", width: 18, height: 18, background: "#62738f", marginRight: 10 }} />a year earlier</span>
          <span><span style={{ display: "inline-block", width: 18, height: 18, background: K.green, marginRight: 10 }} />latest quarter</span>
        </div>
        <svg width={1240} height={940} style={{ position: "absolute", left: 0, top: 0 }}>
          {[0, 50, 100].map((v) => { const y = base - (v / maxV) * H; return (<g key={v}><line x1={150} x2={1180} y1={y} y2={y} stroke={K.line} strokeDasharray="6 10" /><text x={130} y={y + 8} textAnchor="end" style={{ font: `500 24px ${font.cijfer}`, fill: K.soft }}>${v}B</text></g>); })}
          {bars.map((b, i) => { const x = 260 + i * 460, y = top(b); const klaar = f - b.op > 14; return (
            <g key={i}>
              <rect x={x} y={y} width={300} height={base - y} rx={10} fill={b.k} />
              {klaar && <text x={x + 150} y={y - 22} textAnchor="middle" style={{ font: `900 64px ${font.cijfer}`, fill: K.ink }}>{b.tx}</text>}
              <text x={x + 150} y={base + 46} textAnchor="middle" style={{ font: `800 30px ${font.kop}`, fill: K.ink }}>{b.l}</text>
              <text x={x + 150} y={base + 80} textAnchor="middle" style={{ font: `500 24px ${font.tekst}`, fill: K.soft }}>{b.m}</text>
            </g>); })}
          {groei > 0 && (() => { const y1 = top(bars[0]) - 90, y2 = top(bars[1]) - 100; return (
            <g opacity={groei}>
              <defs><marker id="gp" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill={K.amber} /></marker></defs>
              <path d={`M 470 ${y1 + 40} Q 560 ${y2 + 10} ${680 + 30 * groei} ${y2 + 90}`} stroke={K.amber} strokeWidth={7} fill="none" markerEnd="url(#gp)" />
              <rect x={455} y={(y1 + y2) / 2 + 40} width={230} height={66} rx={33} fill={K.amber} />
              <text x={570} y={(y1 + y2) / 2 + 86} textAnchor="middle" style={{ font: `900 42px ${font.cijfer}`, fill: "#111" }}>+103%</text>
            </g>); })()}
        </svg>
        <div style={{ position: "absolute", left: 46, bottom: 22, font: `400 22px ${font.tekst}`, color: K.soft }}>Source: NVIDIA quarterly results (Nov 2025, Nov 17 2026)</div>
      </div>
      <div style={{ position: "absolute", left: 1380, top: 330, width: 450, opacity: kaart * (1 - eind) }}>
        <div style={{ font: `800 40px ${font.kop}`, color: K.ink, lineHeight: 1.15 }}>The companies behind these chips</div>
        <div style={{ font: `900 64px ${font.zwaar}`, color: K.cyan, marginTop: 14, lineHeight: 1.05 }}>matter more and more</div>
      </div>
      <Kop tekst="THE FUTURE" van={t(28.2)} x={0} y={330} maat={190} midden />
      <Kop tekst="RUNS ON CHIPS" van={t(28.5)} x={0} y={530} maat={190} kleur={K.cyan} midden />
      <Bron tekst="Photo: Fritzchens Fritz (CC0)" />
    </AbsoluteFill>
  );
};

export const AIChips2: React.FC = () => {
  const scenes = [Intro, DeChip, Industrie, Wereld, Slot];
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
      <Audio src={staticFile("ai/stem.wav")} />
    </AbsoluteFill>
  );
};
