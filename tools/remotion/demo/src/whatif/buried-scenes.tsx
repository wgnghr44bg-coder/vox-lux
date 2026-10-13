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
