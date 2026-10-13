import React, { useEffect, useMemo, useState } from "react";
import * as THREE from "three";
import { ThreeCanvas } from "@remotion/three";
import {
  AbsoluteFill,
  Composition,
  continueRender,
  delayRender,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
  Easing,
} from "remotion";

// Showcase: 6 soorten 3D-animatie met three.js. Alles beweegt via useCurrentFrame().

const W = 600;
const H = 480;
const LEN = 180;
const GOLD = "#f5b301";

// Laadt alle foto's eerst; tot ze klaar zijn geeft dit null en wacht Remotion met renderen.
const useTextures = (srcs: string[]) => {
  const [handle] = useState(() => delayRender(`textures ${srcs.join(",")}`));
  const [texs, setTexs] = useState<THREE.Texture[] | null>(null);
  useEffect(() => {
    const loader = new THREE.TextureLoader();
    Promise.all(srcs.map((src) => loader.loadAsync(staticFile(src)))).then(
      (loaded) => {
        loaded.forEach((t) => (t.colorSpace = THREE.SRGBColorSpace));
        setTexs(loaded);
        continueRender(handle);
      },
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return texs;
};

const Tile: React.FC<{
  label: string;
  bg?: string;
  children: React.ReactNode;
}> = ({ label, bg = "#151a22", children }) => (
  <div
    style={{
      position: "relative",
      width: W,
      height: H,
      borderRadius: 20,
      overflow: "hidden",
      background: bg,
    }}
  >
    <ThreeCanvas
      shadows
      width={W}
      height={H}
      camera={{ position: [0, 0, 6], fov: 45 }}
    >
      {children}
    </ThreeCanvas>
    <div
      style={{
        position: "absolute",
        left: 16,
        bottom: 16,
        padding: "6px 14px",
        borderRadius: 10,
        background: "rgba(0,0,0,0.65)",
        color: "#fff",
        fontSize: 30,
        fontFamily: "sans-serif",
        fontWeight: 700,
      }}
    >
      {label}
    </div>
  </div>
);

// 1. Kubus met foto's op de zijkanten
const PhotoCube: React.FC<{ texs: THREE.Texture[] }> = ({ texs: five }) => {
  const f = useCurrentFrame();
  const texs = [...five, five[0]];
  return (
    <>
      <ambientLight intensity={1.2} />
      <directionalLight position={[4, 5, 6]} intensity={2} />
      <mesh rotation={[0.4 + f * 0.01, f * 0.025, 0]}>
        <boxGeometry args={[2.4, 2.4, 2.4]} />
        {texs.map((t, i) => (
          <meshStandardMaterial key={i} attach={`material-${i}`} map={t} />
        ))}
      </mesh>
    </>
  );
};

// 2. Golvend landschap waar de camera overheen vliegt
const Terrain = () => {
  const f = useCurrentFrame();
  const geo = useMemo(() => new THREE.PlaneGeometry(14, 14, 36, 36), []);
  const pos = geo.attributes.position as THREE.BufferAttribute;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i);
    const y = pos.getY(i) + f * 0.05;
    pos.setZ(
      i,
      Math.sin(x * 0.8) * 0.5 +
        Math.cos(y * 0.7) * 0.6 +
        Math.sin((x + y) * 0.3) * 0.4,
    );
  }
  pos.needsUpdate = true;
  geo.computeVertexNormals();
  return (
    <>
      <fog attach="fog" args={["#1b2a3a", 4, 13]} />
      <color attach="background" args={["#1b2a3a"]} />
      <ambientLight intensity={0.6} />
      <directionalLight position={[-3, 4, 2]} intensity={2.2} color="#ffd9a0" />
      <mesh
        geometry={geo}
        rotation={[-Math.PI / 2.3, 0, 0]}
        position={[0, -1.5, 0]}
      >
        <meshStandardMaterial color="#dfe8f0" flatShading />
      </mesh>
    </>
  );
};

// 3. Vlucht door een sterrenveld
const Stars = () => {
  const f = useCurrentFrame();
  const N = 900;
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute(
      "position",
      new THREE.BufferAttribute(new Float32Array(N * 3), 3),
    );
    return g;
  }, []);
  const arr = (geo.attributes.position as THREE.BufferAttribute)
    .array as Float32Array;
  for (let i = 0; i < N; i++) {
    arr[i * 3] = (random(`x${i}`) - 0.5) * 16;
    arr[i * 3 + 1] = (random(`y${i}`) - 0.5) * 12;
    arr[i * 3 + 2] = ((random(`z${i}`) * 40 + f * 0.25) % 40) - 34;
  }
  geo.attributes.position.needsUpdate = true;
  return (
    <>
      <color attach="background" args={["#05060c"]} />
      <points geometry={geo}>
        <pointsMaterial color="#ffffff" size={0.06} />
      </points>
    </>
  );
};

