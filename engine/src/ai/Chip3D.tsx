import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { zacht, inUit, font } from "../theme";
import { K } from "./Delen";

// EXPLODED VIEW van een AI-processor (zoals moderne AI-GPU's): koeldeksel, rekenchip (GPU-die), HBM-geheugenstapels,
// silicium-interposer, package-substraat. Start dicht, schuift op het woord uit elkaar; labels volgen de 3D-posities.
type Props = { openOp: number; labelsOp: number[]; stroomOp: number; duur: number };

const LAGEN = [
  { naam: "Heat spreader", sub: "pulls heat away", y: 0.62, dy: 3.0, kleur: "#9aa7b8" },
  { naam: "GPU compute die", sub: "thousands of cores", y: 0.42, dy: 1.85, kleur: "#1d2433" },
  { naam: "HBM memory stacks", sub: "feed data to the cores", y: 0.42, dy: 1.85, kleur: "#3a3f48" },
  { naam: "Silicon interposer", sub: "connects chip and memory", y: 0.28, dy: 0.9, kleur: "#7d8794" },
  { naam: "Package substrate", sub: "links to the board", y: 0.12, dy: 0, kleur: "#1f6b3a" },
];

export const Chip3D: React.FC<Props> = ({ openOp, labelsOp, stroomOp, duur }) => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const open = inUit((f - openOp) / 40);
  const hoek = 0.55 + f * 0.004;
  const zoom = 95 + 40 * inUit(f / duur);
  const cam = useMemo(() => new THREE.OrthographicCamera(), []);
  cam.left = -width / 2; cam.right = width / 2; cam.top = height / 2; cam.bottom = -height / 2; cam.near = -100; cam.far = 100; cam.zoom = zoom;
  cam.position.set(Math.cos(hoek) * 10, 7.5, Math.sin(hoek) * 10); cam.lookAt(0, 1.6, 0); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  const Y = (i: number) => LAGEN[i].y + LAGEN[i].dy * open;
  // schermpositie van een 3D-punt (voor de labels)
  const scherm = (x: number, y: number, z: number) => { const v = new THREE.Vector3(x, y, z).project(cam); return { x: (v.x + 1) / 2 * width, y: (1 - v.y) / 2 * height }; };
  const hbm = [[-1.55, -0.55], [-1.55, 0.55], [1.55, -0.55], [1.55, 0.55], [-1.55, 0], [1.55, 0]];
  const stroom = f >= stroomOp;
  return (
    <>
      <ThreeCanvas width={width} height={height} camera={cam} style={{ position: "absolute" }} gl={{ antialias: true }}>
        <ambientLight intensity={0.55} color="#9fb8ff" />
        <directionalLight position={[5, 9, 3]} intensity={1.6} />
        <directionalLight position={[-6, 4, -4]} intensity={0.5} color="#38d4f2" />
        {/* substraat (groene printplaat met contactpunten) */}
        <mesh position={[0, Y(4), 0]}><boxGeometry args={[5.4, 0.18, 4.2]} /><meshStandardMaterial color={LAGEN[4].kleur} roughness={0.7} /></mesh>
        {Array.from({ length: 12 }).map((_, i) => <mesh key={i} position={[-2.4 + i * 0.44, Y(4) + 0.1, 1.95]}><boxGeometry args={[0.22, 0.02, 0.12]} /><meshStandardMaterial color="#d8b25a" metalness={0.9} roughness={0.3} /></mesh>)}
        {/* interposer */}
        <mesh position={[0, Y(3), 0]}><boxGeometry args={[4.3, 0.1, 2.6]} /><meshStandardMaterial color={LAGEN[3].kleur} metalness={0.6} roughness={0.35} /></mesh>
        {/* GPU-die */}
        <mesh position={[0, Y(1), 0]}><boxGeometry args={[2.1, 0.16, 2.1]} /><meshStandardMaterial color={LAGEN[1].kleur} metalness={0.5} roughness={0.25} emissive={stroom ? "#76b900" : "#000"} emissiveIntensity={stroom ? 0.25 + 0.15 * Math.sin(f / 4) : 0} /></mesh>
        {/* HBM-stapels */}
        {hbm.map(([x, z], i) => <mesh key={i} position={[x, Y(2), z]}><boxGeometry args={[0.7, 0.22, 0.46]} /><meshStandardMaterial color={LAGEN[2].kleur} metalness={0.4} roughness={0.4} emissive={stroom ? "#38d4f2" : "#000"} emissiveIntensity={stroom ? 0.35 : 0} /></mesh>)}
        {/* deksel */}
        <mesh position={[0, Y(0), 0]}><boxGeometry args={[4.6, 0.12, 2.9]} /><meshStandardMaterial color={LAGEN[0].kleur} metalness={0.95} roughness={0.22} /></mesh>
        {/* datastroom: lichtpunten van geheugen naar rekenchip */}
        {stroom && hbm.map(([x, z], i) => Array.from({ length: 4 }).map((_, j) => {
          const u = (((f - stroomOp) / 26 + j / 4 + i * 0.13) % 1);
          return <mesh key={i + "-" + j} position={[x * (1 - u) + x * 0.35 * u, Y(2) + 0.2, z * (1 - u)]}><sphereGeometry args={[0.07, 12, 12]} /><meshBasicMaterial color="#38d4f2" /></mesh>;
        }))}
      </ThreeCanvas>
      {/* labels met lijntje naar het onderdeel */}
      <svg width={width} height={height} style={{ position: "absolute" }}>
        {LAGEN.map((l, i) => {
          const a = zacht((f - labelsOp[i]) / 12); if (a <= 0) return null;
          const px = i === 2 ? 1.55 : 2.0; const p = scherm(px, Y(i) + 0.05, i === 2 ? 0.55 : 1.2);
          const lx = 1330, ly = 300 + i * 125;                    // vaste, ruime labelplekken (nooit over elkaar)
          return (
            <g key={i} opacity={a}>
              <circle cx={p.x} cy={p.y} r={7} fill={K.cyan} />
              <line x1={p.x} y1={p.y} x2={p.x + (lx - p.x) * a} y2={ly} stroke={K.cyan} strokeWidth={2} />
              <text x={lx + 14} y={ly - 4} style={{ font: `800 32px ${font.kop}`, fill: K.ink }}>{l.naam}</text>
              <text x={lx + 14} y={ly + 28} style={{ font: `400 22px ${font.tekst}`, fill: K.soft }}>{l.sub}</text>
            </g>
          );
        })}
      </svg>
    </>
  );
};
