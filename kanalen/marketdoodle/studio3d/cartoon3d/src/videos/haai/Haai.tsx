// Haai-proef in de cartoon-3d-short stijl: één three.js-wereld per frame, post-keten van de skill
// (inkt -> lensblur -> bloom -> NEUTRAL tone map -> grade), plus onze eigen ondertitels (Market Doodle-regel).
import React, { useEffect, useMemo, useState } from "react";
import * as THREE from "three";
import { AbsoluteFill, useCurrentFrame, delayRender, continueRender } from "remotion";
import { laadOud } from "./oud";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { EffectComposer } from "@react-three/postprocessing";
import { BlendFunction, BloomEffect, ToneMappingEffect, ToneMappingMode } from "postprocessing";
import { InkPass, noInkFallback } from "../bridge/ink";
import { LensBlur } from "../bridge/lensblur";
import { GradeEffect, GRADES, GRADE_STRENGTH } from "../bridge/grade";
import { World } from "./world";
import { TOTAL, FPS, FLASH_AT, DOF, shotAt } from "./story";
import { WORDS } from "./words";

export const HAAI_FRAMES = TOTAL;

const makeBloom = () => {
  const b = new BloomEffect({ blendFunction: BlendFunction.ADD, intensity: 0.5, luminanceThreshold: 1.0, luminanceSmoothing: 0.2, mipmapBlur: true, levels: 6, radius: 0.6 });
  const mip = b.mipmapBlurPass, setSize = mip.setSize.bind(mip);
  mip.setSize = (w: number, h: number) => setSize(Math.round((1920 * w) / Math.max(h, 1)), 1920);
  return b;
};
const fwd = new THREE.Vector3();

const Inner: React.FC = () => {
  const f = useCurrentFrame();
  const { camera, scene } = useThree();
  const world = useMemo(() => new World(), []);
  const fx = useMemo(() => ({
    ink: new InkPass(scene, camera as THREE.PerspectiveCamera),
    lens: new LensBlur({ maxCoC: 24, nearScale: 1.2 }),
    bloom: makeBloom(),
    tone: new ToneMappingEffect({ mode: ToneMappingMode.NEUTRAL }),
    grade: new GradeEffect(GRADES.day, GRADE_STRENGTH.day),
  }), [camera, scene]);
  useEffect(() => () => fx.ink.dispose(), [fx]);
  const post = useMemo(() => (
    <EffectComposer multisampling={4}>
      <primitive object={fx.ink} dispose={null} />
      <primitive object={fx.lens.pre} dispose={null} />
      <primitive object={fx.lens.main} dispose={null} />
      <primitive object={fx.bloom} dispose={null} />
      <primitive object={fx.tone} dispose={null} />
      <primitive object={fx.grade} dispose={null} />
    </EffectComposer>
  ), [fx]);
  const cam = camera as THREE.PerspectiveCamera;
  const target = world.update(f, cam, scene);
  noInkFallback(world.root);
  cam.getWorldDirection(fwd);
  fx.lens.focus = Math.max(0.3, target.clone().sub(cam.position).dot(fwd));
  fx.lens.cInf = DOF[shotAt(f).id];
  return (<><primitive object={world.root} dispose={null} />{post}</>);
};

// ondertitels: 1-3 woorden tegelijk, groot wit met zwarte rand, het gesproken woord geel (zoals onze shorts)
const chunks = (() => {
  const out: { a: number; b: number; w: [string, number, number, number][] }[] = [];
  let cur: [string, number, number, number][] = [];
  WORDS.forEach((w, i) => {
    cur.push(w);
    const next = WORDS[i + 1];
    const end = /[.,?!]$/.test(w[0]) || cur.length >= 3 || !next || next[3] !== w[3];
    if (end) { out.push({ a: cur[0][1], b: next && next[3] === w[3] ? next[1] : w[2] + 0.25, w: cur }); cur = []; }
  });
  return out;
})();
const Captions: React.FC<{ t: number }> = ({ t }) => {
  const c = chunks.find((k) => t >= k.a - 0.05 && t < k.b);
  if (!c) return null;
  const pop = Math.min(1, (t - c.a + 0.05) / 0.1);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", top: 1220 }}>
      <div style={{ transform: `scale(${0.85 + 0.15 * pop})`, textAlign: "center", width: 960, fontFamily: "Arial Black, Arial, sans-serif", fontWeight: 900, fontSize: 96, lineHeight: 1.1, letterSpacing: 1,
        WebkitTextStroke: "14px #000", paintOrder: "stroke fill", color: "#fff", textShadow: "0 8px 0 rgba(0,0,0,0.35)" }}>
        {c.w.map(([w, a, b], i) => <span key={i} style={{ color: t >= a && t < b + 0.05 ? "#ffd84a" : "#fff" }}>{w.toUpperCase()}{i < c.w.length - 1 ? " " : ""}</span>)}
      </div>
    </AbsoluteFill>
  );
};

export const HaaiShort: React.FC = () => {
  const f = useCurrentFrame();
  const [klaar, setKlaar] = useState(false);
  const [h] = useState(() => delayRender("oude figuren"));
  useEffect(() => { laadOud().then(() => { setKlaar(true); continueRender(h); }); }, [h]);
  if (!klaar) return null;
  const flash = f >= FLASH_AT && f < FLASH_AT + 4 ? [0.7, 0.5, 0.3, 0.12][f - FLASH_AT] : 0;
  return (
    <AbsoluteFill style={{ background: "#cfe3f2" }}>
      <ThreeCanvas width={1080} height={1920} shadows gl={{ antialias: false, stencil: false, powerPreference: "high-performance", toneMappingExposure: 1.0 }} camera={{ fov: 50, near: 0.1, far: 1200 }}>
        <Inner />
      </ThreeCanvas>
      {flash > 0 && <AbsoluteFill style={{ background: "#ffffff", opacity: flash }} />}
      <Captions t={f / FPS} />
    </AbsoluteFill>
  );
};