// 4. Glanzende vorm met bewegend licht
const Shiny = () => {
  const f = useCurrentFrame();
  const a = f * 0.05;
  return (
    <>
      <ambientLight intensity={0.25} />
      <pointLight
        position={[Math.cos(a) * 4, 2, Math.sin(a) * 4]}
        intensity={60}
        color={GOLD}
      />
      <pointLight
        position={[-Math.cos(a) * 4, -2, -Math.sin(a) * 4]}
        intensity={40}
        color="#4aa3ff"
      />
      <mesh rotation={[f * 0.01, f * 0.015, 0]}>
        <torusKnotGeometry args={[1.1, 0.35, 200, 32]} />
        <meshStandardMaterial color="#cccccc" metalness={0.9} roughness={0.2} />
      </mesh>
    </>
  );
};

// 5. Draaiende carrousel van foto's
const Carousel: React.FC<{ texs: THREE.Texture[] }> = ({ texs }) => {
  const f = useCurrentFrame();
  const turn = interpolate(f, [0, LEN], [0, Math.PI * 2], {
    easing: Easing.inOut(Easing.sin),
  });
  return (
    <>
      <ambientLight intensity={1.5} />
      <group rotation={[0.15, turn, 0]} position={[0, 0.5, -1.5]}>
        {texs.map((t, i) => {
          const ang = (i / texs.length) * Math.PI * 2;
          return (
            <mesh
              key={i}
              position={[Math.sin(ang) * 2.6, 0, Math.cos(ang) * 2.6]}
              rotation={[0, ang, 0]}
            >
              <planeGeometry args={[2.4, 1.35]} />
              <meshStandardMaterial map={t} side={THREE.DoubleSide} />
            </mesh>
          );
        })}
      </group>
    </>
  );
};

// 6. Stuiterende ballen met schaduw
const Balls = () => {
  const f = useCurrentFrame();
  const colors = [GOLD, "#4aa3ff", "#ff5c5c", "#5cff9d"];
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[3, 6, 4]} intensity={2.5} castShadow />
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -1.6, 0]}
        receiveShadow
      >
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="#2a3240" />
      </mesh>
      {colors.map((c, i) => {
        const t = (f + i * 9) / 22;
        const y = -1.1 + Math.abs(Math.sin(t)) * 2.2;
        return (
          <mesh key={c} position={[-2.1 + i * 1.4, y, 0]} castShadow>
            <sphereGeometry args={[0.5, 32, 32]} />
            <meshStandardMaterial color={c} roughness={0.3} />
          </mesh>
        );
      })}
    </>
  );
};

// Foto's worden geladen vóór de 3D-canvassen starten, anders blijven ze zwart.
export const ThreeShowcase: React.FC = () => {
  const texs = useTextures([
    "004.jpg",
    "018.jpg",
    "031.jpg",
    "044.jpg",
    "060.jpg",
  ]);
  if (!texs) return null;
  return (
    <AbsoluteFill
      style={{
        background: "#0e1116",
        display: "grid",
        gridTemplateColumns: `repeat(3, ${W}px)`,
        gridTemplateRows: `repeat(2, ${H}px)`,
        gap: 30,
        justifyContent: "center",
        alignContent: "center",
      }}
    >
      <Tile label="1. Kubus met foto's">
        <PhotoCube texs={texs} />
      </Tile>
      <Tile label="2. Vlucht over landschap">
        <Terrain />
      </Tile>
      <Tile label="3. Sterrenveld">
        <Stars />
      </Tile>
      <Tile label="4. Glans en licht">
        <Shiny />
      </Tile>
      <Tile label="5. Foto-carrousel">
        <Carousel texs={texs} />
      </Tile>
      <Tile label="6. Stuiterende ballen">
        <Balls />
      </Tile>
    </AbsoluteFill>
  );
};

export const ThreeComposition = () => (
  <Composition
    id="DrieD"
    component={ThreeShowcase}
    durationInFrames={LEN}
    fps={30}
    width={1920}
    height={1080}
  />
);
