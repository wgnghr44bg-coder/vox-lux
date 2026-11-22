import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { zacht, inUit, font } from "../theme";
import { K } from "./Delen";

// EXPLODED VIEW van een AI-processor (opbouw zoals moderne AI-GPU's): koeldeksel, rekenchip (GPU-die), HBM-geheugen,
// silicium-interposer, package-substraat. v2 (22 nov): groter, realistischere oppervlakken (procedurele texturen),
// het actieve onderdeel licht op, pijlen laten zien hoe de delen samenwerken.
type Props = { openOp: number; labelsOp: number[]; stroomOp: number; duur: number; zoomVan?: number; zoomTot?: number; dx?: number };

const LAGEN = [
  { naam: "Heat spreader", sub: "metal lid that pulls heat away", y: 0.62, dy: 3.1 },
  { naam: "GPU compute die", sub: "thousands of cores working in parallel", y: 0.42, dy: 1.95 },
  { naam: "HBM memory", sub: "stacked memory next to the die", y: 0.42, dy: 1.95 },
  { naam: "Silicon interposer", sub: "wires die and memory together", y: 0.28, dy: 0.95 },
  { naam: "Package substrate", sub: "connects the chip to the board", y: 0.12, dy: 0 },
];

// procedurele texturen (geen nepfoto's): rasters van rekenkernen, geheugenlagen, contactpunten
const tex = (w: number, h: number, teken: (c: CanvasRenderingContext2D) => void) => {
  const cv = document.createElement("canvas"); cv.width = w; cv.height = h; const c = cv.getContext("2d")!; teken(c);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
};

