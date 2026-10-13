import React, { useMemo } from "react";
import * as THREE from "three";
import { useThree } from "@react-three/fiber";
import { random } from "remotion";

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
        size={size}
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
        <cylinderGeometry args={[r, r * 0.85, len, 8]} />
      </mesh>
      <mesh position={b} material={mat}>
        <sphereGeometry args={[r * 1.4, 8, 6]} />
      </mesh>
    </group>
  );
};

// Liggend lichaam onder een wit laken, lengte langs de x-as (hoofd bij -x).
export const SheetBody: React.FC<{ opacity?: number; color?: string; scale?: number }> = ({
  opacity = 1,
  color = "#e6ebf0",
  scale = 1,
}) => (
  <group scale={scale}>
    <mesh position={[0.05, 0.3, 0]} rotation={[0, 0, Math.PI / 2]} scale={[0.95, 1, 0.75]} castShadow>
      <capsuleGeometry args={[0.42, 1.5, 6, 14]} />
      <meshStandardMaterial color={color} roughness={0.95} transparent={opacity < 1} opacity={opacity} />
    </mesh>
    <mesh position={[-1.2, 0.34, 0]} scale={[1, 0.85, 0.9]} castShadow>
      <sphereGeometry args={[0.3, 16, 12]} />
      <meshStandardMaterial color={color} roughness={0.95} transparent={opacity < 1} opacity={opacity} />
    </mesh>
    {[-0.16, 0.16].map((z) => (
      <mesh key={z} position={[1.12, 0.42, z]} castShadow>
        <sphereGeometry args={[0.16, 10, 8]} />
        <meshStandardMaterial color={color} roughness={0.95} transparent={opacity < 1} opacity={opacity} />
      </mesh>
    ))}
  </group>
);

// Skelet op de rug, lengte langs x (schedel bij -x), y = 0 is de ondergrond.
export const Skeleton: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => {
  const mat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#e6dcc3", roughness: 0.75, transparent: true }),
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
        <sphereGeometry args={[0.2, 14, 10]} />
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
          <torusGeometry args={[0.22 - i * 0.012, 0.016, 5, 14, Math.PI]} />
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
      <meshStandardMaterial color="#4a2c1a" roughness={0.55} />
    </mesh>
    <mesh position={[0, 0.6 + lidOpen * 0.5, -lidOpen * 0.8]} rotation={[-lidOpen * 1.2, 0, 0]} castShadow>
      <boxGeometry args={[2.6, 0.1, 0.98]} />
      <meshStandardMaterial color="#5c3820" roughness={0.5} />
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
  const wood = <meshStandardMaterial color="#3f2516" roughness={0.6} />;
  return (
    <group>
      <mesh position={[0, 0.03, 0]}>
        <boxGeometry args={[2.6, 0.06, 0.9]} />
        {wood}
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
      <meshStandardMaterial color="#7d8288" roughness={0.9} />
    </mesh>
    <mesh position={[0, 1, 0]} rotation={[Math.PI / 2, 0, 0]} castShadow>
      <cylinderGeometry args={[0.4, 0.4, 0.18, 20, 1, false, -Math.PI / 2, Math.PI]} />
      <meshStandardMaterial color="#7d8288" roughness={0.9} />
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
    return new THREE.LatheGeometry(pts, 32);
  }, []);
  return (
    <group position={position} scale={scale}>
      <mesh geometry={geo} castShadow>
        <meshStandardMaterial color="#8c6a3a" metalness={0.75} roughness={0.32} />
      </mesh>
      <mesh position={[0, 1.24, 0]}>
        <sphereGeometry args={[0.09, 12, 8]} />
        <meshStandardMaterial color="#a7834c" metalness={0.8} roughness={0.3} />
      </mesh>
    </group>
  );
};

export const Pedestal: React.FC<{ position?: V3 }> = ({ position = [0, 0, 0] }) => (
  <mesh position={[position[0], position[1] + 0.5, position[2]]} receiveShadow castShadow>
    <cylinderGeometry args={[0.55, 0.62, 1, 24]} />
    <meshStandardMaterial color="#2d2f35" roughness={0.4} />
  </mesh>
);

// Vlammen: doorzichtige kegels die oplichten (additief) en flakkeren met t
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
      const fl = 0.55 + 0.45 * wobble(t * 0.22 + i * 1.37);
      const hh = h * fl * (0.6 + r("h") * 0.6);
      const colors = ["#ff4a12", "#ff8a1f", "#ffc44a"];
      return (
        <mesh key={i} position={[(r("x") - 0.5) * w, y + hh / 2, (r("z") - 0.5) * d]} rotation={[0, r("ry") * 6, wobble(t * 0.1 + i) * 0.12]}>
          <coneGeometry args={[0.16 + r("rad") * 0.18, hh, 6, 1, true]} />
          <meshBasicMaterial
            color={colors[i % 3]}
            transparent
            opacity={0.5}
            depthWrite={false}
            blending={THREE.AdditiveBlending}
            side={THREE.DoubleSide}
          />
        </mesh>
      );
    })}
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
        <cylinderGeometry args={[0.14, 0.14, 3.1, 20]} />
        <meshStandardMaterial color="#ffffff" transparent opacity={0.22} roughness={0.1} />
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
