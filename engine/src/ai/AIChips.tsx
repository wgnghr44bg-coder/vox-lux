import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, interpolate } from "remotion";
import { font, zacht, inUit } from "../theme";
import { K, sec, clamp, Foto, Kop, Rubriek, Paneel, Bron, Ticker, Pijl, Overgang } from "./Delen";
import { Chip3D } from "./Chip3D";

// 30-SECONDEN DEMO "HOW AI CHIPS POWER THE FUTURE" (22 nov 2026). Tijden = woordtijden van de stem (Whisper), in seconden.
// Scènes beginnen op hun zin; elke visuele stap op zijn kernwoord.
export const AI_DUUR = 900;
const B = [0, sec(6.85), sec(12.27), sec(17.87), sec(23.49), AI_DUUR]; // scènegrenzen
const OVERLAP = 10;

// ---------- SCÈNE 1: INTRO ----------
const Intro: React.FC<{ d: number; s: number }> = ({ d }) => {
  const f = useCurrentFrame();
  const kaart = zacht((f - sec(3.5)) / 16);
  const ring = zacht((f - sec(5.8)) / 14);
  return (
    <AbsoluteFill>
      <Foto src="ai/dc.jpg" duur={d} zoom={[1.25, 1.05]} pan={[-30, 10, 20, -10]} donker={0.45} />
      <Rubriek tekst="AI SPECIAL REPORT" van={4} x={110} y={150} />
      <Kop tekst="THE AI" van={sec(0.4)} x={104} y={220} maat={150} />
      <Kop tekst="REVOLUTION" van={sec(0.75)} x={104} y={375} maat={150} kleur={K.cyan} />
      <Kop tekst="How AI chips power the future" van={sec(1.6)} x={110} y={560} maat={46} gewicht={600} kleur={K.soft} />
      {/* rechts: echte foto van AI-chipborden, met markering van de chip */}
      <div style={{ position: "absolute", right: 90, top: 250, width: 560, opacity: kaart, transform: `translateX(${(1 - kaart) * 80}px)`, boxShadow: "0 30px 80px rgba(0,0,0,0.7)", border: `1px solid ${K.line}` }}>
        <Img src={staticFile("ai/gb200.jpg")} style={{ width: 560, height: 380, objectFit: "cover", display: "block", transform: `scale(${1.05 + 0.1 * inUit((f - sec(3.5)) / (d - sec(3.5)))})` }} />
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "12px 18px", background: "linear-gradient(transparent, rgba(5,8,15,0.95))", font: `700 26px ${font.kop}`, color: K.ink }}>AI accelerator boards · NVIDIA GB200</div>
        {ring > 0 && <div style={{ position: "absolute", left: 90, top: 104, width: 135, height: 100, border: `4px solid ${K.amber}`, borderRadius: 10, opacity: ring, transform: `scale(${1.4 - 0.4 * ring})`, boxShadow: `0 0 30px ${K.amber}` }} />}
      </div>
      {ring > 0 && <div style={{ position: "absolute", right: 90, top: 660, opacity: ring, font: `800 34px ${font.kop}`, color: K.amber, textAlign: "right" }}>The AI chip ▸</div>}
      <Paneel van={sec(3.6)} x={110} y={690} w={760} kleur={K.amber} titel="Behind every AI breakthrough" tekst="Specialised processors do the heavy work: training and running AI models." />
      <Bron tekst="Photos: G. Rocher / IFREMER (CC BY 4.0) · Geekerwan (CC BY 3.0)" />
    </AbsoluteFill>
  );
};

// ---------- SCÈNE 2: DE CHIP (exploded view) ----------
const DeChip: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 40% 50%, #10203a 0%, #05080F 70%)" }}>
      <Chip3D duur={d} openOp={t(8.9)} labelsOp={[t(9.2), t(9.5), t(9.8), t(10.1), t(10.4)]} stroomOp={t(10.5)} />
      <Rubriek tekst="INSIDE THE MACHINE" van={4} x={110} y={110} kleur={K.cyan} />
      <Kop tekst="THE AI PROCESSOR" van={6} x={104} y={160} maat={84} />
      <Paneel van={t(10.6)} x={110} y={760} w={560} kleur={K.cyan} titel="Billions of calculations" tekst="Memory feeds data to the compute die, which works on it in parallel." />
      <div style={{ position: "absolute", left: 110, top: 270, font: `600 30px ${font.kop}`, color: K.soft, opacity: zacht((f - t(9.0)) / 12) }}>One package, many layers</div>
    </AbsoluteFill>
  );
};

