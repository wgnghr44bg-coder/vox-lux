import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { kleur, font, zacht } from "../theme";

// Achtergrond: diepe gradient + heel zacht raster dat langzaam meebeweegt (diepte, nooit helemaal stil)
export const Achtergrond: React.FC = () => {
  const f = useCurrentFrame();
  const dx = (f * 0.15) % 80;
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 35%, ${kleur.achter2} 0%, ${kleur.achter1} 70%)` }}>
      <AbsoluteFill
        style={{
          backgroundImage: `linear-gradient(${kleur.raster} 1px, transparent 1px), linear-gradient(90deg, ${kleur.raster} 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          backgroundPosition: `${dx}px ${dx * 0.5}px`,
          maskImage: "radial-gradient(ellipse at 50% 50%, black 30%, transparent 80%)",
        }}
      />
    </AbsoluteFill>
  );
};

// Kop linksboven (hoofdstuk) — schuift zacht in
export const Kop: React.FC<{ tekst: string; nr?: string }> = ({ tekst, nr }) => {
  const f = useCurrentFrame();
  const a = zacht(f / 18);
  return (
    <div style={{ position: "absolute", left: 90, top: 70, opacity: a, transform: `translateY(${(1 - a) * 14}px)` }}>
      {nr && <div style={{ font: `600 22px ${font.kop}`, color: kleur.cyaan, letterSpacing: 6 }}>{nr}</div>}
      <div style={{ font: `600 40px ${font.kop}`, color: kleur.tekst, marginTop: 6 }}>{tekst}</div>
      <div style={{ height: 3, width: 120 * a, background: kleur.cyaan, marginTop: 14, borderRadius: 2 }} />
    </div>
  );
};

// Kinetische typografie: groot getal/woord dat op zijn woord binnenkomt (schaal + vervaging -> scherp)
export const Groot: React.FC<{ tekst: string; van: number; x: number; y: number; maat?: number; kleur?: string; sub?: string; uitlijn?: "left" | "center" }> = ({
  tekst, van, x, y, maat = 150, kleur: k = kleur.tekst, sub, uitlijn = "left",
}) => {
  const f = useCurrentFrame() - van;
  if (f < 0) return null;
  const a = zacht(f / 14);
  return (
    <div style={{ position: "absolute", left: x, top: y, textAlign: uitlijn, transform: `translateX(${uitlijn === "center" ? "-50%" : "0"}) scale(${0.85 + 0.15 * a})`, transformOrigin: "left center", opacity: a, filter: `blur(${(1 - a) * 8}px)` }}>
      <div style={{ font: `900 ${maat}px ${font.cijfer}`, color: k, letterSpacing: -2, lineHeight: 1, textShadow: `0 0 40px ${k}55` }}>{tekst}</div>
      {sub && <div style={{ font: `400 34px ${font.tekst}`, color: kleur.zacht, marginTop: 12 }}>{sub}</div>}
    </div>
  );
};

// Label in een paneel (infographic-overlay)
export const Label: React.FC<{ tekst: string; van: number; x: number; y: number; k?: string }> = ({ tekst, van, x, y, k = kleur.cyaan }) => {
  const f = useCurrentFrame() - van;
  if (f < 0) return null;
  const a = zacht(f / 12);
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: a, transform: `translateY(${(1 - a) * 10}px)`, padding: "10px 18px", background: kleur.paneel, border: `1px solid ${k}66`, borderRadius: 10, font: `600 28px ${font.kop}`, color: kleur.tekst, backdropFilter: "blur(6px)" }}>
      <span style={{ display: "inline-block", width: 10, height: 10, borderRadius: 5, background: k, marginRight: 12, boxShadow: `0 0 12px ${k}` }} />
      {tekst}
    </div>
  );
};

// Overgang: korte zachte fade in/uit per scène (filmisch, geen harde knip)
export const Fade: React.FC<{ duur: number; children: React.ReactNode }> = ({ duur, children }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 10, duur - 10, duur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};
