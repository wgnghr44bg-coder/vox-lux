import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { font, zacht, inUit } from "../theme";

// Huisstijl "broadcast documentary": donker, één accentkleur per onderwerp, strakke typografie.
export const K = {
  bg: "#05080F", ink: "#F4F7FC", soft: "#9DB0CC", line: "rgba(160,190,230,0.25)",
  cyan: "#38D4F2", green: "#76B900", red: "#E63946", amber: "#FFB547", panel: "rgba(8,14,26,0.78)",
};
export const sec = (s: number) => Math.round(s * 30);
export const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

// Foto over het hele scherm met langzame camerabeweging (Ken Burns) en filmische verduistering
export const Foto: React.FC<{ src: string; van?: number; zoom?: [number, number]; pan?: [number, number, number, number]; duur: number; donker?: number; links?: boolean; stijl?: React.CSSProperties }> = ({ src, zoom = [1.12, 1.0], pan = [0, 0, 0, 0], duur, donker = 0.55, links = true, stijl }) => {
  const f = useCurrentFrame(); const t = inUit(f / duur);
  const s = zoom[0] + (zoom[1] - zoom[0]) * t; const x = pan[0] + (pan[2] - pan[0]) * t; const y = pan[1] + (pan[3] - pan[1]) * t;
  return (
    <AbsoluteFill style={{ overflow: "hidden", ...stijl }}>
      <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${s}) translate(${x}px, ${y}px)` }} />
      <AbsoluteFill style={{ background: links ? `linear-gradient(90deg, rgba(5,8,15,${donker + 0.35}) 0%, rgba(5,8,15,${donker}) 45%, rgba(5,8,15,${donker * 0.4}) 100%)` : `rgba(5,8,15,${donker})` }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,0.55) 100%)" }} />
    </AbsoluteFill>
  );
};

// Grote kop: woorden schuiven omhoog uit een masker (broadcast-stijl)
export const Kop: React.FC<{ tekst: string; van: number; x: number; y: number; maat: number; kleur?: string; midden?: boolean; gewicht?: number }> = ({ tekst, van, x, y, maat, kleur = K.ink, midden, gewicht = 900 }) => {
  const f = useCurrentFrame() - van; if (f < 0) return null;
  const w = tekst.split(" ");
  return (
    <div style={{ position: "absolute", left: x, top: y, width: midden ? 1920 - 2 * x : undefined, textAlign: midden ? "center" : "left", font: `${gewicht} ${maat}px ${font.zwaar}`, color: kleur, letterSpacing: -1, lineHeight: 1.02, textShadow: "0 4px 30px rgba(0,0,0,0.6)" }}>
      {w.map((woord, i) => { const a = zacht((f - i * 3) / 12); return (
        <span key={i} style={{ display: "inline-block", overflow: "hidden", verticalAlign: "top", marginRight: maat * 0.25 }}>
          <span style={{ display: "inline-block", transform: `translateY(${(1 - a) * 105}%)` }}>{woord}</span>
        </span>); })}
    </div>
  );
};

// Kleine bovenregel (rubriek) met gekleurd blokje
export const Rubriek: React.FC<{ tekst: string; van: number; x: number; y: number; kleur?: string }> = ({ tekst, van, x, y, kleur = K.red }) => {
  const f = useCurrentFrame() - van; if (f < 0) return null; const a = zacht(f / 10);
  return (
    <div style={{ position: "absolute", left: x, top: y, display: "flex", alignItems: "center", gap: 14, opacity: a, transform: `translateX(${(1 - a) * -20}px)` }}>
      <div style={{ background: kleur, color: "#fff", font: `800 22px ${font.kop}`, padding: "6px 14px", letterSpacing: 3 }}>{tekst}</div>
      <div style={{ height: 2, width: 260 * a, background: `linear-gradient(90deg, ${kleur}, transparent)` }} />
    </div>
  );
};

// Informatiepaneel: schuift in, met titel en korte tekst (+ optionele foto)
export const Paneel: React.FC<{ titel: string; tekst?: string; van: number; x: number; y: number; w: number; kleur?: string; foto?: string; fotoH?: number }> = ({ titel, tekst, van, x, y, w, kleur = K.cyan, foto, fotoH = 150 }) => {
  const f = useCurrentFrame() - van; if (f < 0) return null; const a = zacht(f / 14);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, opacity: a, transform: `translateY(${(1 - a) * 24}px)`, background: K.panel, border: `1px solid ${K.line}`, borderTop: `3px solid ${kleur}`, backdropFilter: "blur(8px)", boxShadow: "0 20px 50px rgba(0,0,0,0.45)" }}>
      {foto && <Img src={staticFile(foto)} style={{ width: "100%", height: fotoH, objectFit: "cover", display: "block", opacity: 0.92 }} />}
      <div style={{ padding: "14px 18px 16px" }}>
        <div style={{ font: `800 30px ${font.kop}`, color: K.ink }}>{titel}</div>
        {tekst && <div style={{ font: `400 22px ${font.tekst}`, color: K.soft, marginTop: 6, lineHeight: 1.3 }}>{tekst}</div>}
      </div>
    </div>
  );
};

// Bronvermelding (licentie) klein rechtsonder
export const Bron: React.FC<{ tekst: string }> = ({ tekst }) => (
  <div style={{ position: "absolute", right: 28, bottom: 66, font: `400 15px ${font.tekst}`, color: "rgba(220,230,245,0.65)", textShadow: "0 1px 3px #000" }}>{tekst}</div>
);

// Nieuwsbalk onderaan met lopende tekst (blijft over alle scènes staan)
export const Ticker: React.FC<{ tekst: string }> = ({ tekst }) => {
  const f = useCurrentFrame(); const x = -((f * 3.2) % 1400);
  const a = zacht(f / 15);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 52, background: "rgba(5,8,15,0.92)", borderTop: `2px solid ${K.red}`, overflow: "hidden", opacity: a }}>
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 230, background: K.red, color: "#fff", font: `800 22px ${font.kop}`, display: "flex", alignItems: "center", justifyContent: "center", letterSpacing: 2, zIndex: 2 }}>AI EXPLAINED</div>
      <div style={{ position: "absolute", left: 250 + x, top: 12, whiteSpace: "nowrap", font: `600 24px ${font.kop}`, color: K.ink, letterSpacing: 1 }}>{(tekst + "     ").repeat(6)}</div>
    </div>
  );
};

// Pijl die zichzelf tekent
export const Pijl: React.FC<{ d: string; van: number; duur?: number; kleur?: string; dik?: number; lengte?: number }> = ({ d, van, duur = 14, kleur = K.cyan, dik = 5, lengte = 600 }) => {
  const f = useCurrentFrame() - van; if (f < 0) return null; const p = zacht(f / duur);
  return (
    <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
      <defs><marker id={`kop${van}`} markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill={kleur} /></marker></defs>
      <path d={d} stroke={kleur} strokeWidth={dik} fill="none" strokeLinecap="round" strokeDasharray={lengte} strokeDashoffset={lengte * (1 - p)} markerEnd={p > 0.95 ? `url(#kop${van})` : undefined} style={{ filter: `drop-shadow(0 0 8px ${kleur})` }} />
    </svg>
  );
};

// Overgang tussen scènes: korte crossfade + lichte inzoom (geen harde knip)
export const Overgang: React.FC<{ duur: number; children: React.ReactNode; laatste?: boolean }> = ({ duur, children, laatste }) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 10, duur - (laatste ? 14 : 8), duur], [0, 1, 1, laatste ? 0 : 1], clamp);
  const s = interpolate(f, [0, 12], [1.04, 1], clamp);
  return <AbsoluteFill style={{ opacity: o, transform: `scale(${s})` }}>{children}</AbsoluteFill>;
};