// ---------- SCÈNE 3: DE INDUSTRIE (split screen + keten) ----------
const Industrie: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const split = zacht(f / 16);
  const stappen = [
    { naam: "Chip design", wie: "NVIDIA", op: t(13.4), k: K.green },
    { naam: "Wafer fabrication", wie: "TSMC", op: t(15.0), k: K.red },
    { naam: "Advanced packaging", wie: "TSMC", op: t(16.3), k: K.red },
    { naam: "AI servers", wie: "data centers", op: t(17.1), k: K.cyan },
  ];
  return (
    <AbsoluteFill style={{ background: K.bg }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 960 * split, height: 700, overflow: "hidden" }}>
        <Foto src="ai/dgx.jpg" duur={d} zoom={[1.15, 1.0]} donker={0.5} links={false} stijl={{ width: 960 }} />
      </div>
      <div style={{ position: "absolute", right: 0, top: 0, width: 960 * split, height: 700, overflow: "hidden" }}>
        <Foto src="ai/fab.jpg" duur={d} zoom={[1.0, 1.15]} donker={0.5} links={false} stijl={{ width: 960, left: "auto", right: 0 }} />
      </div>
      <div style={{ position: "absolute", left: 958, top: 0, width: 4, height: 700, background: K.ink, opacity: split }} />
      {/* NVIDIA */}
      <div style={{ position: "absolute", left: 90, top: 120, opacity: zacht((f - t(12.9)) / 12) }}>
        <div style={{ background: "#fff", padding: "14px 22px", display: "inline-block" }}><Img src={staticFile("ai/nvidia-logo.png")} style={{ height: 110 }} /></div>
        <div style={{ font: `900 92px ${font.zwaar}`, color: K.ink, marginTop: 20 }}>DESIGNS</div>
        <div style={{ font: `500 32px ${font.tekst}`, color: K.soft }}>the AI chips</div>
      </div>
      {/* TSMC */}
      <div style={{ position: "absolute", left: 1050, top: 120, opacity: zacht((f - t(15.6)) / 12) }}>
        <div style={{ background: "#fff", padding: "26px 30px", display: "inline-block" }}><Img src={staticFile("ai/tsmc-logo.png")} style={{ height: 70 }} /></div>
        <div style={{ font: `900 92px ${font.zwaar}`, color: K.ink, marginTop: 20 }}>MANUFACTURES</div>
        <div style={{ font: `500 32px ${font.tekst}`, color: K.soft }}>the advanced chips</div>
      </div>
      {/* keten onderaan */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 700, height: 330, background: "linear-gradient(#0a1222, #05080F)", borderTop: `1px solid ${K.line}` }} />
      <div style={{ position: "absolute", left: 110, top: 728, font: `800 24px ${font.kop}`, color: K.soft, letterSpacing: 4 }}>THE AI CHIP SUPPLY CHAIN</div>
      {stappen.map((st, i) => {
        const a = zacht((f - st.op) / 12); const x = 110 + i * 440;
        return (
          <React.Fragment key={i}>
            <div style={{ position: "absolute", left: x, top: 790, width: 330, height: 150, opacity: a, transform: `translateY(${(1 - a) * 20}px)`, background: K.panel, border: `1px solid ${K.line}`, borderLeft: `6px solid ${st.k}`, padding: "20px 22px", boxSizing: "border-box" }}>
              <div style={{ font: `500 22px ${font.tekst}`, color: K.soft }}>Step {i + 1}</div>
              <div style={{ font: `800 32px ${font.kop}`, color: K.ink, marginTop: 4 }}>{st.naam}</div>
              <div style={{ font: `700 24px ${font.kop}`, color: st.k, marginTop: 6 }}>{st.wie}</div>
            </div>
            {i < 3 && <Pijl d={`M ${x + 345} 865 L ${x + 425} 865`} van={stappen[i + 1].op - 6} duur={8} kleur={K.ink} dik={5} lengte={90} />}
          </React.Fragment>
        );
      })}
      <Bron tekst="Photos: Pokiiri (CC BY-SA 4.0) · 4300streetcar (CC BY 4.0)" />
    </AbsoluteFill>
  );
};

