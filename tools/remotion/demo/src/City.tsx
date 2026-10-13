import React, { useMemo } from "react";
import * as THREE from "three";
import { ThreeCanvas } from "@remotion/three";
import { AbsoluteFill, Composition, random, useCurrentFrame, useVideoConfig } from "remotion";

// Low-poly stad: de camera rijdt over een lange rechte straat (staand 9:16).
// Alles wordt met code gebouwd; elke beweging hangt af van useCurrentFrame().

const FPS = 30;
const LEN = 300;
const SPEED = 14; // meter per seconde
const ROAD_HALF = 10;
const WALK = 4; // breedte stoep
const STREET_END = -420;
const SKY_TOP = "#3f74c9";
const HAZE = "#d9d4c6";

const PALETTE = ["#e5583f", "#d94e36", "#4f93a6", "#d8c9a3", "#e9dcc0", "#b9c4b8", "#c7b28a"];

// Gevel met ramen, getekend op een canvas (laadt direct, dus geen zwarte texturen).
const facadeCache = new Map<string, THREE.CanvasTexture>();
const facade = (color: string) => {
  if (!facadeCache.has(color)) {
    const c = document.createElement("canvas");
    c.width = 128;
    c.height = 128;
    const g = c.getContext("2d")!;
    g.fillStyle = color;
    g.fillRect(0, 0, 128, 128);
    g.fillStyle = "#2a3550";
    g.fillRect(36, 30, 56, 66);
    g.fillStyle = "rgba(255,255,255,0.18)";
    g.fillRect(36, 30, 56, 8);
    g.fillStyle = "rgba(0,0,0,0.12)";
    g.fillRect(0, 120, 128, 8);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    facadeCache.set(color, t);
  }
  return facadeCache.get(color)!;
};

const stripes = (() => {
  let t: THREE.CanvasTexture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement("canvas");
    c.width = 64;
    c.height = 64;
    const g = c.getContext("2d")!;
    g.fillStyle = "#e3dccb";
    g.fillRect(0, 0, 64, 64);
    g.fillStyle = "#9d978a";
    g.fillRect(0, 40, 64, 16);
    t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  };
})();

const Building: React.FC<{ x: number; z: number; w: number; d: number; h: number; color: string; side: 1 | -1 }> = ({
  x,
  z,
  w,
  d,
  h,
  color,
  side,
}) => {
  const tex = useMemo(() => {
    const t = facade(color).clone();
    t.needsUpdate = true;
    t.repeat.set(d / 4, h / 3.5);
    return t;
  }, [color, d, h]);
  const red = color === "#e5583f" || color === "#d94e36";
  const floors = Math.floor(h / 3.5);
  const faceX = x - (side * w) / 2; // gevel aan de straatkant
  return (
    <group>
      <mesh position={[x, h / 2, z]} castShadow receiveShadow>
        <boxGeometry args={[w, h, d]} />
        <meshLambertMaterial map={tex} />
      </mesh>
      {red &&
        [-d / 4, d / 4].map((oz) =>
          Array.from({ length: floors - 1 }).map((_, f) => (
            <group key={`${oz}-${f}`} position={[faceX - side * 0.6, 4 + f * 3.5, z + oz]}>
              <mesh castShadow>
                <boxGeometry args={[1.2, 0.15, 3]} />
                <meshLambertMaterial color="#141414" />
              </mesh>
              <mesh position={[0, 1.75, 0]} rotation={[f % 2 ? 0.75 : -0.75, 0, 0]} castShadow>
                <boxGeometry args={[0.9, 0.12, 4]} />
                <meshLambertMaterial color="#141414" />
              </mesh>
            </group>
          )),
        )}
    </group>
  );
};

const Tree: React.FC<{ x: number; z: number; s: number }> = ({ x, z, s }) => (
  <group position={[x, 0.2, z]} scale={s}>
    <mesh position={[0, 1.2, 0]} castShadow>
      <cylinderGeometry args={[0.15, 0.2, 2.4, 6]} />
      <meshLambertMaterial color="#4a3426" />
    </mesh>
    <mesh position={[0, 3.2, 0]} castShadow>
      <icosahedronGeometry args={[1.6, 0]} />
      <meshLambertMaterial color="#2f6b35" flatShading />
    </mesh>
  </group>
);

