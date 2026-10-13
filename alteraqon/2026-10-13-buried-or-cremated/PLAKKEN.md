# Plakken in de andere chat

## 1. De prompt (alles in dit blok kopiëren)

```text
Ik wil een verticale 3D what-if video (1080x1920, 30 fps, YouTube Shorts) in Remotion met @remotion/three.

Onderwerp: What happens to you if you're buried or cremated?
Taal: Engels. Lengte: 78,6 seconden (de stem eindigt op 77 s).

Stijl:
- donker en spannend, filmische belichting, mist
- gloed (bloom) bij vuur en licht, zachte deeltjes zoals stof, as en vonken
- elke scène (S01..S18) een eigen 3D-scène met een langzaam bewegende camera
- ondertitels in het midden-onder (wit, Inter SemiBold), de zin die op dat moment gesproken wordt
- bij feiten een korte tijdstempel linksboven: klein goud label + groot getal, 2,6 seconden in beeld
- donkere drone op de achtergrond, lage klap bij elke tijdstempel, dreun bij "Then.", vuurgeluid bij de crematie
- korte overgang via zwart tussen scènes, harde opening (geen fade aan het begin)
- slot: grote tekst "BURIED or CREMATED?"

Scènes (wat je ziet):
S01 ziekenhuisbed, lichaam onder een laken, hartmonitor die vlak wordt
S02 een pad dat splitst: links een graf met grafsteen, rechts een crematorium met vuur
S03 lichaam op een metalen tafel, licht van warm naar koud blauw, thermometer die daalt
S04 een klok die snel doorloopt boven het lichaam
S05 nachtelijke begraafplaats, kist zakt het graf in
S06 vanuit het graf omhoog kijken, deksel schuift dicht, alles zwart
S07 duizenden gloeiend groene bacteriën die zich vermenigvuldigen
S08 doorsnede onder de grond: kist, lichaam wordt een skelet, gras groeit erboven
S09 close-up van het skelet in de aarde, wortels groeien
S10 crematorium-oven, de stalen deur gaat open, vlammen
S11 vlammen rond een thermometer die wit-heet wordt
S12 een kist die verkoolt en krimpt in de vlammen
S13 as die in een bronzen urn valt
S14 zwart, één lichtbundel op de urn
S15 een draaiende glazen diamant met regenbooglicht
S16 een raket stijgt op van de aarde de ruimte in
S17 graf en urn naast elkaar, camera trekt terug
S18 idem, donkerder, met de eindtekst

Tijdstempels:
S03 BODY TEMPERATURE / −1.5°F / HR
S04 RIGOR MORTIS / 2–6 HRS
S05 DEPTH / 6 FT
S07 BACTERIA / TRILLIONS
S08 IN A COFFIN / 10 YEARS
S09 BONES / CENTURIES
S11 TEMPERATURE / 1,800°F
S12 TIME / 2 HOURS
S13 WHAT'S LEFT / 5 LBS
S16 INTO SPACE / 1997

Mijn script met de tijden per zin (start - eind in seconden, [Sxx] = hier begint een nieuwe scène):
0.80 - 4.42  [S01]  Imagine… your heart beats for the very last time.
4.77 - 8.15  [S02]  What happens next depends on one choice.
8.40 - 10.10  [  ]  Buried… or burned.
10.90 - 12.72  [S03]  Your body starts to cool.
12.97 - 15.95  [  ]  About one and a half degrees every hour.
16.30 - 18.88  [S04]  A few hours later, your muscles lock up.
19.13 - 20.51  [  ]  Rigor mortis.
21.31 - 22.73  [S05]  Option one.
22.98 - 25.92  [  ]  They lower you six feet into the cold earth.
26.27 - 27.01  [S06]  Then.
27.81 - 29.51  [S07]  The lid goes dark.
29.76 - 32.82  [  ]  And trillions of your own bacteria wake up.
33.17 - 37.15  [S08]  After about ten years in a coffin, only your skeleton is left.
37.50 - 40.52  [S09]  And your bones… can last for centuries.
41.32 - 42.62  [S10]  Option two.
42.87 - 43.69  [  ]  Fire.
44.04 - 48.50  [S11]  The chamber reaches up to one thousand eight hundred degrees Fahrenheit.
48.85 - 52.03  [S12]  In about two hours, everything soft… is gone.
52.38 - 57.16  [S13]  What's left is around five pounds of bone, ground into ash.
57.96 - 60.22  [S14]  But… here is the strange part.
60.57 - 63.75  [S15]  Your ashes can be pressed into a real diamond.
64.10 - 69.36  [S16]  And in nineteen ninety-seven, the creator of Star Trek had his ashes launched into space.
70.16 - 71.18  [S17]  So remember.
71.43 - 74.65  [  ]  Six feet of earth… or five pounds of ash.
75.00 - 77.02  [S18]  Which one would you choose?

Ik heb al een voice.mp3; zet die in public/voice.mp3.
Maak de 3D-kwaliteit zo hoog mogelijk: ACES tone mapping, zachte schaduwen, reflecties (omgevingslicht), bloom, texturen.
Schrijf de volledige compositie (alle bestanden) zodat ik hem direct kan renderen, en leg uit hoe ik het op mijn pc zet en render.
```

## 2. (Optioneel) De code die Claude al gemaakt heeft

Plak dit erachter met de zin: *"Hier is een werkende versie, verbeter deze."*

### src/whatif/Buried.tsx
```tsx
import React from "react";
import { ThreeCanvas } from "@remotion/three";
import {
  AbsoluteFill,
  Composition,
  Html5Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { SCENES } from "./buried-scenes";
import { Bloom, DPR, Environment, setupRenderer } from "./quality";
import { DURATION_S, HAS_VOICE, SHOTS, SUBS } from "./buried-timeline";

// Alteraqon: "What happens to you if you're buried or cremated?" – volledig in 3D (three.js).
// Tijden komen uit buried-timeline.ts (make_timeline.py, uit voice-times.tsv van de standaardstem).

const FPS = 30;
const f = (s: number) => Math.round(s * FPS);

// Tijdstempels (lower third): label + groot getal, ~2,6 s in beeld
const STAMPS: Record<string, [string, string]> = {
  S03: ["BODY TEMPERATURE", "−1.5°F / HR"],
  S04: ["RIGOR MORTIS", "2–6 HRS"],
  S05: ["DEPTH", "6 FT"],
  S07: ["BACTERIA", "TRILLIONS"],
  S08: ["IN A COFFIN", "10 YEARS"],
  S09: ["BONES", "CENTURIES"],
  S11: ["TEMPERATURE", "1,800°F"],
  S12: ["TIME", "2 HOURS"],
  S13: ["WHAT'S LEFT", "5 LBS"],
  S16: ["INTO SPACE", "1997"],
};
const STAMP_DELAY = 0.3;
const STAMP_LEN = 2.6;

const LowerThird: React.FC<{ label: string; value: string }> = ({ label, value }) => {
  const t = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = spring({ frame: t, fps, config: { damping: 200 }, durationInFrames: 12 });
  const out = interpolate(t, [f(STAMP_LEN) - 8, f(STAMP_LEN)], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: 80, top: 250, opacity: out }}>
      <div style={{ width: 170 * inn, height: 4, background: "#d4a64a", marginBottom: 18 }} />
      <div
        style={{
          fontFamily: "Inter",
          fontWeight: 600,
          fontSize: 34,
          letterSpacing: 6,
          color: "#e9d3a0",
          opacity: inn,
          transform: `translateX(${(1 - inn) * -30}px)`,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontFamily: "Inter Display",
          fontWeight: 300,
          fontSize: 132,
          color: "#ffffff",
          lineHeight: 1.05,
          opacity: inn,
          transform: `translateX(${(1 - inn) * -40}px)`,
          textShadow: "0 4px 24px rgba(0,0,0,0.6)",
        }}
      >
        {value}
      </div>
    </div>
  );
};

const Subtitle: React.FC = () => {
  const s = useCurrentFrame() / FPS;
  const cur = SUBS.find((x) => s >= x.start - 0.05 && s < x.end + 0.25);
  if (!cur) return null;
  return (
    <div
      style={{
        position: "absolute",
        top: 1180,
        left: 70,
        right: 70,
        textAlign: "center",
        fontFamily: "Inter",
        fontWeight: 600,
        fontSize: 58,
        lineHeight: 1.25,
        color: "#ffffff",
        textShadow: "0 3px 14px rgba(0,0,0,0.9), 0 0 4px rgba(0,0,0,0.8)",
      }}
    >
      {cur.text}
    </div>
  );
};

const Grade: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      <AbsoluteFill style={{ background: "#2a4a7a", mixBlendMode: "soft-light", opacity: 0.2 }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.5) 100%)" }} />
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: 0.09, mixBlendMode: "overlay" }}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={frame % 24} />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
    </>
  );
};

const EndTitle: React.FC = () => {
  const t = useCurrentFrame();
  const o = interpolate(t, [10, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", top: 330, left: 0, right: 0, textAlign: "center", opacity: o, fontFamily: "Inter Display", fontWeight: 300 }}>
      <div style={{ fontSize: 120, color: "#a9c4ff", letterSpacing: 8 }}>BURIED</div>
      <div style={{ fontSize: 60, color: "#ffffff", margin: "10px 0" }}>or</div>
      <div style={{ fontSize: 120, color: "#ffb070", letterSpacing: 8 }}>CREMATED?</div>
    </div>
  );
};

export const BuriedOrCremated: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const s = frame / FPS;
  const idx = Math.max(0, SHOTS.findIndex((x) => s >= x.start && s < x.end));
  const shot = SHOTS[idx] ?? SHOTS[SHOTS.length - 1];
  const Scene = SCENES[shot.id];
  const t = frame - f(shot.start);
  const dur = f(shot.end) - f(shot.start);
  // korte overgang via zwart, behalve bij de harde opening
  const dip = idx === 0 ? 0 : interpolate(t, [0, 6], [0.85, 0], { extrapolateRight: "clamp" });
  const byId = (id: string) => SHOTS.find((x) => x.id === id)!;

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <ThreeCanvas
        width={width}
        height={height}
        shadows
        dpr={DPR}
        gl={{ antialias: true }}
        onCreated={({ gl }) => setupRenderer(gl)}
        camera={{ position: [0, 2, 6], fov: 50, near: 0.05, far: 200 }}
      >
        <Environment intensity={0.3} />
        <Bloom />
        <hemisphereLight args={["#bcd0ff", "#2a2420", 0.45]} />
        <Scene key={shot.id} t={t} dur={dur} />
      </ThreeCanvas>
      <Grade />
      <AbsoluteFill style={{ background: "#000", opacity: dip }} />
      {Object.entries(STAMPS).map(([id, [label, value]]) => (
        <Sequence key={id} from={f(byId(id).start + STAMP_DELAY)} durationInFrames={f(STAMP_LEN)} layout="none">
          <LowerThird label={label} value={value} />
          <Html5Audio src={staticFile("buried/hit.mp3")} volume={0.55} />
        </Sequence>
      ))}
      <Sequence from={f(byId("S18").start)} layout="none">
        <EndTitle />
      </Sequence>
      <Subtitle />
      {/* geluid */}
      <Html5Audio src={staticFile("buried/drone.mp3")} volume={0.32} />
      {HAS_VOICE && <Html5Audio src={staticFile("buried/voice.mp3")} />}
      <Sequence from={f(byId("S06").start)} durationInFrames={f(2.5)} layout="none">
        <Html5Audio src={staticFile("buried/thud.mp3")} volume={0.9} />
      </Sequence>
      <Sequence from={f(byId("S10").start)} durationInFrames={f(byId("S13").start - byId("S10").start)} layout="none">
        <Html5Audio src={staticFile("buried/fire.mp3")} volume={0.45} loop />
      </Sequence>
      <Sequence from={f(byId("S16").start)} durationInFrames={f(5)} layout="none">
        <Html5Audio src={staticFile("buried/rocket.mp3")} volume={0.4} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const BuriedComposition = () => (
  <Composition
    id="BuriedOrCremated"
    component={BuriedOrCremated}
    durationInFrames={Math.ceil(DURATION_S * FPS)}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
```

