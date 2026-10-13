import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Showcase: 12 soorten animaties die Remotion kan, elk in een eigen tegel.
// Elke animatie loopt in 3 s en blijft daarna staan; de video herhaalt na 4 s.

const BG = "#0e1116";
const TILE = "#1a1f29";
const ACCENT = "#f5b301";
const TEXT = "#f2f2f2";
const LOOP = 120;

const useT = () => useCurrentFrame() % LOOP;

const Tile: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div
    style={{
      background: TILE,
      borderRadius: 24,
      position: "relative",
      overflow: "hidden",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    {children}
    <div
      style={{
        position: "absolute",
        bottom: 18,
        left: 0,
        right: 0,
        textAlign: "center",
        color: "#9aa4b2",
        fontSize: 30,
        fontFamily: "sans-serif",
        fontWeight: 600,
      }}
    >
      {label}
    </div>
  </div>
);

const Box: React.FC<{ style?: React.CSSProperties }> = ({ style }) => (
  <div style={{ width: 130, height: 130, borderRadius: 20, background: ACCENT, ...style }} />
);

const Fade = () => {
  const t = useT();
  return <Box style={{ opacity: interpolate(t, [0, 45], [0, 1], { extrapolateRight: "clamp" }) }} />;
};

const Slide = () => {
  const t = useT();
  const x = interpolate(t, [0, 40], [-400, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return <Box style={{ transform: `translateX(${x}px)` }} />;
};

const Bounce = () => {
  const { fps } = useVideoConfig();
  const s = spring({ frame: useT(), fps, config: { damping: 6 } });
  return <Box style={{ transform: `scale(${s})`, borderRadius: 999 }} />;
};

const Typewriter = () => {
  const text = "Wat als...?";
  const n = Math.floor(interpolate(useT(), [0, 60], [0, text.length], { extrapolateRight: "clamp" }));
  return (
    <div style={{ color: TEXT, fontSize: 56, fontFamily: "monospace", whiteSpace: "nowrap", fontWeight: 700 }}>
      {text.slice(0, n)}
      <span style={{ color: ACCENT }}>|</span>
    </div>
  );
};

const Counter = () => {
  const v = interpolate(useT(), [0, 75], [0, 2026], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  return (
    <div style={{ color: ACCENT, fontSize: 130, fontFamily: "sans-serif", fontWeight: 800 }}>
      {Math.round(v)}
    </div>
  );
};

const Rotate = () => {
  const r = interpolate(useT(), [0, 90], [0, 360], { extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  return <Box style={{ transform: `rotate(${r}deg)` }} />;
};

const DrawLine = () => {
  const len = 900;
  const p = interpolate(useT(), [0, 75], [len, 0], { extrapolateRight: "clamp" });
  return (
    <svg width={420} height={220} viewBox="0 0 420 220">
      <path
        d="M10 180 C 90 20, 160 20, 210 110 S 330 200, 410 40"
        fill="none"
        stroke={ACCENT}
        strokeWidth={12}
        strokeLinecap="round"
        strokeDasharray={len}
        strokeDashoffset={p}
      />
    </svg>
  );
};

const Captions = () => {
  const words = ["Dit", "is", "een", "ondertitel"];
  const active = Math.min(words.length - 1, Math.floor(useT() / 18));
  return (
    <div style={{ display: "flex", gap: 6, fontSize: 34, fontFamily: "sans-serif", fontWeight: 800 }}>
      {words.map((w, i) => (
        <span
          key={w}
          style={{
            color: i === active ? BG : TEXT,
            background: i === active ? ACCENT : "transparent",
            padding: "4px 10px",
            borderRadius: 10,
          }}
        >
          {w}
        </span>
      ))}
    </div>
  );
};

const Wipe = () => {
  const p = interpolate(useT(), [0, 50], [0, 100], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <div
      style={{
        color: TEXT,
        fontSize: 66,
        fontFamily: "sans-serif",
        fontWeight: 900,
        clipPath: `inset(0 ${100 - p}% 0 0)`,
      }}
    >
      IfScape3D
    </div>
  );
};

const Flip3D = () => {
  const r = interpolate(useT(), [0, 75], [-180, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.back(1.5)) });
  return (
    <div style={{ perspective: 600 }}>
      <Box style={{ transform: `rotateY(${r}deg)`, width: 220 }} />
    </div>
  );
};

const Bars = () => {
  const { fps } = useVideoConfig();
  const t = useT();
  const values = [0.4, 0.75, 0.55, 1, 0.65];
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 18, height: 200 }}>
      {values.map((v, i) => {
        const s = spring({ frame: t - i * 6, fps, config: { damping: 14 } });
        return <div key={i} style={{ width: 46, height: 200 * v * s, background: ACCENT, borderRadius: 8 }} />;
      })}
    </div>
  );
};

const Stagger = () => {
  const { fps } = useVideoConfig();
  const t = useT();
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 50px)", gap: 14 }}>
      {Array.from({ length: 15 }).map((_, i) => {
        const s = spring({ frame: t - i * 3, fps });
        return (
          <div
            key={i}
            style={{ width: 50, height: 50, borderRadius: 12, background: ACCENT, transform: `scale(${s})`, opacity: s }}
          />
        );
      })}
    </div>
  );
};

export const Showcase: React.FC = () => (
  <AbsoluteFill
    style={{
      background: BG,
      padding: 40,
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gridTemplateRows: "repeat(3, 1fr)",
      gap: 30,
    }}
  >
    <Tile label="1. Infaden"><Fade /></Tile>
    <Tile label="2. Inschuiven"><Slide /></Tile>
    <Tile label="3. Veer / stuiter"><Bounce /></Tile>
    <Tile label="4. Typemachine"><Typewriter /></Tile>
    <Tile label="5. Teller"><Counter /></Tile>
    <Tile label="6. Draaien"><Rotate /></Tile>
    <Tile label="7. Lijn tekenen"><DrawLine /></Tile>
    <Tile label="8. Ondertitel per woord"><Captions /></Tile>
    <Tile label="9. Onthullen (wipe)"><Wipe /></Tile>
    <Tile label="10. 3D-draai"><Flip3D /></Tile>
    <Tile label="11. Groeiende grafiek"><Bars /></Tile>
    <Tile label="12. Een voor een"><Stagger /></Tile>
  </AbsoluteFill>
);

export const MyComposition = () => (
  <Composition id="Showcase" component={Showcase} durationInFrames={LOOP} fps={30} width={1920} height={1080} />
);