const Lamp: React.FC<{ x: number; z: number; side: 1 | -1 }> = ({ x, z, side }) => (
  <group position={[x, 0, z]}>
    <mesh position={[0, 3, 0]}>
      <cylinderGeometry args={[0.08, 0.1, 6, 6]} />
      <meshLambertMaterial color="#2b2f36" />
    </mesh>
    <mesh position={[-side * 0.9, 5.9, 0]}>
      <boxGeometry args={[1.8, 0.12, 0.3]} />
      <meshLambertMaterial color="#2b2f36" />
    </mesh>
  </group>
);

const TrafficLight: React.FC<{ x: number; z: number; side: 1 | -1 }> = ({ x, z, side }) => (
  <group position={[x, 0, z]}>
    <mesh position={[0, 3.5, 0]}>
      <cylinderGeometry args={[0.12, 0.14, 7, 6]} />
      <meshLambertMaterial color="#2b2f36" />
    </mesh>
    <mesh position={[-side * 4, 6.8, 0]}>
      <boxGeometry args={[8, 0.15, 0.15]} />
      <meshLambertMaterial color="#2b2f36" />
    </mesh>
    <group position={[-side * 6, 5.9, 0.15]}>
      <mesh>
        <boxGeometry args={[0.7, 1.9, 0.5]} />
        <meshLambertMaterial color="#d6b52e" />
      </mesh>
      {["#3a2a2a", "#3a3a2a", "#44ff88"].map((c, i) => (
        <mesh key={i} position={[0, 0.55 - i * 0.55, 0.26]}>
          <circleGeometry args={[0.18, 12]} />
          <meshBasicMaterial color={c} />
        </mesh>
      ))}
    </group>
  </group>
);

const Person: React.FC<{ x: number; z: number; color: string; f: number; seed: number }> = ({ x, z, color, f, seed }) => {
  const dir = random(`pd${seed}`) > 0.5 ? 1 : -1;
  const pz = z + dir * f * 0.04;
  const bob = Math.abs(Math.sin(f * 0.25 + seed)) * 0.06;
  return (
    <group position={[x, 0.2 + bob, pz]}>
      <mesh position={[0, 0.85, 0]} castShadow>
        <boxGeometry args={[0.45, 1.1, 0.3]} />
        <meshLambertMaterial color={color} />
      </mesh>
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[0.35, 0.5, 0.25]} />
        <meshLambertMaterial color="#22252b" />
      </mesh>
      <mesh position={[0, 1.6, 0]}>
        <boxGeometry args={[0.28, 0.32, 0.28]} />
        <meshLambertMaterial color="#d9a77f" />
      </mesh>
    </group>
  );
};

const Car: React.FC<{ x: number; z: number; color: string; dir: 1 | -1 }> = ({ x, z, color, dir }) => (
  <group position={[x, 0, z]} rotation={[0, dir === 1 ? 0 : Math.PI, 0]}>
    <mesh position={[0, 0.75, 0]} castShadow>
      <boxGeometry args={[2.1, 0.9, 4.4]} />
      <meshLambertMaterial color={color} />
    </mesh>
    <mesh position={[0, 1.45, 0.2]} castShadow>
      <boxGeometry args={[1.8, 0.6, 2.2]} />
      <meshLambertMaterial color={color} />
    </mesh>
    <mesh position={[0, 0.85, -2.21]}>
      <planeGeometry args={[1.6, 0.18]} />
      <meshBasicMaterial color="#c0392b" side={THREE.DoubleSide} />
    </mesh>
    {[-0.8, 0.8].map((wx) =>
      [-1.4, 1.4].map((wz) => (
        <mesh key={`${wx}${wz}`} position={[wx, 0.32, wz]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.32, 0.32, 0.4, 8]} />
          <meshLambertMaterial color="#15171c" />
        </mesh>
      )),
    )}
  </group>
);