### src/whatif/buried-scenes.tsx
```tsx
import React, { useMemo } from "react";
import * as THREE from "three";
import { random } from "remotion";
import {
  BareTree,
  bricks,
  Cam,
  clamp01,
  Clock,
  Coffin,
  Flames,
  Headstone,
  lerp,
  OpenCoffin,
  Particles,
  Pedestal,
  Rocket,
  SheetBody,
  Skeleton,
  smooth,
  Thermometer,
  Urn,
  wobble,
} from "./props";
import { Environment, Glow, TEX } from "./quality";

// De 18 scènes van "What happens if you're buried or cremated?" (één per zin).
// t = frame binnen de scène, dur = lengte van de scène in frames.

type SceneProps = { t: number; dur: number };
const prog = (t: number, dur: number) => smooth(t / Math.max(1, dur));

const Env: React.FC<{ bg: string; fog?: [number, number] }> = ({ bg, fog }) => (
  <>
    <color attach="background" args={[bg]} />
    {fog && <fog attach="fog" args={[bg, fog[0], fog[1]]} />}
  </>
);

const Floor: React.FC<{ color: string; y?: number; size?: number; map?: THREE.Texture; rough?: number }> = ({
  color,
  y = 0,
  size = 60,
  map,
  rough = 0.95,
}) => (
  <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, y, 0]} receiveShadow>
    <planeGeometry args={[size, size]} />
    <meshStandardMaterial color={color} map={map} roughness={rough} />
  </mesh>
);

const Dust: React.FC<{ t: number; n?: number; spread?: number; color?: string; seed?: string }> = ({
  t,
  n = 120,
  spread = 6,
  color = "#cfd8e3",
  seed = "d",
}) => (
  <Particles
    n={n}
    size={0.03}
    color={color}
    opacity={0.5}
    additive
    pos={(i) => [
      (random(`${seed}x${i}`) - 0.5) * spread + Math.sin(t * 0.01 + i) * 0.2,
      ((random(`${seed}y${i}`) * 4 + t * 0.003) % 4) - 0.5,
      (random(`${seed}z${i}`) - 0.5) * spread,
    ]}
  />
);

// Hartmonitor-lijn: kleine balkjes; na `flat` (0..1) wordt de lijn vlak
const Ecg: React.FC<{ t: number; flatAt: number }> = ({ t, flatAt }) => {
  const N = 90;
  const W = 1.5;
  const head = (t * 0.012) % 1;
  const pts = Array.from({ length: N + 1 }).map((_, i) => {
    const x = i / N;
    const phase = (x * 3 + 0.2) % 1;
    const beat = phase > 0.42 && phase < 0.5 ? Math.sin(((phase - 0.42) / 0.08) * Math.PI * 2) * 0.32 : 0;
    const flat = t / 30 > flatAt ? 1 : 0;
    return [x * W - W / 2, flat ? 0 : beat] as [number, number];
  });
  return (
    <group>
      {pts.slice(1).map(([x, y], i) => {
        const [px, py] = pts[i];
        const dx = x - px;
        const dy = y - py;
        const len = Math.hypot(dx, dy);
        const lit = Math.abs(i / N - head) < 0.5;
        return (
          <mesh key={i} position={[(x + px) / 2, (y + py) / 2, 0.01]} rotation={[0, 0, Math.atan2(dy, dx)]}>
            <planeGeometry args={[len + 0.004, 0.022]} />
            <meshBasicMaterial color={lit ? "#57ff9a" : "#1f6b42"} />
          </mesh>
        );
      })}
    </group>
  );
};

const Bed: React.FC = () => (
  <group>
    <mesh position={[0, 0.45, 0]} castShadow receiveShadow>
      <boxGeometry args={[2.9, 0.25, 1.25]} />
      <meshStandardMaterial color="#c9d2dc" roughness={0.8} />
    </mesh>
    <mesh position={[0, 0.2, 0]}>
      <boxGeometry args={[2.7, 0.08, 1.1]} />
      <meshStandardMaterial color="#5f6873" metalness={0.6} roughness={0.4} />
    </mesh>
    {[-1.3, 1.3].map((x) =>
      [-0.5, 0.5].map((z) => (
        <mesh key={`${x}${z}`} position={[x, 0.15, z]}>
          <cylinderGeometry args={[0.03, 0.03, 0.3, 6]} />
          <meshStandardMaterial color="#5f6873" metalness={0.6} />
        </mesh>
      )),
    )}
    <mesh position={[-1.15, 0.65, 0]}>
      <boxGeometry args={[0.45, 0.14, 0.75]} />
      <meshStandardMaterial color="#eef2f6" roughness={1} />
    </mesh>
  </group>
);

// S01 – laatste hartslag
const S01: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const flatAt = (dur / 30) * 0.62;
  const flat = t / 30 > flatAt;
  return (
    <>
      <Env bg="#05080d" fog={[6, 16]} />
      <Cam p={p} from={[3.2, 3.4, 6.4]} to={[2.4, 2.8, 5.0]} look={[0.2, 0.9, -0.3]} lookTo={[0.4, 1.0, -0.4]} fov={50} />
      <ambientLight intensity={0.15} />
      <spotLight position={[0, 5, 1]} angle={0.6} penumbra={0.8} intensity={40} color="#9db8d9" castShadow />
      <pointLight position={[1.6, 1.6, -0.6]} intensity={flat ? 1.5 : 3} color="#57ff9a" distance={4} />
      <Floor color="#8a929c" map={TEX.concrete()} rough={0.55} />
      <Bed />
      <group position={[0, 0.58, 0]}>
        <SheetBody />
      </group>
      <group position={[1.7, 0, -0.9]} rotation={[0, -0.6, 0]}>
        <mesh position={[0, 0.7, 0]}>
          <cylinderGeometry args={[0.04, 0.05, 1.4, 6]} />
          <meshStandardMaterial color="#3b424b" metalness={0.6} />
        </mesh>
        <mesh position={[0, 1.55, 0]}>
          <boxGeometry args={[1.8, 0.9, 0.12]} />
          <meshStandardMaterial color="#1b1f25" roughness={0.5} />
        </mesh>
        <mesh position={[0, 1.55, 0.065]}>
          <planeGeometry args={[1.65, 0.75]} />
          <meshBasicMaterial color="#030806" />
        </mesh>
        <group position={[0, 1.55, 0.07]}>
          <Ecg t={t} flatAt={flatAt} />
        </group>
        <Glow position={[0, 1.55, 0.3]} size={2.6} color="#3dff8a" opacity={flat ? 0.12 : 0.3} />
      </group>
    </>
  );
};

// S02 – de keuze: graf links, vuur rechts
const S02: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  return (
    <>
      <Env bg="#0a0e16" fog={[8, 30]} />
      <Cam p={p} from={[0, 1.5, 6.5]} to={[0, 2.8, 8]} look={[0, 1, -3.5]} fov={55} />
      <ambientLight intensity={0.2} />
      <directionalLight position={[-6, 8, 3]} intensity={2.4} color="#8fb3ff" castShadow />
      <Floor color="#9aa39a" map={TEX.grass()} />
      {[-1, 1].map((s) => (
        <mesh key={s} rotation={[-Math.PI / 2, 0, s * 0.33]} position={[s * 1.6, 0.01, 0]}>
          <planeGeometry args={[1.3, 12]} />
          <meshStandardMaterial color="#2b3038" roughness={1} />
        </mesh>
      ))}
      {/* links: het graf */}
      <group position={[-1.9, 0, -3.5]} scale={0.8}>
        <spotLight position={[0, 6, 2]} angle={0.5} penumbra={0.7} intensity={60} color="#9fc0ff" castShadow />
        <mesh position={[0, 0, 0.8]} scale={[1, 0.35, 1.8]}>
          <sphereGeometry args={[0.8, 10, 8]} />
          <meshStandardMaterial color="#2c241d" flatShading />
        </mesh>
        <Headstone position={[0, 0, -0.6]} scale={1.3} />
        <BareTree position={[-1.6, 0, -1.4]} scale={1.2} seed={1} />
      </group>
      {/* rechts: het crematorium */}
      <group position={[1.9, 0, -3.5]} scale={0.8}>
        <mesh position={[0, 1.2, 0]} castShadow>
          <boxGeometry args={[2.6, 2.4, 2]} />
          <meshStandardMaterial map={bricks()} roughness={0.9} />
        </mesh>
        <mesh position={[0.7, 2.9, -0.3]}>
          <boxGeometry args={[0.45, 1.6, 0.45]} />
          <meshStandardMaterial color="#2a1f1b" />
        </mesh>
        <mesh position={[0, 0.75, 1.01]}>
          <planeGeometry args={[1, 1.2]} />
          <meshBasicMaterial color="#ff7a1a" />
        </mesh>
        <pointLight position={[0, 1, 2]} intensity={12 + 4 * wobble(t * 0.3)} color="#ff7a1a" distance={8} />
        <Glow position={[0, 0.8, 1.3]} size={3} color="#ff7a1a" opacity={0.45} />
        <group position={[0, 0.2, 1.05]}>
          <Flames n={10} w={0.9} d={0.1} h={0.8} t={t} />
        </group>
      </group>
      <Dust t={t} spread={14} />
    </>
  );
};

// S03 – afkoelen: licht van warm naar koud + thermometer
const S03: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const warm = new THREE.Color("#ffb070");
  const cold = new THREE.Color("#5f8fff");
  const c = warm.clone().lerp(cold, p);
  return (
    <>
      <Env bg="#060a10" fog={[5, 14]} />
      <Cam p={p} from={[0.6, 5.6, 4.4]} to={[0.4, 4.8, 3.6]} look={[0.4, 0.6, -0.2]} fov={52} />
      <ambientLight intensity={0.12} />
      <spotLight position={[0, 4, 0.5]} angle={0.7} penumbra={0.9} intensity={45} color={c} castShadow />
      <mesh position={[0, 0.4, 0]} receiveShadow>
        <boxGeometry args={[3, 0.1, 1.3]} />
        <meshStandardMaterial color="#9aa3ad" metalness={0.85} roughness={0.25} />
      </mesh>
      <Floor color="#7a828c" map={TEX.concrete()} rough={0.5} />
      <group position={[0, 0.45, 0]}>
        <SheetBody color="#c9d0d8" />
      </group>
      <Thermometer level={lerp(0.85, 0.45, p)} color={`#${c.getHexString()}`} position={[1.3, 2.2, -1.0]} scale={0.7} />
    </>
  );
};