export const Chip3D: React.FC<Props> = ({ openOp, labelsOp, stroomOp, duur, zoomVan = 120, zoomTot = 165, dx = 0 }) => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const T = useMemo(() => ({
    die: tex(512, 512, (c) => {
      c.fillStyle = "#151b26"; c.fillRect(0, 0, 512, 512);
      for (let i = 0; i < 16; i++) for (let j = 0; j < 16; j++) { c.fillStyle = (i + j) % 3 ? "#26344d" : "#2f4470"; c.fillRect(14 + i * 30.5, 14 + j * 30.5, 26, 26); }
      c.strokeStyle = "#76b900"; c.lineWidth = 3; c.strokeRect(8, 8, 496, 496);
    }),
    hbm: tex(256, 128, (c) => { for (let i = 0; i < 8; i++) { c.fillStyle = i % 2 ? "#3d4452" : "#4b5466"; c.fillRect(0, i * 16, 256, 16); } }),
    sub: tex(1024, 768, (c) => {
      c.fillStyle = "#1c5a33"; c.fillRect(0, 0, 1024, 768); c.strokeStyle = "rgba(220,190,90,0.35)"; c.lineWidth = 2;
      for (let i = 0; i < 40; i++) { c.beginPath(); c.moveTo(Math.random() * 1024, 0); c.lineTo(Math.random() * 1024, 768); c.stroke(); }
      c.fillStyle = "#d8b25a"; for (let i = 0; i < 28; i++) { c.fillRect(24 + i * 35.5, 20, 18, 10); c.fillRect(24 + i * 35.5, 738, 18, 10); }
    }),
    inter: tex(512, 320, (c) => { c.fillStyle = "#6f7987"; c.fillRect(0, 0, 512, 320); c.strokeStyle = "rgba(255,255,255,0.18)"; for (let i = 0; i < 64; i++) { c.beginPath(); c.moveTo(i * 8, 0); c.lineTo(i * 8, 320); c.stroke(); } }),
  }), []);
  const open = inUit((f - openOp) / 36);
  const hoek = 0.62 + f * 0.0035;
  const zoom = zoomVan + (zoomTot - zoomVan) * inUit(f / duur);
  const cam = useMemo(() => new THREE.OrthographicCamera(), []);
  cam.left = -width / 2; cam.right = width / 2; cam.top = height / 2; cam.bottom = -height / 2; cam.near = -100; cam.far = 100; cam.zoom = zoom;
  cam.position.set(Math.cos(hoek) * 10, 7.0, Math.sin(hoek) * 10); cam.lookAt(-0.6, 1.75, 0); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  const Y = (i: number) => LAGEN[i].y + LAGEN[i].dy * open;
  const scherm = (x: number, y: number, z: number) => { const v = new THREE.Vector3(x, y, z).project(cam); return { x: (v.x + 1) / 2 * width + dx, y: (1 - v.y) / 2 * height }; };
  const hbm = [[-1.55, -0.6], [-1.55, 0], [-1.55, 0.6], [1.55, -0.6], [1.55, 0], [1.55, 0.6]];
  const stroom = f >= stroomOp;
  // welk onderdeel is nu "aan de beurt" (licht op)
  const actief = labelsOp.reduce((a, op, i) => (f >= op ? i : a), -1);
  const gloei = (i: number) => (actief === i ? 0.55 + 0.25 * Math.sin(f / 3) : 0);
  return (
    <>
      <ThreeCanvas width={width} height={height} camera={cam} style={{ position: "absolute", left: dx }} gl={{ antialias: true }}>
        <ambientLight intensity={0.6} color="#a9c0ff" />
        <directionalLight position={[5, 9, 3]} intensity={1.8} />
        <directionalLight position={[-6, 4, -4]} intensity={0.7} color="#38d4f2" />
        <mesh position={[0, Y(4), 0]}><boxGeometry args={[5.6, 0.2, 4.3]} /><meshStandardMaterial map={T.sub} roughness={0.6} emissive="#38d4f2" emissiveIntensity={gloei(4) * 0.4} /></mesh>
        <mesh position={[0, Y(3), 0]}><boxGeometry args={[4.4, 0.1, 2.7]} /><meshStandardMaterial map={T.inter} metalness={0.6} roughness={0.35} emissive="#38d4f2" emissiveIntensity={gloei(3) * 0.4} /></mesh>
        <mesh position={[0, Y(1), 0]}><boxGeometry args={[2.2, 0.16, 2.2]} /><meshStandardMaterial map={T.die} metalness={0.45} roughness={0.25} emissive="#76b900" emissiveIntensity={Math.max(gloei(1) * 0.5, stroom ? 0.22 + 0.12 * Math.sin(f / 4) : 0)} /></mesh>
        {hbm.map(([x, z], i) => <mesh key={i} position={[x, Y(2), z]}><boxGeometry args={[0.72, 0.26, 0.5]} /><meshStandardMaterial map={T.hbm} metalness={0.4} roughness={0.4} emissive="#38d4f2" emissiveIntensity={Math.max(gloei(2) * 0.6, stroom ? 0.3 : 0)} /></mesh>)}
        <mesh position={[0, Y(0), 0]}><boxGeometry args={[4.7, 0.14, 3.0]} /><meshStandardMaterial color="#b7c2cf" metalness={0.95} roughness={0.18} emissive="#38d4f2" emissiveIntensity={gloei(0) * 0.25} /></mesh>
        {stroom && hbm.map(([x, z], i) => Array.from({ length: 5 }).map((_, j) => {
          const u = (((f - stroomOp) / 22 + j / 5 + i * 0.11) % 1);
          return <mesh key={i + "-" + j} position={[x * (1 - u) + x * 0.4 * u, Y(2) + 0.22, z * (1 - u * 0.6)]}><sphereGeometry args={[0.08, 12, 12]} /><meshBasicMaterial color="#5be3ff" /></mesh>;
        }))}
      </ThreeCanvas>
      {/* labels: vaste ruime plekken rechts, lijn naar het onderdeel; actieve label is helder */}
      <svg width={width} height={height} style={{ position: "absolute" }}>
        {LAGEN.map((l, i) => {
          const a = zacht((f - labelsOp[i]) / 10); if (a <= 0) return null;
          const p = i === 2 ? scherm(1.9, Y(2) + 0.1, 0.6) : scherm(i === 1 ? 1.1 : 2.2, Y(i) + 0.06, i === 1 ? 1.1 : 1.3);
          const lx = 1290, ly = 250 + i * 150; const aan = actief === i;
          return (
            <g key={i} opacity={a * (aan ? 1 : 0.72)}>
              <circle cx={p.x} cy={p.y} r={aan ? 10 : 7} fill={K.cyan} />
              <path d={`M ${p.x} ${p.y} L ${p.x + (lx - 30 - p.x) * a} ${ly}`} stroke={K.cyan} strokeWidth={aan ? 3 : 2} fill="none" />
              <rect x={lx - 22} y={ly - 46} width={8} height={88} fill={aan ? K.cyan : K.line} />
              <text x={lx} y={ly - 6} style={{ font: `800 40px ${font.kop}`, fill: K.ink }}>{l.naam}</text>
              <text x={lx} y={ly + 32} style={{ font: `400 27px ${font.tekst}`, fill: K.soft }}>{l.sub}</text>
            </g>
          );
        })}
        {/* hoe het samenwerkt: geheugen -> rekenchip -> resultaat */}
        {stroom && (() => {
          const a = zacht((f - stroomOp) / 12); const m = scherm(-1.55, Y(2) + 0.3, 0.6); const d = scherm(-0.4, Y(1) + 0.3, 0.6); const o = { x: d.x - 260, y: d.y + 250 };
          return (
            <g opacity={a}>
              <defs><marker id="pk" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill={K.amber} /></marker></defs>
              <path d={`M ${m.x} ${m.y - 10} Q ${(m.x + d.x) / 2} ${m.y - 120} ${d.x} ${d.y - 10}`} stroke={K.amber} strokeWidth={6} fill="none" markerEnd="url(#pk)" strokeDasharray="14 10" strokeDashoffset={-f * 2} />
              <text x={Math.min(m.x, d.x) - 40} y={Math.min(m.y, d.y) - 120} textAnchor="end" style={{ font: `800 34px ${font.kop}`, fill: K.amber }}>1 · data in</text>
              <path d={`M ${d.x - 20} ${d.y + 30} Q ${d.x - 40} ${o.y - 40} ${o.x + 40} ${o.y}`} stroke={K.green} strokeWidth={6} fill="none" markerEnd="url(#pk)" strokeDasharray="14 10" strokeDashoffset={-f * 2} />
              <text x={o.x + 10} y={o.y + 50} textAnchor="end" style={{ font: `800 34px ${font.kop}`, fill: K.green }}>2 · results out</text>
            </g>
          );
        })()}
      </svg>
    </>
  );
};