// Statische stad: wordt één keer opgebouwd.
const useCityLayout = () =>
  useMemo(() => {
    const buildings: { x: number; z: number; w: number; d: number; h: number; color: string; side: 1 | -1 }[] = [];
    ([-1, 1] as const).forEach((side) => {
      let z = 30;
      let i = 0;
      while (z > STREET_END) {
        const d = 10 + random(`bd${side}${i}`) * 14;
        const w = 12 + random(`bw${side}${i}`) * 8;
        const h = 14 + random(`bh${side}${i}`) * (side === 1 ? 34 : 22);
        const color = PALETTE[Math.floor(random(`bc${side}${i}`) * PALETTE.length)];
        const x = side * (ROAD_HALF + WALK + w / 2);
        buildings.push({ x, z: z - d / 2, w, d, h, color, side });
        z -= d + 0.3;
        i++;
      }
    });
    const trees: { x: number; z: number; s: number }[] = [];
    const lamps: { x: number; z: number; side: 1 | -1 }[] = [];
    ([-1, 1] as const).forEach((side) => {
      for (let z = 20, i = 0; z > STREET_END; z -= 14, i++) {
        trees.push({ x: side * (ROAD_HALF + 1.3), z: z - random(`tz${side}${i}`) * 4, s: 0.9 + random(`ts${side}${i}`) * 0.4 });
        if (i % 2 === 0) lamps.push({ x: side * (ROAD_HALF + 0.5), z: z - 7, side });
      }
    });
    const crossings = [-40, -130, -220, -310, -400];
    const people = Array.from({ length: 160 }).map((_, i) => ({
      x: (random(`px${i}`) > 0.5 ? 1 : -1) * (ROAD_HALF + 1.8 + random(`pxx${i}`) * 1.8),
      z: 25 - random(`pz${i}`) * 440,
      color: ["#2d4a7a", "#7a2d2d", "#c9a23a", "#3d6b4a", "#5a5a66", "#b5b5b5"][i % 6],
    }));
    const cars = Array.from({ length: 34 }).map((_, i) => {
      const lane = [-7.5, -2.6, 2.6, 7.5][i % 4];
      const dir: 1 | -1 = lane < 0 ? 1 : -1; // links tegemoet, rechts van je af
      const r = random(`cc${i}`);
      return {
        lane,
        dir,
        z0: 10 - random(`cz${i}`) * 330,
        speed: dir === 1 ? 10 + random(`cs${i}`) * 4 : 9 + random(`cs${i}`) * 4,
        color: r < 0.6 ? "#e8c032" : r < 0.8 ? "#c9302c" : "#e6e6e6",
      };
    });
    return { buildings, trees, lamps, crossings, people, cars };
  }, []);

const Road: React.FC = () => {
  const dashes = [];
  for (let z = 20; z > STREET_END; z -= 12) {
    for (const x of [-5, 5]) dashes.push([x, z]);
  }
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, -200]} receiveShadow>
        <planeGeometry args={[ROAD_HALF * 2, 520]} />
        <meshLambertMaterial color="#16245a" />
      </mesh>
      {[-1, 1].map((s) => (
        <mesh key={s} position={[s * (ROAD_HALF + WALK / 2), 0.1, -200]} receiveShadow>
          <boxGeometry args={[WALK, 0.2, 520]} />
          <meshLambertMaterial color="#8d93a3" />
        </mesh>
      ))}
      {[-0.22, 0.22].map((x) => (
        <mesh key={x} rotation={[-Math.PI / 2, 0, 0]} position={[x, 0.02, -200]}>
          <planeGeometry args={[0.2, 520]} />
          <meshLambertMaterial color="#d2a42a" />
        </mesh>
      ))}
      {dashes.map(([x, z]) => (
        <mesh key={`${x}${z}`} rotation={[-Math.PI / 2, 0, 0]} position={[x, 0.02, z]}>
          <planeGeometry args={[0.18, 3]} />
          <meshLambertMaterial color="#e8e8e8" />
        </mesh>
      ))}
    </group>
  );
};

const Crosswalk: React.FC<{ z: number }> = ({ z }) => (
  <group>
    {Array.from({ length: 9 }).map((_, i) => (
      <mesh key={i} rotation={[-Math.PI / 2, 0, 0]} position={[-8.8 + i * 2.2, 0.03, z]}>
        <planeGeometry args={[1.4, 3]} />
        <meshLambertMaterial color="#e8e8e8" />
      </mesh>
    ))}
  </group>
);