// S04 – rigor mortis: klok draait snel
const S04: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  return (
    <>
      <Env bg="#05070b" fog={[5, 14]} />
      <Cam p={p} from={[0, 2.2, 5.5]} to={[0.6, 1.8, 4.2]} look={[0, 1.6, 0]} fov={52} />
      <ambientLight intensity={0.15} />
      <spotLight position={[0, 5, 2]} angle={0.6} penumbra={0.8} intensity={50} color="#a9c1e0" castShadow />
      <Floor color="#7a828c" map={TEX.concrete()} rough={0.5} />
      <mesh position={[0, 2.5, -1.2]} receiveShadow>
        <planeGeometry args={[12, 8]} />
        <meshStandardMaterial color="#181c22" />
      </mesh>
      <Clock hours={2 + p * 4} position={[0, 2.6, -1.1]} scale={0.75} />
      <mesh position={[0, 0.4, 0.6]}>
        <boxGeometry args={[3, 0.1, 1.3]} />
        <meshStandardMaterial color="#9aa3ad" metalness={0.85} roughness={0.25} />
      </mesh>
      <group position={[0, 0.45, 0.6]}>
        <SheetBody color="#b9c3cf" />
      </group>
    </>
  );
};

// Grond met een open graf in het midden (gat 2.8 x 1.3)
const GraveGround: React.FC = () => {
  const soil = <meshStandardMaterial color="#c0c8b8" map={TEX.grass([10, 20])} roughness={1} />;
  return (
    <group>
      <mesh position={[-11.4, -0.1, 0]} receiveShadow>
        <boxGeometry args={[20, 0.2, 40]} />
        {soil}
      </mesh>
      <mesh position={[11.4, -0.1, 0]} receiveShadow>
        <boxGeometry args={[20, 0.2, 40]} />
        {soil}
      </mesh>
      <mesh position={[0, -0.1, 10.65]} receiveShadow>
        <boxGeometry args={[2.8, 0.2, 20]} />
        {soil}
      </mesh>
      <mesh position={[0, -0.1, -10.65]} receiveShadow>
        <boxGeometry args={[2.8, 0.2, 20]} />
        {soil}
      </mesh>
      {/* binnenkant van het gat: box die je alleen van binnen ziet */}
      <mesh position={[0, -1.25, 0]}>
        <boxGeometry args={[2.8, 2.5, 1.3]} />
        <meshStandardMaterial color="#d8c8b8" map={TEX.soil([2, 2])} roughness={1} side={THREE.BackSide} />
      </mesh>
    </group>
  );
};

// S05 – de kist zakt het graf in
const S05: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  return (
    <>
      <Env bg="#0b1018" fog={[6, 26]} />
      <Cam p={p} from={[3.6, 2.4, 6.2]} to={[2.4, 3.6, 4.4]} look={[0, -0.3, -0.6]} lookTo={[0, -1, -0.2]} fov={55} />
      <ambientLight intensity={0.25} />
      <directionalLight position={[-4, 7, 3]} intensity={3} color="#9db6e8" castShadow shadow-mapSize={[1024, 1024]} />
      <spotLight position={[0, 6, 2]} angle={0.5} penumbra={0.8} intensity={60} color="#c9d8ff" />
      <GraveGround />
      <group position={[0, lerp(0.5, -2.35, p), 0]}>
        <Coffin />
      </group>
      <mesh position={[0, 0, -1.6]} scale={[1.6, 0.45, 0.7]}>
        <sphereGeometry args={[1, 10, 8]} />
        <meshStandardMaterial color="#d0b8a0" map={TEX.soil([2, 2])} roughness={1} />
      </mesh>
      <Headstone position={[0, 0, -2.6]} scale={1.1} />
      <Headstone position={[-3.5, 0, -3.5]} rotation={[0, 0.15, 0.05]} />
      <Headstone position={[3.8, 0, -4.2]} rotation={[0, -0.2, -0.04]} />
      <Headstone position={[-2.2, 0, -7]} />
      <BareTree position={[-4.5, 0, -6]} scale={1.4} seed={2} />
      <BareTree position={[5, 0, -8]} scale={1.6} seed={3} />
      <Dust t={t} spread={12} />
    </>
  );
};

// S06 – "Then." vanuit het graf omhoog; het deksel schuift dicht
const S06: React.FC<SceneProps> = ({ t, dur }) => {
  const close = clamp01(t / Math.max(1, dur * 0.45));
  return (
    <>
      <Env bg="#2c3a52" />
      <Cam p={0} from={[0, -2.1, 0]} to={[0, -2.1, 0]} look={[0.05, 3, 0]} up={[0, 0, -1]} fov={70} />
      <ambientLight intensity={0.6} />
      <GraveGround />
      <mesh position={[lerp(-3.2, 0, smooth(close)), -1.7, 0]}>
        <boxGeometry args={[3.2, 0.06, 2.2]} />
        <meshStandardMaterial color="#1a0f08" />
      </mesh>
      <Particles
        n={80}
        size={0.05}
        color="#5a4632"
        pos={(i) => [(random(`gx${i}`) - 0.5) * 2.4, 2.5 - ((random(`gy${i}`) * 4 + t * 0.12) % 4), (random(`gz${i}`) - 0.5) * 1.1]}
      />
    </>
  );
};