// ---------- SCÈNE 4: WERELDWIJDE IMPACT (kaart) ----------
const MW = 1920 * 1.15, MH = MW / 2; // kaart groter dan het scherm, camera beweegt erover
const plek = (lat: number, lon: number) => ({ x: ((lon + 180) / 360) * MW, y: ((90 - lat) / 180) * MH });
const TAIWAN = plek(24.8, 121.0);
const HUBS = [
  { naam: "N. Virginia", ...plek(39.0, -77.5) }, { naam: "Oregon", ...plek(45.6, -121.2) }, { naam: "Dublin", ...plek(53.3, -6.3) },
  { naam: "Amsterdam", ...plek(52.4, 4.9) }, { naam: "Mumbai", ...plek(19.1, 72.9) }, { naam: "Singapore", ...plek(1.35, 103.8) }, { naam: "Tokyo", ...plek(35.7, 139.7) },
];
const Wereld: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const p = inUit(f / d);
  const camX = -200 + 60 * p, camY = 60 + 20 * p, sc = 1.06 - 0.06 * p;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 55% 40%, #0d1b33 0%, #04070d 75%)", overflow: "hidden" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: MW, height: MH, transform: `translate(${camX}px, ${camY}px) scale(${sc})`, transformOrigin: "0 0" }}>
        <Img src={staticFile("ai/wereld-stijl.png")} style={{ width: MW, height: MH, opacity: 0.95 }} />
        <svg width={MW} height={MH} style={{ position: "absolute", left: 0, top: 0 }}>
          {HUBS.map((h, i) => {
            const st = t(18.5) + i * 4; const a = zacht((f - st) / 18); if (a <= 0) return null;
            const mx = (TAIWAN.x + h.x) / 2, my = Math.min(TAIWAN.y, h.y) - Math.abs(TAIWAN.x - h.x) * 0.22;
            const dd = `M ${TAIWAN.x} ${TAIWAN.y} Q ${mx} ${my} ${h.x} ${h.y}`;
            const puls = f > t(22.4) ? 0.5 + 0.5 * Math.sin((f - i * 3) / 4) : 1;
            return (
              <g key={i}>
                <path d={dd} stroke={K.cyan} strokeWidth={4} fill="none" strokeDasharray={3000} strokeDashoffset={3000 * (1 - a)} opacity={0.85} style={{ filter: `drop-shadow(0 0 6px ${K.cyan})` }} />
                {a >= 1 && <circle cx={h.x} cy={h.y} r={12 + 10 * (1 - puls)} fill="none" stroke={K.cyan} strokeWidth={3} opacity={puls} />}
                {a >= 1 && <circle cx={h.x} cy={h.y} r={9} fill={K.ink} />}
                {a >= 1 && <text x={["Dublin", "Tokyo"].includes(h.naam) ? h.x - 18 : h.x + 18} y={h.y - 14} textAnchor={["Dublin", "Tokyo"].includes(h.naam) ? "end" : "start"} style={{ font: `700 28px ${font.kop}`, fill: K.ink }}>{h.naam}</text>}
              </g>
            );
          })}
          <circle cx={TAIWAN.x} cy={TAIWAN.y} r={16} fill={K.red} style={{ filter: `drop-shadow(0 0 12px ${K.red})` }} />
          <text x={TAIWAN.x - 30} y={TAIWAN.y + 74} textAnchor="end" style={{ font: `800 32px ${font.kop}`, fill: K.ink }}>Taiwan · chips made</text>
        </svg>
      </div>
      <Rubriek tekst="GLOBAL IMPACT" van={4} x={110} y={110} kleur={K.cyan} />
      <Kop tekst="CHIPS POWER THE WORLD" van={6} x={104} y={160} maat={78} />
      <div style={{ position: "absolute", left: 110, top: 258, font: `500 26px ${font.tekst}`, color: K.soft, opacity: zacht((f - t(18.6)) / 12) }}>Examples of major data center hubs</div>
      <Paneel van={t(18.9)} x={110} y={730} w={520} kleur={K.cyan} titel="Data centers" tekst="Racks of AI servers" />
      <Paneel van={t(19.8)} x={700} y={730} w={520} kleur={K.green} titel="AI systems" tekst="Chatbots, models, research" />
      <Paneel van={t(21.4)} x={1290} y={730} w={520} kleur={K.amber} titel="Everyday technology" tekst="Search, phones, cars, cloud apps" />
      <Bron tekst="Map: public domain (CIA World Factbook)" />
    </AbsoluteFill>
  );
};