const Skyline: React.FC = () => {
  const t = stripes();
  const tower = (x: number, z: number, w: number, h: number) => {
    const tx = t.clone();
    tx.needsUpdate = true;
    tx.repeat.set(1, h / 2.2);
    return (
      <mesh key={`${x}${z}`} position={[x, h / 2, z]}>
        <boxGeometry args={[w, h, w]} />
        <meshLambertMaterial map={tx} />
      </mesh>
    );
  };
  return (
    <group>
      {tower(-32, -470, 22, 120)}
      {tower(-20, -500, 18, 100)}
      {tower(30, -480, 26, 135)}
      {tower(44, -520, 18, 95)}
      {tower(14, -520, 14, 70)}
      {/* torenspits zoals het Chrysler Building */}
      <group position={[0, 0, -460]}>
        {tower(0, 0, 22, 120)}
        {tower(0, 0, 16, 140)}
        <mesh position={[0, 150, 0]}>
          <coneGeometry args={[8, 22, 4]} />
          <meshLambertMaterial color="#cfcfcf" flatShading />
        </mesh>
        <mesh position={[0, 172, 0]}>
          <coneGeometry args={[1.6, 28, 4]} />
          <meshLambertMaterial color="#d9d9d9" flatShading />
        </mesh>
      </group>
    </group>
  );
};

export const City: React.FC = () => {
  const f = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const camZ = 22 - (f / FPS) * SPEED;
  const city = useCityLayout();
  const sunTarget = useMemo(() => new THREE.Object3D(), []);
  sunTarget.position.set(0, 0, camZ - 45);
  const level = ((f / FPS) * 0.25).toFixed(2);

  return (
    <AbsoluteFill style={{ background: `linear-gradient(${SKY_TOP} 0%, #6f99d6 45%, ${HAZE} 62%)` }}>
      <ThreeCanvas
        width={width}
        height={height}
        shadows
        camera={{ position: [0, 3.2, camZ], fov: 62, near: 0.5, far: 900 }}
        onCreated={({ camera }) => camera.lookAt(0, 6, camZ - 100)}
      >
        <CameraRig z={camZ} />
        <fog attach="fog" args={[HAZE, 160, 560]} />
        <hemisphereLight args={["#cfe0ff", "#3a3f55", 1.1]} />
        <primitive object={sunTarget} />
        <directionalLight
          position={[45, 70, camZ - 10]}
          target={sunTarget}
          intensity={2.6}
          color="#fff2dc"
          castShadow
          shadow-mapSize={[2048, 2048]}
          shadow-camera-left={-70}
          shadow-camera-right={70}
          shadow-camera-top={90}
          shadow-camera-bottom={-90}
          shadow-camera-near={1}
          shadow-camera-far={260}
        />
        <Road />
        {city.crossings.map((z) => (
          <Crosswalk key={z} z={z} />
        ))}
        {city.crossings.map((z) => (
          <group key={`tl${z}`}>
            <TrafficLight x={ROAD_HALF + 0.6} z={z - 3} side={1} />
            <TrafficLight x={-ROAD_HALF - 0.6} z={z + 3} side={-1} />
          </group>
        ))}
        {city.buildings.map((b, i) => (
          <Building key={i} {...b} />
        ))}
        {city.trees.map((t, i) => (
          <Tree key={i} {...t} />
        ))}
        {city.lamps.map((l, i) => (
          <Lamp key={i} {...l} />
        ))}
        {city.people.map((p, i) => (
          <Person key={i} {...p} f={f} seed={i} />
        ))}
        {city.cars.map((c, i) => {
          const raw = c.z0 - c.dir * (f / FPS) * c.speed;
          // auto's die uit beeld raken komen verderop terug
          const span = 340;
          const z = camZ + 15 - ((((camZ + 15 - raw) % span) + span) % span);
          return <Car key={i} x={c.lane} z={z} color={c.color} dir={c.dir} />;
        })}
        <Skyline />
      </ThreeCanvas>
      <div style={{ position: "absolute", left: 70, top: 300, color: "#f4efe6", fontFamily: "serif", textShadow: "0 2px 8px rgba(0,0,0,0.35)" }}>
        <div style={{ fontSize: 44, letterSpacing: 12 }}>LEVEL</div>
        <div style={{ fontSize: 120, fontWeight: 700, marginTop: 10 }}>{level}</div>
      </div>
    </AbsoluteFill>
  );
};

const CameraRig: React.FC<{ z: number }> = ({ z }) => {
  return <PerspectiveRig z={z} />;
};

// Zet de camera elk frame op de juiste plek (geen useFrame, dus geen flikkeren).
import { useThree } from "@react-three/fiber";
const PerspectiveRig: React.FC<{ z: number }> = ({ z }) => {
  const camera = useThree((s) => s.camera);
  camera.position.set(0, 3.2, z);
  camera.lookAt(0, 7, z - 100);
  return null;
};

export const CityComposition = () => (
  <Composition id="Stad" component={City} durationInFrames={LEN} fps={FPS} width={1080} height={1920} />
);
