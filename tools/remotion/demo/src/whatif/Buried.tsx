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