// S07 – bacteriën
const S07: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const N = 260;
  const mesh = useMemo(() => {
    const m = new THREE.InstancedMesh(
      new THREE.CapsuleGeometry(0.05, 0.18, 4, 8),
      new THREE.MeshStandardMaterial({ color: "#5cff8a", emissive: "#1f9e4a", emissiveIntensity: 0.8, roughness: 0.4 }),
      N,
    );
    return m;
  }, []);
  const m4 = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const e = new THREE.Euler();
  for (let i = 0; i < N; i++) {
    const born = (i / N) * 0.85;
    const s = clamp01((t / Math.max(1, dur) - born) * 6);
    const x = (random(`bx${i}`) - 0.5) * 5 + Math.sin(t * 0.02 + i) * 0.1;
    const y = (random(`by${i}`) - 0.5) * 5 + Math.cos(t * 0.017 + i) * 0.1;
    const z = (random(`bz${i}`) - 0.5) * 4;
    e.set(random(`ra${i}`) * 6 + t * 0.01, random(`rb${i}`) * 6, random(`rc${i}`) * 6);
    q.setFromEuler(e);
    m4.compose(new THREE.Vector3(x, y, z), q, new THREE.Vector3(s, s, s));
    mesh.setMatrixAt(i, m4);
  }
  mesh.instanceMatrix.needsUpdate = true;
  return (
    <>
      <Env bg="#010604" fog={[2, 7]} />
      <Cam p={p} from={[0, 0, 4.2]} to={[0.4, 0.2, 2.6]} look={[0, 0, 0]} fov={55} />
      <ambientLight intensity={0.3} />
      <pointLight position={[2, 2, 3]} intensity={25} color="#9bffbe" />
      <primitive object={mesh} />
      <Particles n={200} size={0.02} color="#3dff7a" opacity={0.4} additive pos={(i) => [(random(`mx${i}`) - 0.5) * 6, (random(`my${i}`) - 0.5) * 6, (random(`mz${i}`) - 0.5) * 4]} />
    </>
  );
};

// S08 – doorsnede: kist onder de grond, lichaam wordt skelet
const S08: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const fade = smooth((t / Math.max(1, dur) - 0.15) / 0.6);
  return (
    <>
      <Env bg="#0b0f16" />
      <Cam p={p} from={[0, -0.8, 8.6]} to={[0.3, -1.4, 6.8]} look={[0, -1.5, 0]} lookTo={[0, -2.0, 0]} fov={50} />
      <ambientLight intensity={0.35} />
      <directionalLight position={[2, 4, 6]} intensity={3} color="#d7c2a2" />
      {/* lagen aarde (achterwand van de doorsnede) */}
      {[
        ["#4a3424", -0.6],
        ["#3d2a1d", -1.6],
        ["#33231a", -2.6],
        ["#2a1c14", -3.6],
      ].map(([c, y]) => (
        <mesh key={c as string} position={[0, y as number, -0.6]}>
          <boxGeometry args={[9, 1, 0.3]} />
          <meshStandardMaterial color={c as string} map={TEX.soil([4, 1])} roughness={1} />
        </mesh>
      ))}
      <mesh position={[0, -0.05, 0]}>
        <boxGeometry args={[9, 0.1, 1.6]} />
        <meshStandardMaterial color="#2f5a2a" roughness={1} />
      </mesh>
      {Array.from({ length: 60 }).map((_, i) => (
        <mesh key={i} position={[(random(`gr${i}`) - 0.5) * 8.6, 0.05 + 0.1 * p, (random(`gz${i}`) - 0.5) * 1.4]} scale={[1, 0.3 + p * 1.2, 1]}>
          <coneGeometry args={[0.03, 0.25, 4]} />
          <meshStandardMaterial color="#4f8a3a" />
        </mesh>
      ))}
      <Headstone position={[-1.6, 0, -0.2]} scale={0.8} />
      <group position={[0, -2.75, 0]}>
        <OpenCoffin />
        <group position={[0, 0.07, 0]} scale={0.95}>
          <SheetBody opacity={1 - fade} color="#b8b0a2" scale={0.95} />
          <Skeleton opacity={fade} />
        </group>
        <pointLight position={[0, 0.5, 1.2]} intensity={2.5} color="#ffe2b0" distance={3} />
      </group>
    </>
  );
};

// S09 – botten blijven eeuwen liggen; wortels groeien
const S09: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const a = lerp(-0.5, 0.4, p);
  return (
    <>
      <Env bg="#0a0806" fog={[1.5, 6]} />
      <Cam p={0} from={[-1.2 + Math.sin(a) * 1.4, 1.1, Math.cos(a) * 1.4]} to={[0, 0, 0]} look={[-0.7, 0.1, 0]} fov={50} />
      <ambientLight intensity={0.2} />
      <spotLight position={[-0.8, 3, 1]} angle={0.5} penumbra={0.9} intensity={22} color="#ffe0b8" castShadow />
      <Floor color="#b8a090" map={TEX.soil([3, 3])} y={0} size={10} />
      <Skeleton />
      {Array.from({ length: 9 }).map((_, i) => {
        const x = -1.4 + i * 0.4;
        const grow = clamp01(p * 1.6 - i * 0.06);
        return (
          <mesh key={i} position={[x, 0.9 - grow * 0.45, -0.35 + random(`rz${i}`) * 0.2]} rotation={[0.2, 0, (random(`rr${i}`) - 0.5) * 0.8]} scale={[1, Math.max(0.01, grow), 1]}>
            <cylinderGeometry args={[0.006, 0.025, 0.9, 5]} />
            <meshStandardMaterial color="#5c4430" />
          </mesh>
        );
      })}
      <Dust t={t} spread={3} color="#d9c2a0" n={80} seed="b" />
    </>
  );
};

// Crematorium-oven (voorkant bij z = 0)
const Furnace: React.FC<{ t: number; open: number }> = ({ t, open }) => (
  <group>
    {[
      [-2, 1.6, 2, 3.2],
      [2, 1.6, 2, 3.2],
      [0, 2.475, 2, 1.45],
      [0, 0.225, 2, 0.45],
    ].map(([x, y, w, h]) => (
      <mesh key={`${x}${y}`} position={[x, y, -0.5]}>
        <boxGeometry args={[w, h, 1]} />
        <meshStandardMaterial map={bricks()} roughness={0.9} />
      </mesh>
    ))}
    <mesh position={[0, 1.1, -0.95]}>
      <boxGeometry args={[1.9, 1.3, 0.1]} />
      <meshBasicMaterial color="#ff6a12" />
    </mesh>
    <group position={[0, 0.5, -0.8]}>
      <Flames n={16} w={1.7} d={0.3} h={1.1} t={t} seed={7} />
    </group>
    <mesh position={[0, 1.1 + open * 1.35, -0.25]}>
      <boxGeometry args={[2.1, 1.45, 0.12]} />
      <meshStandardMaterial color="#5b6168" metalness={0.85} roughness={0.35} />
    </mesh>
    <pointLight position={[0, 1.1, 0.8]} intensity={open * (18 + 6 * wobble(t * 0.3))} color="#ff7a1a" distance={7} />
  </group>
);

// S10 – optie twee: vuur (de ovendeur gaat open)
const S10: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  return (
    <>
      <Env bg="#070505" fog={[4, 14]} />
      <Cam p={p} from={[0, 1.4, 7.5]} to={[0, 1.2, 4.6]} look={[0, 1.1, 0]} fov={50} />
      <ambientLight intensity={0.12} />
      <Floor color="#6a5a50" map={TEX.concrete()} rough={0.6} />
      <Furnace t={t} open={smooth(t / Math.max(1, dur * 0.6))} />
    </>
  );
};

// S11 – 1800 °F: vlammen rond een thermometer die oploopt
const S11: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const c = new THREE.Color("#ff5a1a").lerp(new THREE.Color("#fff1c9"), p);
  return (
    <>
      <Env bg="#140502" fog={[3, 9]} />
      <Cam p={p} from={[0, 0.4, 4.4]} to={[0, 0.6, 3.4]} look={[0, 0.6, 0]} fov={55} />
      <ambientLight intensity={0.3} />
      <pointLight position={[0, 1, 2]} intensity={30 + 8 * wobble(t * 0.4)} color="#ff7a1a" />
      <Flames n={60} w={7} d={4} h={2.6} t={t} seed={11} y={-1.6} />
      <Thermometer level={lerp(0.15, 1, p)} color={`#${c.getHexString()}`} position={[0, 0.7, 0.5]} scale={0.9} />
      <Particles n={150} size={0.04} color="#ffb04a" additive pos={(i) => [(random(`ex${i}`) - 0.5) * 6, -1.5 + ((random(`ey${i}`) * 5 + t * 0.05) % 5), (random(`ez${i}`) - 0.5) * 3]} />
    </>
  );
};

// S12 – twee uur: de kist verkoolt en krimpt in de vlammen
const S12: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const s = lerp(1, 0.25, p);
  const col = new THREE.Color("#5c3820").lerp(new THREE.Color("#0d0806"), clamp01(p * 1.5));
  return (
    <>
      <Env bg="#120402" fog={[3, 10]} />
      <Cam p={p} from={[2.6, 1.6, 3.6]} to={[1.6, 1.1, 2.6]} look={[0, 0.4, 0]} fov={50} />
      <ambientLight intensity={0.2} />
      <pointLight position={[0, 1.5, 1.5]} intensity={26 + 8 * wobble(t * 0.35)} color="#ff6a1a" />
      <mesh position={[0, -0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[8, 6]} />
        <meshStandardMaterial color="#2a1a12" />
      </mesh>
      <mesh position={[0, 0.3 * s, 0]} scale={[s, s, s]}>
        <boxGeometry args={[2.5, 0.6, 0.9]} />
        <meshStandardMaterial color={col} roughness={1} emissive="#ff3a0a" emissiveIntensity={0.25 * p} />
      </mesh>
      <Flames n={36} w={3.2} d={1.6} h={lerp(1.8, 0.9, p)} t={t} seed={12} />
      <Particles n={120} size={0.04} color="#ffb04a" additive pos={(i) => [(random(`fx${i}`) - 0.5) * 3, ((random(`fy${i}`) * 3 + t * 0.04) % 3), (random(`fz${i}`) - 0.5) * 1.6]} />
    </>
  );
};

