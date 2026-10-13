import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  Img,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Showcase: 9 manieren om een stilstaande afbeelding te laten bewegen.

const BG = "#0e1116";
const LEN = 150;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const Pic: React.FC<{ src: string; style?: React.CSSProperties }> = ({ src, style }) => (
  <Img
    src={staticFile(src)}
    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", ...style }}
  />
);

const Tile: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div style={{ position: "relative", overflow: "hidden", borderRadius: 18, background: "#000" }}>
    {children}
    <div
      style={{
        position: "absolute",
        left: 14,
        bottom: 14,
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

const ZoomIn = () => {
  const s = interpolate(useCurrentFrame(), [0, LEN], [1, 1.35], clamp);
  return <Pic src="004.jpg" style={{ transform: `scale(${s})` }} />;
};

const Pan = () => {
  const x = interpolate(useCurrentFrame(), [0, LEN], [-8, 8], clamp);
  return <Pic src="018.jpg" style={{ transform: `scale(1.25) translateX(${x}%)` }} />;
};

const Crossfade = () => {
  const o = interpolate(useCurrentFrame(), [50, 90], [0, 1], clamp);
  return (
    <>
      <Pic src="031.jpg" />
      <Pic src="044.jpg" style={{ opacity: o }} />
    </>
  );
};

const Tilt3D = () => {
  const f = useCurrentFrame();
  const ry = interpolate(f, [0, LEN], [-18, 18], clamp);
  const rx = Math.sin(f / 25) * 5;
  return (
    <AbsoluteFill style={{ perspective: 900 }}>
      <Pic src="060.jpg" style={{ transform: `scale(1.2) rotateY(${ry}deg) rotateX(${rx}deg)` }} />
    </AbsoluteFill>
  );
};

const Shake = () => {
  const f = useCurrentFrame();
  const strength = interpolate(f, [30, 45, 90], [0, 14, 0], clamp);
  const x = (random(`x${f}`) - 0.5) * strength;
  const y = (random(`y${f}`) - 0.5) * strength;
  return <Pic src="044.jpg" style={{ transform: `scale(1.1) translate(${x}px, ${y}px)` }} />;
};

const CircleReveal = () => {
  const r = interpolate(useCurrentFrame(), [10, 80], [0, 75], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  return (
    <>
      <Pic src="018.jpg" style={{ filter: "grayscale(1) brightness(0.4)" }} />
      <Pic src="004.jpg" style={{ clipPath: `circle(${r}% at 50% 50%)` }} />
    </>
  );
};

const SlideTransition = () => {
  const { fps } = useVideoConfig();
  const p = spring({ frame: useCurrentFrame() - 50, fps, config: { damping: 200 } });
  return (
    <>
      <Pic src="060.jpg" style={{ transform: `translateX(${-100 * p}%)` }} />
      <Pic src="031.jpg" style={{ transform: `translateX(${100 - 100 * p}%)` }} />
    </>
  );
};

const Snow = () => {
  const f = useCurrentFrame();
  return (
    <>
      <Pic src="004.jpg" style={{ transform: `scale(${1 + f / 1500})` }} />
      {Array.from({ length: 70 }).map((_, i) => {
        const speed = 1 + random(`s${i}`) * 2.5;
        const size = 3 + random(`r${i}`) * 7;
        const y = ((random(`y${i}`) * 120 + f * speed * 0.4) % 120) - 10;
        const x = random(`x${i}`) * 100 + Math.sin((f + i * 20) / 20) * 2;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size,
              borderRadius: "50%",
              background: "white",
              opacity: 0.85,
            }}
          />
        );
      })}
    </>
  );
};

const Focus = () => {
  const f = useCurrentFrame();
  const blur = interpolate(f, [0, 70], [18, 0], clamp);
  const bright = interpolate(f, [0, 70], [0.3, 1], clamp);
  return <Pic src="031.jpg" style={{ filter: `blur(${blur}px) brightness(${bright})`, transform: "scale(1.08)" }} />;
};

export const ImageShowcase: React.FC = () => (
  <AbsoluteFill
    style={{
      background: BG,
      padding: 30,
      display: "grid",
      gridTemplateColumns: "repeat(3, 1fr)",
      gridTemplateRows: "repeat(3, 1fr)",
      gap: 24,
    }}
  >
    <Tile label="1. Inzoomen"><ZoomIn /></Tile>
    <Tile label="2. Pannen (schuiven)"><Pan /></Tile>
    <Tile label="3. Overvloeien"><Crossfade /></Tile>
    <Tile label="4. 3D-kantelen"><Tilt3D /></Tile>
    <Tile label="5. Schudden"><Shake /></Tile>
    <Tile label="6. Cirkel-onthulling"><CircleReveal /></Tile>
    <Tile label="7. Schuif-overgang"><SlideTransition /></Tile>
    <Tile label="8. Sneeuw erover"><Snow /></Tile>
    <Tile label="9. Scherp worden"><Focus /></Tile>
  </AbsoluteFill>
);

export const ImageComposition = () => (
  <Composition id="Afbeeldingen" component={ImageShowcase} durationInFrames={LEN} fps={30} width={1920} height={1080} />
);
