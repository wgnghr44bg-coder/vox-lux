import React, { useMemo } from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { font, zacht } from "../theme";
import { K } from "./Delen";
import W_ from "./data/woorden-stad.json";
import Z_ from "./data/zinnen-stad.json";
import S_ from "./data/stad.json";

// PROEF "BEURS-STAD" (22 nov 2026): de beurs als nachtelijke 3D-stad, één doorlopende camerabeweging, geen knippen.
// Elke toren = een bedrijf. Hoogte = slotkoers t.o.v. de top van 6 okt 2026 (echte dagkoersen, data/stad.json).
// Anthropic: hoogte t.o.v. de uitgifteprijs $83. Alleen stem, geen muziek of effecten.
const Z = Z_ as [number, number, string, string][];
const WD = W_ as [number, string, number, number][];
const S = S_ as unknown as Record<string, { okt6: number; nu: number; pct: number; reeks: number[]; data: string[] }>;
const kw = (zin: number, woord: string, na = 0) => {
  const w = WD.find((x) => x[0] === zin && x[1].toLowerCase().replace(/[^\w$%.]/g, "").startsWith(woord.toLowerCase()));
  return (w ? w[2] : Z[zin][0]) + na;   // in seconden
};
export const STAD_DUUR = Math.round((Z[Z.length - 1][1] + 2.8) * 30);

// vaste toevalsgetallen (elke render-tab exact hetzelfde beeld, geen flikkering)
const rng = (seed: number) => () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

type Toren = { id: string; naam: string; x: number; z: number; b: number; d: number; basis: number; kleur: string };
const TORENS: Toren[] = [
  { id: "nvda", naam: "NVIDIA", x: 0, z: 0, b: 2.6, d: 2.6, basis: 13, kleur: K.green },
  { id: "meta", naam: "Meta", x: -4.6, z: 1.4, b: 2.0, d: 2.0, basis: 9, kleur: "#4c8dff" },
  { id: "goog", naam: "Alphabet", x: -4.8, z: -3.4, b: 2.0, d: 2.0, basis: 9.5, kleur: "#f2c94c" },
  { id: "msft", naam: "Microsoft", x: 4.6, z: -3.4, b: 2.0, d: 2.0, basis: 10, kleur: K.cyan },
  { id: "amzn", naam: "Amazon", x: 4.8, z: 1.4, b: 2.0, d: 2.0, basis: 9, kleur: K.amber },
  { id: "avgo", naam: "Broadcom", x: 8.6, z: -1.0, b: 1.7, d: 1.7, basis: 8, kleur: "#ff6b6b" },
  { id: "tsla", naam: "Tesla", x: -8.6, z: -1.0, b: 1.7, d: 1.7, basis: 7.5, kleur: "#e0e0e0" },
];
const ANT = { x: 0, z: 5.6, b: 2.0, d: 2.0, hIpo: 6.5 };

// camera: één doorlopende vlucht (Catmull-Rom door sleutelpunten)
const SLEUTELS: [number, [number, number, number], [number, number, number]][] = [
  [0, [0, 34, 40], [0, 5, 0]],
  [kw(2, "on"), [6, 22, 28], [0, 6, 0]],
  [kw(3, "six"), [2, 18, 26], [0, 5, 0]],
  [kw(4, "meta", -0.6), [-11, 11, 15], [-4.6, 4, 0]],
  [kw(4, "alphabet", -0.4), [-12, 10, 6], [-4.8, 4, -2.5]],
  [kw(5, "tallest"), [7, 15, 15], [0, 6, 0]],
  [kw(6, "about"), [8, 11, 11], [0, 5, 0]],
  [kw(7, "giant", -0.3), [-4, 9, 22], [0, 4.5, 5]],
  [kw(8, "shot"), [-9, 9, 21], [0, 5.5, 5.6]],
  [kw(9, "sank"), [-10, 8, 20], [0, 4.8, 5.6]],
  [kw(10, "storm", -0.6), [0, 5, 27], [0, 11, 0]],
  [kw(11, "computers"), [2, 6, 29], [0, 12, 0]],
  [kw(12, "so"), [0, 26, 36], [0, 4, 0]],
  [Z[Z.length - 1][1] + 2.8, [0, 42, 48], [0, 2, 0]],
];

