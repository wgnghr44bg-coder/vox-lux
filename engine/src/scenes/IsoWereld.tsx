import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { kleur, zacht, inUit } from "../theme";

// SCÈNE A — ISOMETRISCHE WERELD: een miniatuur-diorama (campus/stad) op een zwevend platform.
// Gebouwen groeien omhoog bij het begin, camera draait heel langzaam (parallax/diepte).
// stemming: "nacht" (normaal), "lichtUit" (op frame X gaan de lichten van de hoofdtoren uit), "rood" (verkoop: rood licht, gebouwen zakken)
type Props = { hoofdKleur?: string; lichtUitOp?: number; rood?: boolean; zakOp?: number };

const rnd = (s: number) => { const x = Math.sin(s * 9301 + 49297) * 233280; return x - Math.floor(x); };

const Gebouw: React.FC<{ x: number; z: number; w: number; d: number; h: number; groei: number; kl: string; ramen: number; uit: number; zak: number }> = ({ x, z, w, d, h, groei, kl, ramen, uit, zak }) => {
  const hh = Math.max(0.01, h * groei * (1 - 0.35 * zak));
  const lagen = Math.floor(h / 0.5);
  return (
    <group position={[x, 0, z]}>
      <mesh position={[0, hh / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[w, hh, d]} />
        <meshStandardMaterial color="#1a2742" roughness={0.6} metalness={0.3} />
      </mesh>
      {/* raamstroken: dunne, oplichtende lagen aan de voorkant */}
      {Array.from({ length: lagen }).map((_, i) => {
        const y = 0.3 + i * 0.5;
        if (y > hh - 0.15) return null;
        const aan = ramen * (1 - uit * (y / Math.max(0.1, h)));
        return (
          <mesh key={i} position={[0, y, d / 2 + 0.005]}>
            <planeGeometry args={[w * 0.82, 0.14]} />
            <meshBasicMaterial color={kl} transparent opacity={Math.max(0, aan) * (0.55 + 0.45 * rnd(i + x * 7))} />
          </mesh>
        );
      })}
      {Array.from({ length: lagen }).map((_, i) => {
        const y = 0.3 + i * 0.5;
        if (y > hh - 0.15) return null;
        const aan = ramen * (1 - uit * (y / Math.max(0.1, h)));
        return (
          <mesh key={"z" + i} position={[w / 2 + 0.005, y, 0]} rotation={[0, Math.PI / 2, 0]}>
            <planeGeometry args={[d * 0.82, 0.14]} />
            <meshBasicMaterial color={kl} transparent opacity={Math.max(0, aan) * 0.35} />
          </mesh>
        );
      })}
    </group>
  );
};

export const IsoWereld: React.FC<Props> = ({ hoofdKleur = kleur.nvidia, lichtUitOp, rood = false, zakOp }) => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const blokken = useMemo(() => {
    const uit: { x: number; z: number; w: number; d: number; h: number; vertraging: number; hoofd: boolean }[] = [];
    for (let i = -3; i <= 3; i++)
      for (let j = -3; j <= 3; j++) {
        if (Math.abs(i) + Math.abs(j) > 5) continue;
        const hoofd = i === 0 && j === 0;
        const r = rnd(i * 13 + j * 7);
        if (!hoofd && r < 0.22) continue;
        uit.push({ x: i * 1.25, z: j * 1.25, w: hoofd ? 1.05 : 0.75 + r * 0.25, d: hoofd ? 1.05 : 0.75 + rnd(r) * 0.25,
                   h: hoofd ? 5.2 : 0.6 + r * 2.4, vertraging: hoofd ? 18 : (Math.abs(i) + Math.abs(j)) * 3 + r * 6, hoofd });
      }
    return uit;
  }, []);
  // camera: langzaam draaien + inzoomen (filmisch, rustig)
  const hoek = Math.PI / 4 + f * 0.0016;
  const zoom = 70 + 14 * inUit(f / 240);
  const cam = useMemo(() => new THREE.OrthographicCamera(), []);
  cam.left = -width / 2; cam.right = width / 2; cam.top = height / 2; cam.bottom = -height / 2;
  cam.near = -100; cam.far = 100; cam.zoom = zoom;
  cam.position.set(Math.cos(hoek) * 10, 8.2, Math.sin(hoek) * 10);
  cam.lookAt(0, 1.4, 0);
  cam.updateProjectionMatrix();
  const uit = lichtUitOp !== undefined ? zacht((f - lichtUitOp) / 45) : 0;
  const zak = zakOp !== undefined ? zacht((f - zakOp) / 60) : 0;
  const accent = rood ? kleur.rood : hoofdKleur;
  return (
    <ThreeCanvas width={width} height={height} camera={cam} style={{ position: "absolute" }} gl={{ antialias: true }}>
      <ambientLight intensity={0.35} color="#7fa2ff" />
      <directionalLight position={[6, 10, 4]} intensity={1.1} color="#cfe0ff" castShadow />
      <pointLight position={[0, 6.5, 0]} intensity={rood ? 30 : 22 * (1 - uit)} distance={9} color={accent} />
      {/* zwevend platform met gloeiende rand */}
      <mesh position={[0, -0.25, 0]} receiveShadow>
        <boxGeometry args={[9.6, 0.5, 9.6]} />
        <meshStandardMaterial color="#0f1a2f" roughness={0.8} />
      </mesh>
      <mesh position={[0, 0.005, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[4.55, 4.62, 4, 1, Math.PI / 4]} />
        <meshBasicMaterial color={accent} transparent opacity={0.5} />
      </mesh>
      {blokken.map((b, k) => {
        const groei = zacht((f - b.vertraging) / 28);
        const kl = b.hoofd ? accent : rood ? "#ff8a8d" : kleur.cyaan;
        return <Gebouw key={k} {...b} groei={groei} kl={kl} ramen={b.hoofd ? 1 : 0.55} uit={b.hoofd ? uit : 0} zak={rood ? zak * (0.5 + rnd(k)) : 0} />;
      })}
    </ThreeCanvas>
  );
};