// S13 – vijf pond as valt in een urn
const S13: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  return (
    <>
      <Env bg="#0c0d10" fog={[4, 12]} />
      <Cam p={p} from={[0, 2.2, 4.4]} to={[0, 2.0, 3.2]} look={[0, 1.4, 0]} fov={48} />
      <ambientLight intensity={0.2} />
      <spotLight position={[0, 5, 1]} angle={0.45} penumbra={0.8} intensity={80} color="#e8e4dc" castShadow />
      <Floor color="#5a6068" map={TEX.concrete()} rough={0.35} />
      <Pedestal />
      <Urn position={[0, 1, 0]} />
      <Particles
        n={260}
        size={0.025}
        color="#b9b6b0"
        opacity={0.85}
        pos={(i) => {
          const fall = (random(`ay${i}`) * 3 + t * 0.06) % 3;
          const r = 0.12 * random(`ar${i}`);
          const a = random(`aa${i}`) * 6.28;
          return [Math.cos(a) * r, 5.2 - fall, Math.sin(a) * r];
        }}
      />
    </>
  );
};

// S14 – "But…": één lichtbundel op de urn
const S14: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  return (
    <>
      <Env bg="#000000" />
      <Cam p={p} from={[0, 1.7, 5]} to={[0, 1.6, 3.3]} look={[0, 1.4, 0]} fov={45} />
      <spotLight position={[0, 6, 0]} angle={0.28} penumbra={0.6} intensity={70} color="#fff3dd" castShadow />
      <mesh position={[0, 3.6, 0]}>
        <coneGeometry args={[1.25, 5, 32, 1, true]} />
        <meshBasicMaterial color="#fff3dd" transparent opacity={0.06} depthWrite={false} blending={THREE.AdditiveBlending} side={THREE.DoubleSide} />
      </mesh>
      <Floor color="#3a3e44" map={TEX.concrete()} rough={0.35} />
      <Pedestal />
      <Urn position={[0, 1, 0]} />
      <Particles n={90} size={0.02} color="#fff3dd" opacity={0.6} additive pos={(i) => [(random(`sx${i}`) - 0.5) * 1.6, 1 + ((random(`sy${i}`) * 4 + t * 0.004) % 4), (random(`sz${i}`) - 0.5) * 1.6]} />
    </>
  );
};

// S15 – een diamant van as
const S15: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const a = t * 0.03;
  return (
    <>
      <Env bg="#03050c" />
      <Environment intensity={1.6} />
      <Cam p={p} from={[0, 0.5, 6.4]} to={[0, 0.4, 5.0]} look={[0, -0.1, 0]} fov={45} />
      <ambientLight intensity={0.25} />
      <pointLight position={[Math.cos(a) * 3, 2, Math.sin(a) * 3]} intensity={40} color="#9fd2ff" />
      <pointLight position={[-Math.cos(a) * 3, -1, -Math.sin(a) * 3]} intensity={30} color="#ffb3e6" />
      <pointLight position={[0, 3, 3]} intensity={25} color="#ffffff" />
      <group rotation={[0.25, t * 0.02, 0]}>
        <mesh position={[0, 0.17, 0]}>
          <cylinderGeometry args={[0.6, 1, 0.38, 16]} />
          <meshPhysicalMaterial color="#eef8ff" transmission={1} thickness={1.2} ior={2.42} roughness={0} dispersion={5} specularIntensity={1} envMapIntensity={2.5} flatShading />
        </mesh>
        <mesh position={[0, -0.55, 0]} rotation={[Math.PI, 0, 0]}>
          <coneGeometry args={[1, 1.1, 16]} />
          <meshPhysicalMaterial color="#e2f2ff" transmission={1} thickness={1.2} ior={2.42} roughness={0} dispersion={5} specularIntensity={1} envMapIntensity={2.5} flatShading />
        </mesh>
      </group>
      <Particles
        n={40}
        size={0.09}
        color="#ffffff"
        additive
        opacity={0.9}
        pos={(i) => {
          const on = Math.sin(t * 0.25 + i * 2.1) > 0.85;
          const ang = random(`dx${i}`) * 6.28;
          return on ? [Math.cos(ang) * 1.05, (random(`dy${i}`) - 0.5) * 1.2, Math.sin(ang) * 1.05] : [0, -99, 0];
        }}
      />
    </>
  );
};

// S16 – as de ruimte in (1997)
const S16: React.FC<SceneProps> = ({ t, dur }) => {
  const p = prog(t, dur);
  const ry = lerp(-3.2, 2.4, p);
  return (
    <>
      <Env bg="#000005" />
      <Cam p={p} from={[1.5, -2.6, 6]} to={[1, 1.2, 6.5]} look={[0, -2.4, 0]} lookTo={[0, 2, 0]} fov={55} />
      <ambientLight intensity={0.15} />
      <directionalLight position={[5, 3, 4]} intensity={2.2} />
      <mesh position={[0, -8.5, -2]}>
        <sphereGeometry args={[5.5, 48, 32]} />
        <meshStandardMaterial color="#1f5aa6" emissive="#0a2350" emissiveIntensity={0.4} roughness={0.7} />
      </mesh>
      <mesh position={[0, -8.5, -2]}>
        <sphereGeometry args={[5.8, 48, 32]} />
        <meshBasicMaterial color="#5fb0ff" transparent opacity={0.18} side={THREE.BackSide} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      <group position={[0, ry, 0]} rotation={[0, 0, 0.12]}>
        <Rocket t={t} />
      </group>
      <Particles n={60} size={0.08} color="#d9d9d9" opacity={0.5} pos={(i) => [Math.sin(i) * 0.08 + (random(`tx${i}`) - 0.5) * 0.15, ry - 0.5 - i * 0.12, (random(`tz${i}`) - 0.5) * 0.15]} />
      <Particles n={700} size={0.04} color="#ffffff" opacity={0.85} pos={(i) => [(random(`st${i}`) - 0.5) * 40, (random(`su${i}`) - 0.5) * 40, -10 - random(`sv${i}`) * 10]} />
    </>
  );
};

// S17 / S18 – graf of urn, naast elkaar
const Choice: React.FC<SceneProps & { end?: boolean }> = ({ t, dur, end }) => {
  const p = prog(t, dur);
  return (
    <>
      <Env bg="#05070b" fog={[6, 18]} />
      <Cam
        p={p}
        from={end ? [0, 2.4, 7.4] : [0, 1.6, 5.4]}
        to={end ? [0, 4.2, 9.5] : [0, 2.4, 7.4]}
        look={[0, 0.9, 0]}
        lookTo={[0, end ? 0.6 : 0.9, 0]}
        fov={50}
      />
      <ambientLight intensity={0.1} />
      <Floor color="#5a6068" map={TEX.concrete()} rough={0.4} />
      <group position={[-1.15, 0, 0]} scale={0.8}>
        <spotLight position={[0, 5, 1.5]} angle={0.5} penumbra={0.8} intensity={110} color="#8fb3ff" castShadow />
        <mesh position={[0, 0, 0.6]} scale={[0.9, 0.3, 1.5]}>
          <sphereGeometry args={[0.8, 10, 8]} />
          <meshStandardMaterial color="#2c241d" flatShading />
        </mesh>
        <Headstone position={[0, 0, -0.6]} scale={1.2} />
      </group>
      <group position={[1.15, 0, 0]} scale={0.8}>
        <spotLight position={[0, 5, 1.5]} angle={0.5} penumbra={0.8} intensity={110} color="#ffb070" castShadow />
        <Pedestal />
        <Urn position={[0, 1, 0]} />
      </group>
      <Dust t={t} spread={8} />
    </>
  );
};

export const SCENES: Record<string, React.FC<SceneProps>> = {
  S01,
  S02,
  S03,
  S04,
  S05,
  S06,
  S07,
  S08,
  S09,
  S10,
  S11,
  S12,
  S13,
  S14,
  S15,
  S16,
  S17: (p) => <Choice {...p} />,
  S18: (p) => <Choice {...p} end />,
};
```

### src/whatif/props.tsx
```tsx
import React, { useMemo } from "react";
import * as THREE from "three";
import { useThree } from "@react-three/fiber";
import { random } from "remotion";
import { Glow, TEX } from "./quality";

// Bouwstenen voor de 3D what-if video's: lichaam onder laken, skelet, kist, grafsteen, urn, vlammen, ...
// Alles beweegt alleen via de meegegeven tijd t (frames), nooit via useFrame.

export type V3 = [number, number, number];

export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
export const lerp3 = (a: V3, b: V3, p: number): V3 => [lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[2], b[2], p)];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => {
  const c = clamp01(x);
  return c * c * (3 - 2 * c);
};
// zachte "ruis" uit sinussen: deterministisch, dus geen flikkeren bij renderen
export const wobble = (x: number) => Math.sin(x * 1.7) * 0.5 + Math.sin(x * 3.1 + 1.3) * 0.3 + Math.sin(x * 7.3 + 2.1) * 0.2;