const torenTex = (seed: number, warm = "#ffd38a") => {
  const r = rng(seed); const cv = document.createElement("canvas"); cv.width = 128; cv.height = 128; const c = cv.getContext("2d")!;
  c.fillStyle = "#0b1220"; c.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { const q = r(); c.fillStyle = q < 0.42 ? warm : q < 0.55 ? "#9fd8ff" : "#172238"; c.fillRect(6 + i * 31, 8 + j * 31, 18, 20); }
  const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
};
const wolkTex = (seed: number) => {
  const r = rng(seed); const cv = document.createElement("canvas"); cv.width = 512; cv.height = 256; const c = cv.getContext("2d")!;
  for (let i = 0; i < 40; i++) { const x = 60 + r() * 392, y = 70 + r() * 120, rad = 40 + r() * 80; const g = c.createRadialGradient(x, y, 0, x, y, rad);
    g.addColorStop(0, "rgba(40,48,66,0.55)"); g.addColorStop(1, "rgba(40,48,66,0)"); c.fillStyle = g; c.fillRect(0, 0, 512, 256); }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
};

// toren-hoogte op tijd t (s): tot "six weeks later" op de top van 6 okt, dan in 2,6 s door de echte dagkoersen
const verloop = (t: number) => Math.min(1, Math.max(0, (t - kw(3, "six")) / 2.6));
const factor = (id: string, t: number) => {
  const s = S[id]; const p = verloop(t) * (s.reeks.length - 1); const i = Math.floor(p), fr = p - i;
  const v = i >= s.reeks.length - 1 ? s.reeks[s.reeks.length - 1] : s.reeks[i] * (1 - fr) + s.reeks[i + 1] * fr;
  return v / s.okt6;
};
const antPrijs = (t: number) => {
  const a = kw(7, "went"), b = kw(8, "shot"), c = kw(9, "sank");
  if (t < a) return 0;
  if (t < b) return 83 * zacht((t - a) / 1.2);
  if (t < c) return 83 + (115 - 83) * zacht((t - b) / 1.0);
  return 115 + (88.91 - 115) * zacht((t - c) / 1.2);
};