// ---------- SCÈNE 5: CONCLUSIE ----------
const Slot: React.FC<{ d: number; s: number }> = ({ d, s }) => {
  const t = (x: number) => sec(x) - s;
  const f = useCurrentFrame();
  const kringA = zacht((f - t(23.9)) / 16);
  const nodes = [{ n: "Chip design", k: K.green }, { n: "Manufacturing", k: K.red }, { n: "Data centers", k: K.cyan }, { n: "AI apps", k: K.amber }];
  const cx = 560, cy = 560, R = 250;
  const balk = zacht((f - t(26.4)) / 18);
  const eind = zacht((f - t(28.3)) / 14);
  return (
    <AbsoluteFill>
      <Foto src="ai/chip.jpg" duur={d} zoom={[1.0, 1.18]} pan={[0, 0, -40, -20]} donker={0.72} links={false} />
      {/* ecosysteem rond de chip */}
      <svg width={1920} height={1080} style={{ position: "absolute" }} opacity={kringA * (1 - eind * 0.85)}>
        <circle cx={cx} cy={cy} r={R} fill="none" stroke={K.line} strokeWidth={2} strokeDasharray="8 10" />
        <circle cx={cx} cy={cy} r={110} fill={K.panel} stroke={K.ink} strokeWidth={3} />
        <text x={cx} y={cy + 12} textAnchor="middle" style={{ font: `900 40px ${font.zwaar}`, fill: K.ink }}>AI CHIPS</text>
        {nodes.map((nd, i) => {
          const a = zacht((f - t(24.1) - i * 6) / 12); const hk = -Math.PI / 2 + (i * Math.PI) / 2 + f * 0.004;
          const x = cx + Math.cos(hk) * R, y = cy + Math.sin(hk) * R;
          return (
            <g key={i} opacity={a}>
              <line x1={cx + Math.cos(hk) * 112} y1={cy + Math.sin(hk) * 112} x2={x} y2={y} stroke={nd.k} strokeWidth={3} />
              <circle cx={x} cy={y} r={16} fill={nd.k} />
              <rect x={x - 120} y={y + 24} width={240} height={50} rx={25} fill={K.panel} stroke={nd.k} />
              <text x={x} y={y + 58} textAnchor="middle" style={{ font: `700 26px ${font.kop}`, fill: K.ink }}>{nd.n}</text>
            </g>
          );
        })}
      </svg>
      {/* financieel: omzet NVIDIA (bron: persbericht 17 nov 2026) */}
      <div style={{ position: "absolute", right: 110, top: 220, width: 620, opacity: balk * (1 - eind * 0.85), background: K.panel, border: `1px solid ${K.line}`, borderTop: `3px solid ${K.green}`, padding: "22px 28px 18px" }}>
        <div style={{ font: `800 30px ${font.kop}`, color: K.ink }}>NVIDIA quarterly revenue</div>
        <div style={{ font: `400 22px ${font.tekst}`, color: K.soft }}>Q3 fiscal 2027 vs. a year earlier</div>
        <svg width={560} height={300}>
          {[{ l: "A year earlier", v: 115.8 / 2.03, k: "#5a6b88", t: "≈ $57B" }, { l: "Q3 FY2027", v: 115.8, k: K.green, t: "$115.8B" }].map((b, i) => {
            const h = (b.v / 115.8) * 210 * zacht((f - t(26.6) - i * 8) / 16);
            return (<g key={i}><rect x={70 + i * 250} y={240 - h} width={150} height={h} rx={8} fill={b.k} />
              <text x={145 + i * 250} y={232 - h} textAnchor="middle" style={{ font: `800 32px ${font.cijfer}`, fill: K.ink }}>{h > 30 ? b.t : ""}</text>
              <text x={145 + i * 250} y={280} textAnchor="middle" style={{ font: `500 22px ${font.tekst}`, fill: K.soft }}>{b.l}</text></g>);
          })}
        </svg>
        <div style={{ font: `900 46px ${font.cijfer}`, color: K.green, marginTop: -6, opacity: zacht((f - t(27.4)) / 12) }}>+103%</div>
        <div style={{ font: `400 16px ${font.tekst}`, color: K.soft, marginTop: 4 }}>Source: NVIDIA results, Nov 17, 2026</div>
      </div>
      {/* slotkop */}
      <AbsoluteFill style={{ background: `rgba(3,6,12,${0.55 * eind})` }} />
      <Kop tekst="THE FUTURE" van={t(28.3)} x={0} y={360} maat={150} midden />
      <Kop tekst="RUNS ON CHIPS" van={t(28.6)} x={0} y={520} maat={150} kleur={K.cyan} midden />
      <Bron tekst="Photo: Fritzchens Fritz (CC0)" />
    </AbsoluteFill>
  );
};

export const AIChips: React.FC = () => {
  const scenes = [Intro, DeChip, Industrie, Wereld, Slot];
  return (
    <AbsoluteFill style={{ background: K.bg }}>
      {scenes.map((S, i) => {
        const van = Math.max(0, B[i] - (i ? OVERLAP : 0)); const tot = B[i + 1]; const d = tot - van;
        return (
          <Sequence key={i} from={van} durationInFrames={d}>
            <Overgang duur={d} laatste={i === scenes.length - 1}><S d={d} s={van} /></Overgang>
          </Sequence>
        );
      })}
      <Ticker tekst="HOW AI CHIPS POWER THE FUTURE  •  ARTIFICIAL INTELLIGENCE  •  SEMICONDUCTORS  •  DATA CENTERS  •  CHIP DESIGN & MANUFACTURING" />
      <Audio src={staticFile("ai/stem.wav")} />
    </AbsoluteFill>
  );
};