// Camera die van `from` naar `to` beweegt (p = 0..1) en naar `look` kijkt.
export const Cam: React.FC<{ p: number; from: V3; to: V3; look: V3; lookTo?: V3; fov?: number; up?: V3 }> = ({
  p,
  from,
  to,
  look,
  lookTo,
  fov = 45,
  up = [0, 1, 0],
}) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  camera.up.set(...up);
  camera.position.set(...lerp3(from, to, p));
  camera.lookAt(...lerp3(look, lookTo ?? look, p));
  if (camera.fov !== fov) {
    camera.fov = fov;
    camera.updateProjectionMatrix();
  }
  return null;
};

export const Particles: React.FC<{
  n: number;
  pos: (i: number) => V3;
  size: number;
  color: string;
  opacity?: number;
  additive?: boolean;
}> = ({ n, pos, size, color, opacity = 1, additive }) => {
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 3), 3));
    return g;
  }, [n]);
  const arr = (geo.attributes.position as THREE.BufferAttribute).array as Float32Array;
  for (let i = 0; i < n; i++) arr.set(pos(i), i * 3);
  geo.attributes.position.needsUpdate = true;
  geo.computeBoundingSphere();
  return (
    <points geometry={geo}>
      <pointsMaterial
        size={size * 2.2}
        map={TEX.dot()}
        color={color}
        transparent
        opacity={opacity}
        depthWrite={false}
        blending={additive ? THREE.AdditiveBlending : THREE.NormalBlending}
      />
    </points>
  );
};

// Bot (cilinder) tussen twee punten
const Y = new THREE.Vector3(0, 1, 0);
export const Bone: React.FC<{ a: V3; b: V3; r: number; mat: THREE.Material }> = ({ a, b, r, mat }) => {
  const va = new THREE.Vector3(...a);
  const vb = new THREE.Vector3(...b);
  const dir = vb.clone().sub(va);
  const len = dir.length();
  const q = new THREE.Quaternion().setFromUnitVectors(Y, dir.normalize());
  const mid = va.add(vb).multiplyScalar(0.5);
  return (
    <group>
      <mesh position={mid} quaternion={q} material={mat} castShadow>
        <cylinderGeometry args={[r, r * 0.85, len, 16]} />
      </mesh>
      <mesh position={b} material={mat}>
        <sphereGeometry args={[r * 1.4, 16, 12]} />
      </mesh>
    </group>
  );
};

// Liggend lichaam onder een wit laken, lengte langs de x-as (hoofd bij -x).
export const SheetBody: React.FC<{ opacity?: number; color?: string; scale?: number }> = ({
  opacity = 1,
  color = "#c4ccd6",
  scale = 1,
}) => (
  <group scale={scale}>
    <mesh position={[0.05, 0.3, 0]} rotation={[0, 0, Math.PI / 2]} scale={[0.95, 1, 0.75]} castShadow>
      <capsuleGeometry args={[0.42, 1.5, 16, 32]} />
      <meshPhysicalMaterial color={color} roughness={0.85} sheen={0.5} sheenRoughness={0.7} sheenColor="#dfe6ee" transparent={opacity < 1} opacity={opacity} />
    </mesh>
    <mesh position={[-1.2, 0.34, 0]} scale={[1, 0.85, 0.9]} castShadow>
      <sphereGeometry args={[0.3, 32, 24]} />
      <meshPhysicalMaterial color={color} roughness={0.85} sheen={0.5} sheenRoughness={0.7} sheenColor="#dfe6ee" transparent={opacity < 1} opacity={opacity} />
    </mesh>
    {[-0.16, 0.16].map((z) => (
      <mesh key={z} position={[1.12, 0.42, z]} castShadow>
        <sphereGeometry args={[0.16, 10, 8]} />
        <meshPhysicalMaterial color={color} roughness={0.85} sheen={0.5} sheenRoughness={0.7} sheenColor="#dfe6ee" transparent={opacity < 1} opacity={opacity} />
      </mesh>
    ))}
  </group>
);

// Skelet op de rug, lengte langs x (schedel bij -x), y = 0 is de ondergrond.
export const Skeleton: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => {
  const mat = useMemo(
    () => new THREE.MeshPhysicalMaterial({ color: "#e3d6b8", roughness: 0.6, clearcoat: 0.2, transparent: true }),
    [],
  );
  mat.opacity = opacity;
  const dark = useMemo(() => new THREE.MeshBasicMaterial({ color: "#120d08", transparent: true }), []);
  dark.opacity = opacity;
  const arms = [-1, 1].flatMap((s) => [
    { a: [-0.78, 0.12, s * 0.27] as V3, b: [-0.32, 0.1, s * 0.33] as V3, r: 0.035 },
    { a: [-0.32, 0.1, s * 0.33] as V3, b: [0.08, 0.09, s * 0.3] as V3, r: 0.028 },
  ]);
  const legs = [-1, 1].flatMap((s) => [
    { a: [0.38, 0.1, s * 0.12] as V3, b: [0.96, 0.09, s * 0.14] as V3, r: 0.045 },
    { a: [0.96, 0.09, s * 0.14] as V3, b: [1.5, 0.08, s * 0.14] as V3, r: 0.035 },
  ]);
  return (
    <group>
      <mesh position={[-1.12, 0.2, 0]} scale={[1.1, 0.9, 0.85]} material={mat} castShadow>
        <sphereGeometry args={[0.2, 32, 24]} />
      </mesh>
      {[-0.07, 0.07].map((z) => (
        <mesh key={z} position={[-1.16, 0.35, z]} material={dark}>
          <sphereGeometry args={[0.045, 8, 6]} />
        </mesh>
      ))}
      <mesh position={[-0.95, 0.16, 0]} material={mat}>
        <boxGeometry args={[0.14, 0.08, 0.2]} />
      </mesh>
      {Array.from({ length: 11 }).map((_, i) => (
        <mesh key={i} position={[-0.86 + i * 0.1, 0.1, 0]} material={mat}>
          <boxGeometry args={[0.07, 0.07, 0.07]} />
        </mesh>
      ))}
      {Array.from({ length: 6 }).map((_, i) => (
        <mesh key={i} position={[-0.72 + i * 0.09, 0.1, 0]} rotation={[0, Math.PI / 2, 0]} material={mat}>
          <torusGeometry args={[0.22 - i * 0.012, 0.016, 8, 32, Math.PI]} />
        </mesh>
      ))}
      <mesh position={[0.3, 0.1, 0]} material={mat}>
        <boxGeometry args={[0.18, 0.1, 0.4]} />
      </mesh>
      {[...arms, ...legs].map((b, i) => (
        <Bone key={i} {...b} mat={mat} />
      ))}
      {[-1, 1].map((s) => (
        <mesh key={s} position={[1.58, 0.1, s * 0.14]} material={mat}>
          <boxGeometry args={[0.18, 0.05, 0.08]} />
        </mesh>
      ))}
    </group>
  );
};

// Gesloten kist (y = 0 is de onderkant)
export const Coffin: React.FC<{ lidOpen?: number }> = ({ lidOpen = 0 }) => (
  <group>
    <mesh position={[0, 0.28, 0]} castShadow receiveShadow>
      <boxGeometry args={[2.5, 0.56, 0.9]} />
      <meshPhysicalMaterial map={TEX.wood()} roughness={0.45} clearcoat={0.6} clearcoatRoughness={0.25} />
    </mesh>
    <mesh position={[0, 0.6 + lidOpen * 0.5, -lidOpen * 0.8]} rotation={[-lidOpen * 1.2, 0, 0]} castShadow>
      <boxGeometry args={[2.6, 0.1, 0.98]} />
      <meshPhysicalMaterial map={TEX.wood()} color="#e0c8b0" roughness={0.4} clearcoat={0.7} clearcoatRoughness={0.2} />
    </mesh>
    {[-0.8, 0, 0.8].map((x) =>
      [-1, 1].map((s) => (
        <mesh key={`${x}${s}`} position={[x, 0.3, s * 0.48]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.03, 0.03, 0.3, 6]} />
          <meshStandardMaterial color="#b9975b" metalness={0.8} roughness={0.3} />
        </mesh>
      )),
    )}
  </group>
);

// Doorsnede-kist: voorkant open zodat je naar binnen kijkt (vanaf +z)
export const OpenCoffin: React.FC = () => {
  const wood = <meshPhysicalMaterial map={TEX.wood(true)} roughness={0.55} clearcoat={0.3} />;
  return (
    <group>
      <mesh position={[0, 0.03, 0]}>
        <boxGeometry args={[2.6, 0.06, 0.9]} />
        <meshPhysicalMaterial color="#d8cfc0" roughness={0.7} sheen={1} sheenColor="#fff4e0" />
      </mesh>
      <mesh position={[0, 0.33, -0.42]}>
        <boxGeometry args={[2.6, 0.6, 0.06]} />
        <meshStandardMaterial color="#2a180e" roughness={0.8} />
      </mesh>
      {[-1.27, 1.27].map((x) => (
        <mesh key={x} position={[x, 0.33, 0]}>
          <boxGeometry args={[0.06, 0.6, 0.9]} />
          {wood}
        </mesh>
      ))}
      <mesh position={[0, 0.66, 0]}>
        <boxGeometry args={[2.66, 0.08, 0.96]} />
        {wood}
      </mesh>
    </group>
  );
};