export const Stad: React.FC = () => {
  const f = useCurrentFrame(); const t = f / 30;
  const { width, height } = useVideoConfig();
  const tex = useMemo(() => ({ torens: TORENS.map((_, i) => torenTex(11 + i * 7)), ant: torenTex(97, "#ffe0b0"), vul: torenTex(5, "#c9a56a"), wolken: [wolkTex(3), wolkTex(8), wolkTex(13)] }), []);
  const vulling = useMemo(() => {   // achtergrondstad (vast patroon)
    const r = rng(42); const uit: { x: number; z: number; h: number; b: number }[] = [];
    for (let i = -11; i <= 11; i++) for (let j = -11; j <= 6; j++) {
      const x = i * 3.1 + (r() - 0.5), z = j * 3.1 + (r() - 0.5);
      if (Math.abs(x) < 11.5 && z > -6) continue;
      if (z > 7) continue;   // niets tussen camera en de torens
      if (r() < 0.25) continue;
      uit.push({ x, z, h: 1 + r() * r() * 7, b: 1 + r() * 1.2 });
    }
    return uit;
  }, []);
  const curve = useMemo(() => ({
    pos: new THREE.CatmullRomCurve3(SLEUTELS.map((s) => new THREE.Vector3(...s[1])), false, "centripetal"),
    doel: new THREE.CatmullRomCurve3(SLEUTELS.map((s) => new THREE.Vector3(...s[2])), false, "centripetal"),
  }), []);
  // tijd -> curve-parameter (stuksgewijs, zodat elk sleutelpunt op zijn woord valt)
  let k = 0; while (k < SLEUTELS.length - 2 && t > SLEUTELS[k + 1][0]) k++;
  const lok = Math.min(1, Math.max(0, (t - SLEUTELS[k][0]) / (SLEUTELS[k + 1][0] - SLEUTELS[k][0])));
  const u = (k + lok) / (SLEUTELS.length - 1);
  const cam = useMemo(() => new THREE.PerspectiveCamera(40, width / height, 0.1, 400), [width, height]);
  const cp = curve.pos.getPoint(u), cd = curve.doel.getPoint(u);
  cam.position.copy(cp); cam.lookAt(cd); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  const scherm = (x: number, y: number, z: number) => { const v = new THREE.Vector3(x, y, z).project(cam); return { x: (v.x + 1) / 2 * width, y: (1 - v.y) / 2 * height, voor: v.z < 1 }; };

  const storm = zacht((t - kw(10, "above")) / 2.5);
  const flits = [kw(10, "storm"), kw(10, "storm") + 1.7, kw(11, "computers") + 0.2].reduce((m, s) => Math.max(m, t >= s && t < s + 0.35 ? 1 - (t - s) / 0.35 : 0), 0);
  const hNv = TORENS[0].basis * factor("nvda", t); const verliesOp = kw(5, "lost");
  const antH = (antPrijs(t) / 83) * ANT.hIpo;
  const focus = t >= kw(5, "nvidia", -0.3) && t < kw(7, "then") ? "nvda" : t >= kw(4, "alphabet", -0.2) && t < kw(5, "tallest") ? "goog" : t >= kw(4, "meta", -0.2) && t < kw(4, "alphabet", -0.2) ? "meta" : "";

  // datum-teller
  const dIdx = Math.round(verloop(t) * (S.nvda.data.length - 1)); const datum = new Date(S.nvda.data[dIdx] + "T12:00");
  const datumTekst = datum.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }).toUpperCase();

  return (
    <AbsoluteFill style={{ background: "#03050b" }}>
      <ThreeCanvas width={width} height={height} camera={cam} gl={{ antialias: true }}>
        <color attach="background" args={[storm > 0 ? new THREE.Color("#03050b").lerp(new THREE.Color("#0a0d16"), storm) : new THREE.Color("#03050b")]} />
        <fog attach="fog" args={["#03050b", 30, 95]} />
        <ambientLight intensity={0.35 + flits * 1.6} color="#8fa8ff" />
        <directionalLight position={[-12, 30, 18]} intensity={0.55 * (1 - storm * 0.5)} color="#b9c8ff" />
        <pointLight position={[0, 30, 0]} intensity={flits * 900} color="#dfe8ff" distance={120} />
        <mesh rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[240, 240]} /><meshStandardMaterial color="#05080f" roughness={0.9} /></mesh>
        <gridHelper args={[140, 45, "#173257", "#0c1a30"]} position={[0, 0.01, 0]} />
        {vulling.map((v, i) => (
          <mesh key={i} position={[v.x, v.h / 2, v.z]}><boxGeometry args={[v.b, v.h, v.b]} />
            <meshStandardMaterial map={tex.vul} emissiveMap={tex.vul} emissive="#ffffff" emissiveIntensity={0.14} color="#1c2333" roughness={0.7} /></mesh>))}
        {TORENS.map((tw, i) => {
          const h = tw.basis * factor(tw.id, t); const tx = tex.torens[i]; tx.repeat.set(tw.b * 1.2, h * 1.2);
          const aan = focus === tw.id;
          return (<group key={tw.id}>
            <mesh position={[tw.x, h / 2, tw.z]}><boxGeometry args={[tw.b, h, tw.d]} />
              <meshStandardMaterial map={tx} emissiveMap={tx} emissive="#ffffff" emissiveIntensity={aan ? 1.1 : 0.75} color="#48577a" metalness={0.3} roughness={0.5} /></mesh>
            <mesh position={[tw.x, h + 0.06, tw.z]}><boxGeometry args={[tw.b + 0.12, 0.12, tw.d + 0.12]} /><meshBasicMaterial color={tw.kleur} /></mesh>
            {/* spookomtrek van de oude hoogte (top 6 okt) */}
            {verloop(t) > 0 && <lineSegments position={[tw.x, (tw.basis + h) / 2, tw.z]}>
              <edgesGeometry args={[new THREE.BoxGeometry(tw.b, Math.max(0.01, tw.basis - h), tw.d)]} />
              <lineBasicMaterial color={tw.id === "nvda" ? K.red : "#7d8db0"} transparent opacity={(tw.id === "nvda" && t >= verliesOp ? 0.95 : 0.35) * verloop(t)} /></lineSegments>}
          </group>);
        })}
        {/* Nvidia: het verloren deel valt als gloeiende blokjes uit elkaar */}
        {t >= verliesOp && Array.from({ length: 70 }).map((_, i) => {
          const r = rng(500 + i); const x0 = (r() - 0.5) * 2.5, z0 = (r() - 0.5) * 2.5, y0 = hNv + r() * (TORENS[0].basis - hNv);
          const d = t - verliesOp - r() * 1.5; if (d < 0) return null; const y = y0 - d * d * 2.2; if (y < 0) return null;
          return <mesh key={i} position={[x0 + d * (x0 * 0.4), y, z0 + d * (z0 * 0.4)]} rotation={[d * 2, d * 3, 0]}><boxGeometry args={[0.22, 0.22, 0.22]} /><meshBasicMaterial color={K.red} transparent opacity={Math.max(0, 1 - d / 3)} /></mesh>;
        })}
        {/* Anthropic: de nieuwe toren */}
        <mesh position={[ANT.x, 0.03, ANT.z]} rotation={[-Math.PI / 2, 0, 0]}><planeGeometry args={[ANT.b + 0.6, ANT.d + 0.6]} /><meshBasicMaterial color="#d97757" transparent opacity={0.25 + 0.2 * zacht((t - kw(7, "giant", -0.5)) / 1)} /></mesh>
        {antH > 0.02 && (() => { tex.ant.repeat.set(ANT.b * 1.2, antH * 1.2); return (<group>
          <mesh position={[ANT.x, antH / 2, ANT.z]}><boxGeometry args={[ANT.b, antH, ANT.d]} /><meshStandardMaterial map={tex.ant} emissiveMap={tex.ant} emissive="#ffffff" emissiveIntensity={0.95} color="#6b4a3e" roughness={0.5} /></mesh>
          <mesh position={[ANT.x, antH + 0.06, ANT.z]}><boxGeometry args={[ANT.b + 0.12, 0.12, ANT.d + 0.12]} /><meshBasicMaterial color="#d97757" /></mesh>
          <mesh position={[ANT.x, ANT.hIpo, ANT.z]}><boxGeometry args={[ANT.b + 1.2, 0.04, ANT.d + 1.2]} /><meshBasicMaterial color={K.cyan} transparent opacity={0.8} /></mesh>
        </group>); })()}
        {/* storm: donkere wolken boven de stad */}
        {storm > 0 && tex.wolken.map((w, i) => [0, 1, 2].map((j) => (
          <mesh key={i + "-" + j} position={[-26 + j * 24 + ((t * 0.6 + i * 7) % 10) - 5, 17 + i * 2.2, -8 + i * 6 - j * 3]} rotation={[0, 0, 0]}>
            <planeGeometry args={[34, 15]} /><meshBasicMaterial map={w} transparent opacity={storm * (0.9 + flits * 0.1)} depthWrite={false} color={flits > 0 ? "#cdd8ff" : "#ffffff"} /></mesh>)))}
      </ThreeCanvas>

      {/* labels boven de torens */}
      <svg width={width} height={height} style={{ position: "absolute" }}>
        {TORENS.map((tw, i) => {
          const a = zacht((t - kw(1, "every") - i * 0.15) / 0.5) * (t > kw(6, "about", -0.3) && t < kw(7, "then") ? 0.25 : t > kw(7, "then", -0.3) && t < kw(12, "so") ? 0.35 : 1) * (1 - zacht((t - kw(12, "so", -0.3)) / 0.5)); if (a <= 0) return null;
          const h = tw.basis * factor(tw.id, t); const p = scherm(tw.x, h + 0.5, tw.z); if (!p.voor) return null;
          const pct = (factor(tw.id, t) - 1) * 100; const aan = focus === tw.id; const sch = aan ? 1.35 : 1;
          const tekst = verloop(t) > 0 ? `${tw.naam}  ${pct <= -0.05 ? "−" : "+"}${Math.abs(pct).toFixed(1)}%` : tw.naam; const bw = (tekst.length * 15 + 34) * sch;
          return (<g key={tw.id} opacity={a}>
            <line x1={p.x} y1={p.y} x2={p.x} y2={p.y - 34 * sch} stroke={tw.kleur} strokeWidth={2} />
            <rect x={p.x - bw / 2} y={p.y - 34 * sch - 42 * sch} width={bw} height={42 * sch} rx={21 * sch} fill={aan ? tw.kleur : "rgba(6,11,22,0.86)"} stroke={tw.kleur} strokeWidth={2} />
            <text x={p.x} y={p.y - 34 * sch - 13 * sch} textAnchor="middle" style={{ font: `800 ${24 * sch}px ${font.kop}`, fill: aan ? "#0a0a0a" : K.ink }}>{tekst}</text>
          </g>);
        })}
        {/* Anthropic-labels: uitgifteprijs, dag 1, vrijdag */}
        {antH > 0.3 && t < kw(12, "so", 0.2) && (() => {
          const p = scherm(ANT.x + ANT.b / 2 + 0.2, antH, ANT.z); const pi = scherm(ANT.x - ANT.b / 2 - 0.6, ANT.hIpo, ANT.z);
          const prijs = antPrijs(t); const fase = t < kw(8, "shot") ? 0 : t < kw(9, "sank") ? 1 : 2;
          const tekst = fase === 0 ? `Anthropic  $${prijs.toFixed(0)}` : fase === 1 ? `Day 1  $${prijs.toFixed(0)}` : `Friday  $${prijs.toFixed(2)}`;
          const k2 = fase === 1 ? K.green : fase === 2 ? K.red : "#d97757";
          return (<g>
            <rect x={p.x + 20} y={p.y - 30} width={tekst.length * 17 + 40} height={58} rx={29} fill={k2} />
            <text x={p.x + 40} y={p.y + 10} style={{ font: `900 30px ${font.kop}`, fill: "#0a0a0a" }}>{tekst}</text>
            <text x={pi.x - 14} y={pi.y + 8} textAnchor="end" style={{ font: `700 24px ${font.kop}`, fill: K.cyan }}>IPO price $83</text>
          </g>);
        })()}
      </svg>

      {/* datum + uitleg */}
      <div style={{ position: "absolute", left: 70, top: 56, opacity: zacht((t - kw(2, "on", -0.3)) / 0.5) * (1 - zacht((t - kw(7, "then", -0.5)) / 0.5)) }}>
        <div style={{ font: `700 22px ${font.kop}`, color: K.soft, letterSpacing: 4 }}>{verloop(t) >= 1 ? "CLOSE" : verloop(t) > 0 ? "SIX WEEKS LATER" : "RECORD HIGH"}</div>
        <div style={{ font: `900 64px ${font.cijfer}`, color: verloop(t) > 0 ? K.red : K.ink }}>{datumTekst}</div>
      </div>
      <div style={{ position: "absolute", left: 70, bottom: 44, font: `500 21px ${font.tekst}`, color: "rgba(200,215,240,0.75)", opacity: zacht((t - kw(1, "every")) / 0.6) }}>
        Tower height = share price vs. the Oct 6 record (closing prices). Anthropic: vs. its $83 IPO price.</div>

      {/* Nvidia: groot verlies */}
      {(() => { const a = zacht((t - kw(6, "about", -0.2)) / 0.5) * (1 - zacht((t - kw(7, "then", -0.3)) / 0.5)); if (a <= 0) return null; return (
        <div style={{ position: "absolute", left: 0, right: 0, top: 80, padding: "30px 0", background: "linear-gradient(180deg, rgba(3,5,11,0) 0%, rgba(3,5,11,0.8) 25%, rgba(3,5,11,0.8) 75%, rgba(3,5,11,0) 100%)", textAlign: "center", opacity: a, transform: `scale(${0.94 + 0.06 * a})` }}>
          <div style={{ font: `900 120px ${font.zwaar}`, color: K.red, textShadow: "0 0 40px rgba(230,57,70,0.5)" }}>≈ $2.5 TRILLION</div>
          <div style={{ font: `800 48px ${font.kop}`, color: K.ink, letterSpacing: 6 }}>GONE IN SIX WEEKS</div></div>); })()}
      {/* storm-labels */}
      {[{ s: kw(11, "interest", -0.2), tx: "10-year rate > 5%", x: 330, y: 150 }, { s: kw(11, "computers", -0.2), tx: "Automatic selling", x: 1150, y: 210 }].map((l) => {
        const a = zacht((t - l.s) / 0.5) * (1 - zacht((t - kw(12, "so", -0.3)) / 0.5)); if (a <= 0) return null; return (
          <div key={l.tx} style={{ position: "absolute", left: l.x, top: l.y, opacity: a, transform: `translateY(${(1 - a) * -20}px)`, background: "rgba(8,12,22,0.85)", border: `2px solid ${K.amber}`, padding: "14px 28px", font: `900 46px ${font.zwaar}`, color: K.amber }}>{l.tx}</div>); })}
      {/* slotvraag */}
      {(() => { const a = zacht((t - kw(12, "so", -0.2)) / 0.6), b = zacht((t - kw(13, "or", -0.2)) / 0.6); if (a <= 0) return null; return (
        <div style={{ position: "absolute", left: 0, right: 0, top: 120, textAlign: "center" }}>
          <div style={{ font: `900 96px ${font.zwaar}`, color: K.ink, opacity: a, textShadow: "0 6px 30px #000" }}>FALLING APART?</div>
          <div style={{ font: `900 96px ${font.zwaar}`, color: K.green, opacity: b, textShadow: "0 6px 30px #000" }}>OR A CITY ON SALE?</div></div>); })()}
      {/* flits van de bliksem over het hele beeld */}
      {flits > 0 && <AbsoluteFill style={{ background: `rgba(210,225,255,${flits * 0.22})` }} />}
      <AbsoluteFill style={{ background: "#000", opacity: interpolate(f, [STAD_DUUR - 24, STAD_DUUR], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }} />
      <Audio src={staticFile("ai/stem-stad.wav")} />
    </AbsoluteFill>
  );
};