export const Headstone: React.FC<{ position?: V3; rotation?: V3; scale?: number }> = ({
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = 1,
}) => (
  <group position={position} rotation={rotation} scale={scale}>
    <mesh position={[0, 0.5, 0]} castShadow receiveShadow>
      <boxGeometry args={[0.8, 1, 0.18]} />
      <meshStandardMaterial map={TEX.stone()} roughness={0.85} />
    </mesh>
    <mesh position={[0, 1, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
      <cylinderGeometry args={[0.4, 0.4, 0.18, 40, 1, false, -Math.PI / 2, Math.PI]} />
      <meshStandardMaterial map={TEX.stone()} roughness={0.85} />
    </mesh>
    <mesh position={[0, 0.72, 0.095]}>
      <boxGeometry args={[0.08, 0.36, 0.01]} />
      <meshStandardMaterial color="#5a5f66" />
    </mesh>
    <mesh position={[0, 0.78, 0.095]}>
      <boxGeometry args={[0.24, 0.07, 0.01]} />
      <meshStandardMaterial color="#5a5f66" />
    </mesh>
  </group>
);

export const BareTree: React.FC<{ position: V3; scale?: number; seed?: number }> = ({ position, scale = 1, seed = 0 }) => {
  const mat = <meshStandardMaterial color="#1c1714" roughness={1} />;
  return (
    <group position={position} scale={scale}>
      <mesh position={[0, 1.5, 0]} castShadow>
        <cylinderGeometry args={[0.07, 0.16, 3, 6]} />
        {mat}
      </mesh>
      {Array.from({ length: 6 }).map((_, i) => {
        const a = random(`ta${seed}${i}`) * Math.PI * 2;
        const y = 1.6 + i * 0.25;
        return (
          <mesh key={i} position={[Math.cos(a) * 0.35, y + 0.3, Math.sin(a) * 0.35]} rotation={[Math.sin(a) * 0.9, 0, -Math.cos(a) * 0.9]}>
            <cylinderGeometry args={[0.015, 0.05, 1 - i * 0.08, 5]} />
            {mat}
          </mesh>
        );
      })}
    </group>
  );
};

export const Urn: React.FC<{ position?: V3; scale?: number }> = ({ position = [0, 0, 0], scale = 1 }) => {
  const geo = useMemo(() => {
    const pts = [
      [0, 0],
      [0.32, 0],
      [0.36, 0.05],
      [0.28, 0.14],
      [0.42, 0.45],
      [0.48, 0.72],
      [0.4, 0.98],
      [0.26, 1.08],
      [0.29, 1.15],
      [0, 1.17],
    ].map(([x, y]) => new THREE.Vector2(x, y));
    return new THREE.LatheGeometry(new THREE.SplineCurve(pts).getPoints(60), 96);
  }, []);
  return (
    <group position={position} scale={scale}>
      <mesh geometry={geo} castShadow>
        <meshPhysicalMaterial color="#9a7442" metalness={1} roughness={0.22} clearcoat={0.8} clearcoatRoughness={0.1} />
      </mesh>
      <mesh position={[0, 1.24, 0]}>
        <sphereGeometry args={[0.09, 32, 24]} />
        <meshPhysicalMaterial color="#b88e50" metalness={1} roughness={0.2} clearcoat={0.8} />
      </mesh>
    </group>
  );
};

export const Pedestal: React.FC<{ position?: V3 }> = ({ position = [0, 0, 0] }) => (
  <mesh position={[position[0], position[1] + 0.5, position[2]]} receiveShadow castShadow>
    <cylinderGeometry args={[0.55, 0.62, 1, 64]} />
    <meshPhysicalMaterial map={TEX.marble()} roughness={0.25} clearcoat={0.6} clearcoatRoughness={0.15} />
  </mesh>
);

// Vlammen: druppelvormige lichtgevende vormen met kleurverloop (additief) + zachte gloed; flakkeren met t
const flameGeo = (() => {
  let g: THREE.LatheGeometry | null = null;
  return () => {
    if (g) return g;
    const pts: THREE.Vector2[] = [];
    for (let i = 0; i <= 24; i++) {
      const v = i / 24;
      const r = Math.sin(Math.PI * Math.pow(v, 0.7)) * (1 - v) * 0.9 + 0.001;
      pts.push(new THREE.Vector2(r, v));
    }
    g = new THREE.LatheGeometry(pts, 24);
    return g;
  };
})();

export const Flames: React.FC<{ n: number; w: number; d: number; h: number; t: number; seed?: number; y?: number }> = ({
  n,
  w,
  d,
  h,
  t,
  seed = 0,
  y = 0,
}) => (
  <group>
    {Array.from({ length: n }).map((_, i) => {
      const r = (k: string) => random(`${k}${seed}-${i}`);
      const fl = 0.6 + 0.4 * wobble(t * 0.22 + i * 1.37);
      const hh = h * fl * (0.6 + r("h") * 0.6);
      const rad = (0.22 + r("rad") * 0.22) * (0.9 + 0.2 * wobble(t * 0.31 + i));
      return (
        <mesh
          key={i}
          geometry={flameGeo()}
          position={[(r("x") - 0.5) * w, y, (r("z") - 0.5) * d]}
          rotation={[wobble(t * 0.13 + i * 2) * 0.12, r("ry") * 6, wobble(t * 0.1 + i) * 0.15]}
          scale={[rad, hh, rad]}
        >
          <meshBasicMaterial
            map={TEX.flame()}
            transparent
            opacity={0.75}
            depthWrite={false}
            blending={THREE.AdditiveBlending}
            side={THREE.DoubleSide}
          />
        </mesh>
      );
    })}
    <Glow position={[0, y + h * 0.3, 0]} size={Math.max(w, h) * 1.8} color="#ff6a1a" opacity={0.35 + 0.1 * wobble(t * 0.2)} />
  </group>
);

export const Thermometer: React.FC<{ level: number; color: string; position?: V3; scale?: number }> = ({
  level,
  color,
  position = [0, 0, 0],
  scale = 1,
}) => {
  const h = 0.05 + 2.8 * clamp01(level);
  return (
    <group position={position} scale={scale}>
      <mesh>
        <cylinderGeometry args={[0.14, 0.14, 3.1, 40]} />
        <meshPhysicalMaterial color="#ffffff" transmission={0.9} roughness={0.05} thickness={0.1} ior={1.5} transparent opacity={0.5} />
      </mesh>
      <mesh position={[0, -1.7, 0]}>
        <sphereGeometry args={[0.3, 20, 14]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
      </mesh>
      <mesh position={[0, -1.45 + h / 2, 0]}>
        <cylinderGeometry args={[0.075, 0.075, h, 12]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
      </mesh>
      {Array.from({ length: 10 }).map((_, i) => (
        <mesh key={i} position={[0.2, -1.3 + i * 0.29, 0]}>
          <boxGeometry args={[0.12, 0.02, 0.02]} />
          <meshBasicMaterial color="#cfd6de" />
        </mesh>
      ))}
    </group>
  );
};

export const Clock: React.FC<{ hours: number; position?: V3; scale?: number }> = ({ hours, position = [0, 0, 0], scale = 1 }) => (
  <group position={position} scale={scale}>
    <mesh rotation={[Math.PI / 2, 0, 0]}>
      <cylinderGeometry args={[1.2, 1.2, 0.1, 48]} />
      <meshStandardMaterial color="#d9d4c7" roughness={0.6} />
    </mesh>
    <mesh>
      <torusGeometry args={[1.22, 0.07, 10, 48]} />
      <meshStandardMaterial color="#2b2622" metalness={0.5} roughness={0.4} />
    </mesh>
    {Array.from({ length: 12 }).map((_, i) => {
      const a = (i / 12) * Math.PI * 2;
      return (
        <mesh key={i} position={[Math.sin(a) * 1.0, Math.cos(a) * 1.0, 0.07]} rotation={[0, 0, -a]}>
          <boxGeometry args={[0.05, i % 3 === 0 ? 0.22 : 0.12, 0.02]} />
          <meshBasicMaterial color="#1a1612" />
        </mesh>
      );
    })}
    <group rotation={[0, 0, -(hours / 12) * Math.PI * 2]}>
      <mesh position={[0, 0.3, 0.09]}>
        <boxGeometry args={[0.08, 0.6, 0.02]} />
        <meshBasicMaterial color="#1a1612" />
      </mesh>
    </group>
    <group rotation={[0, 0, -hours * Math.PI * 2]}>
      <mesh position={[0, 0.42, 0.1]}>
        <boxGeometry args={[0.05, 0.84, 0.02]} />
        <meshBasicMaterial color="#1a1612" />
      </mesh>
    </group>
  </group>
);

// Bakstenen muur als canvas-textuur (laadt direct)
let brickTex: THREE.CanvasTexture | null = null;
export const bricks = () => {
  if (brickTex) return brickTex;
  const c = document.createElement("canvas");
  c.width = 256;
  c.height = 256;
  const g = c.getContext("2d")!;
  g.fillStyle = "#2a1f1b";
  g.fillRect(0, 0, 256, 256);
  for (let row = 0; row < 8; row++) {
    for (let col = -1; col < 5; col++) {
      const x = col * 64 + (row % 2) * 32;
      const shade = 70 + Math.floor(random(`b${row}${col}`) * 30);
      g.fillStyle = `rgb(${shade + 30},${shade - 10},${shade - 25})`;
      g.fillRect(x + 3, row * 32 + 3, 58, 26);
    }
  }
  brickTex = new THREE.CanvasTexture(c);
  brickTex.colorSpace = THREE.SRGBColorSpace;
  brickTex.wrapS = brickTex.wrapT = THREE.RepeatWrapping;
  brickTex.repeat.set(3, 3);
  return brickTex;
};

export const Rocket: React.FC<{ t: number }> = ({ t }) => (
  <group>
    <mesh position={[0, 0.5, 0]}>
      <cylinderGeometry args={[0.15, 0.15, 1, 16]} />
      <meshStandardMaterial color="#e8e8ea" metalness={0.3} roughness={0.4} />
    </mesh>
    <mesh position={[0, 1.15, 0]}>
      <coneGeometry args={[0.15, 0.3, 16]} />
      <meshStandardMaterial color="#c9302c" />
    </mesh>
    {[0, 1, 2].map((i) => (
      <mesh key={i} position={[Math.sin((i * Math.PI * 2) / 3) * 0.17, 0.12, Math.cos((i * Math.PI * 2) / 3) * 0.17]} rotation={[0, (i * Math.PI * 2) / 3, 0]}>
        <boxGeometry args={[0.02, 0.25, 0.14]} />
        <meshStandardMaterial color="#c9302c" />
      </mesh>
    ))}
    <mesh position={[0, -0.35 - 0.1 * wobble(t * 0.9), 0]} rotation={[Math.PI, 0, 0]}>
      <coneGeometry args={[0.13, 0.7 + 0.2 * wobble(t * 1.3), 12, 1, true]} />
      <meshBasicMaterial color="#ffb347" transparent opacity={0.85} blending={THREE.AdditiveBlending} depthWrite={false} />
    </mesh>
  </group>
);
```

### src/whatif/quality.tsx
```tsx
import React, { useEffect, useMemo } from "react";
import * as THREE from "three";
import { useFrame, useThree } from "@react-three/fiber";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { random } from "remotion";

// Beeldkwaliteit: filmische kleuren, zachte schaduwen, reflecties (omgevingslicht) en bloom (gloed).
// Textures worden op een canvas getekend: laden direct, dus niets blijft zwart.

export const DPR = 1.5; // supersampling: 1,5x zoveel pixels renderen, daarna verkleinen = scherpere randen

export const setupRenderer = (gl: THREE.WebGLRenderer) => {
  gl.toneMapping = THREE.ACESFilmicToneMapping;
  gl.toneMappingExposure = 0.85;
  gl.shadowMap.enabled = true;
  gl.shadowMap.type = THREE.PCFSoftShadowMap;
};

// Omgevingslicht (studio-reflecties) voor metaal, glas en glans
export const Environment: React.FC<{ intensity?: number }> = ({ intensity = 0.35 }) => {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  const env = useMemo(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const tex = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    return tex;
  }, [gl]);
  scene.environment = env;
  scene.environmentIntensity = intensity;
  return null;
};

// Bloom: heldere delen (vuur, licht, gloed) krijgen een zachte stralenkrans.
// useFrame wordt hier alleen gebruikt om het beeld te tekenen, niet om iets te animeren.
export const Bloom: React.FC<{ strength?: number; radius?: number; threshold?: number }> = ({
  strength = 0.4,
  radius = 0.5,
  threshold = 0.93,
}) => {
  const { gl, scene, camera, size } = useThree();
  const composer = useMemo(() => {
    const c = new EffectComposer(gl);
    c.addPass(new RenderPass(scene, camera));
    c.addPass(new UnrealBloomPass(new THREE.Vector2(size.width, size.height), strength, radius, threshold));
    c.addPass(new OutputPass());
    return c;
  }, [gl, scene, camera, size.width, size.height, strength, radius, threshold]);
  useEffect(() => {
    composer.setPixelRatio(gl.getPixelRatio());
    composer.setSize(size.width, size.height);
  }, [composer, gl, size]);
  useFrame(() => composer.render(), 1);
  return null;
};

const canvasTex = (key: string, w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, repeat: [number, number] = [1, 1]) => {
  const cache = canvasTex as unknown as { m?: Map<string, THREE.CanvasTexture> };
  cache.m ??= new Map();
  if (!cache.m.has(key)) {
    const c = document.createElement("canvas");
    c.width = w;
    c.height = h;
    draw(c.getContext("2d")!);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(...repeat);
    t.anisotropy = 8;
    cache.m.set(key, t);
  }
  return cache.m.get(key)!;
};

const speckle = (g: CanvasRenderingContext2D, w: number, h: number, base: string, n: number, colors: string[], seed: string, max = 3) => {
  g.fillStyle = base;
  g.fillRect(0, 0, w, h);
  for (let i = 0; i < n; i++) {
    g.fillStyle = colors[i % colors.length];
    g.globalAlpha = 0.25 + random(`${seed}a${i}`) * 0.5;
    const r = 0.5 + random(`${seed}r${i}`) * max;
    g.beginPath();
    g.arc(random(`${seed}x${i}`) * w, random(`${seed}y${i}`) * h, r, 0, Math.PI * 2);
    g.fill();
  }
  g.globalAlpha = 1;
};

export const TEX = {
  soil: (rep: [number, number] = [6, 6]) =>
    canvasTex(`soil${rep}`, 512, 512, (g) => speckle(g, 512, 512, "#3a2a1e", 5000, ["#24180f", "#5a4330", "#1a120b", "#6b5440"], "soil", 3), rep),
  grass: (rep: [number, number] = [8, 8]) =>
    canvasTex(`grass${rep}`, 512, 512, (g) => speckle(g, 512, 512, "#22301c", 6000, ["#2f4425", "#18220f", "#3c5530", "#2a2a18"], "grass", 2), rep),
  concrete: (rep: [number, number] = [6, 6]) =>
    canvasTex(`conc${rep}`, 512, 512, (g) => speckle(g, 512, 512, "#3b4048", 4000, ["#2d3138", "#4a5059", "#353a41"], "conc", 2.5), rep),
  stone: () =>
    canvasTex("stone", 256, 256, (g) => {
      speckle(g, 256, 256, "#8a8f95", 2500, ["#6d7278", "#a3a8ad", "#7b8086"], "stone", 1.5);
      g.strokeStyle = "rgba(60,64,70,0.35)";
      for (let i = 0; i < 6; i++) {
        g.lineWidth = 1 + random(`sv${i}`) * 1.5;
        g.beginPath();
        g.moveTo(random(`sa${i}`) * 256, 0);
        g.bezierCurveTo(random(`sb${i}`) * 256, 90, random(`sc${i}`) * 256, 170, random(`sd${i}`) * 256, 256);
        g.stroke();
      }
    }),
  wood: (dark = false) =>
    canvasTex(`wood${dark}`, 512, 128, (g) => {
      g.fillStyle = dark ? "#2e1a0f" : "#5a341c";
      g.fillRect(0, 0, 512, 128);
      for (let i = 0; i < 70; i++) {
        g.strokeStyle = i % 2 ? "rgba(20,10,4,0.35)" : "rgba(140,90,50,0.25)";
        g.lineWidth = 0.5 + random(`wl${i}`) * 2;
        const y = random(`wy${i}`) * 128;
        g.beginPath();
        g.moveTo(0, y);
        for (let x = 0; x <= 512; x += 32) g.lineTo(x, y + Math.sin(x * 0.02 + i) * 3);
        g.stroke();
      }
    }),
  marble: () =>
    canvasTex("marble", 256, 256, (g) => {
      speckle(g, 256, 256, "#1f2228", 1200, ["#2b2f36", "#15171b"], "mar", 2);
      g.strokeStyle = "rgba(200,200,210,0.18)";
      for (let i = 0; i < 8; i++) {
        g.lineWidth = 0.6 + random(`mv${i}`);
        g.beginPath();
        g.moveTo(0, random(`ma${i}`) * 256);
        g.bezierCurveTo(90, random(`mb${i}`) * 256, 170, random(`mc${i}`) * 256, 256, random(`md${i}`) * 256);
        g.stroke();
      }
    }),
  // zacht rond puntje voor deeltjes en gloed
  dot: () =>
    canvasTex("dot", 64, 64, (g) => {
      const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      r.addColorStop(0, "rgba(255,255,255,1)");
      r.addColorStop(0.35, "rgba(255,255,255,0.6)");
      r.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = r;
      g.fillRect(0, 0, 64, 64);
    }),
  // vlam: verloop van wit-geel onderin naar transparant oranje bovenin
  flame: () =>
    canvasTex("flame", 32, 256, (g) => {
      const l = g.createLinearGradient(0, 256, 0, 0);
      l.addColorStop(0, "rgba(255,250,220,1)");
      l.addColorStop(0.25, "rgba(255,200,80,0.95)");
      l.addColorStop(0.6, "rgba(255,100,20,0.6)");
      l.addColorStop(1, "rgba(180,30,0,0)");
      g.fillStyle = l;
      g.fillRect(0, 0, 32, 256);
    }),
};

// Zachte gloed (sprite) – bijvoorbeeld rond vuur of een scherm
export const Glow: React.FC<{ position: [number, number, number]; size: number; color: string; opacity?: number }> = ({
  position,
  size,
  color,
  opacity = 0.6,
}) => (
  <sprite position={position} scale={[size, size, 1]}>
    <spriteMaterial map={TEX.dot()} color={color} transparent opacity={opacity} depthWrite={false} blending={THREE.AdditiveBlending} />
  </sprite>
);
```
