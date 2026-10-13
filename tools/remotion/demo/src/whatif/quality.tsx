import React, { useEffect, useMemo } from "react";
import * as THREE from "three";
import { useFrame, useThree } from "@react-three/fiber";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { random } from "remotion";

// Beeldkwaliteit: filmische kleuren, zachte schaduwen, reflecties (omgevingslicht) en bloom (gloed).
// Textures worden op een canvas getekend: laden direct, dus niets blijft zwart.

export const DPR = 1.5; // supersampling: 1,5x zoveel pixels renderen, daarna verkleinen = scherpere randen

export const setupRenderer = (gl: THREE.WebGLRenderer) => {
  gl.toneMapping = THREE.ACESFilmicToneMapping;
  gl.toneMappingExposure = 0.85;
  gl.shadowMap.enabled = true;
  gl.shadowMap.type = THREE.PCFSoftShadowMap;
};

// Omgevingslicht (studio-reflecties) voor metaal, glas en glans
export const Environment: React.FC<{ intensity?: number }> = ({ intensity = 0.35 }) => {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  const env = useMemo(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const tex = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    return tex;
  }, [gl]);
  scene.environment = env;
  scene.environmentIntensity = intensity;
  return null;
};

// Bloom: heldere delen (vuur, licht, gloed) krijgen een zachte stralenkrans.
// useFrame wordt hier alleen gebruikt om het beeld te tekenen, niet om iets te animeren.
export const Bloom: React.FC<{ strength?: number; radius?: number; threshold?: number }> = ({
  strength = 0.4,
  radius = 0.5,
  threshold = 0.93,
}) => {
  const { gl, scene, camera, size } = useThree();
  const composer = useMemo(() => {
    const c = new EffectComposer(gl);
    c.addPass(new RenderPass(scene, camera));
    c.addPass(new UnrealBloomPass(new THREE.Vector2(size.width, size.height), strength, radius, threshold));
    c.addPass(new OutputPass());
    return c;
  }, [gl, scene, camera, size.width, size.height, strength, radius, threshold]);
  useEffect(() => {
    composer.setPixelRatio(gl.getPixelRatio());
    composer.setSize(size.width, size.height);
  }, [composer, gl, size]);
  useFrame(() => composer.render(), 1);
  return null;
};

const canvasTex = (key: string, w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, repeat: [number, number] = [1, 1]) => {
  const cache = canvasTex as unknown as { m?: Map<string, THREE.CanvasTexture> };
  cache.m ??= new Map();
  if (!cache.m.has(key)) {
    const c = document.createElement("canvas");
    c.width = w;
    c.height = h;
    draw(c.getContext("2d")!);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(...repeat);
    t.anisotropy = 8;
    cache.m.set(key, t);
  }
  return cache.m.get(key)!;
};

const speckle = (g: CanvasRenderingContext2D, w: number, h: number, base: string, n: number, colors: string[], seed: string, max = 3) => {
  g.fillStyle = base;
  g.fillRect(0, 0, w, h);
  for (let i = 0; i < n; i++) {
    g.fillStyle = colors[i % colors.length];
    g.globalAlpha = 0.25 + random(`${seed}a${i}`) * 0.5;
    const r = 0.5 + random(`${seed}r${i}`) * max;
    g.beginPath();
    g.arc(random(`${seed}x${i}`) * w, random(`${seed}y${i}`) * h, r, 0, Math.PI * 2);
    g.fill();
  }
  g.globalAlpha = 1;
};

export const TEX = {
  soil: (rep: [number, number] = [6, 6]) =>
    canvasTex(`soil${rep}`, 512, 512, (g) => speckle(g, 512, 512, "#3a2a1e", 5000, ["#24180f", "#5a4330", "#1a120b", "#6b5440"], "soil", 3), rep),
  grass: (rep: [number, number] = [8, 8]) =>
    canvasTex(`grass${rep}`, 512, 512, (g) => speckle(g, 512, 512, "#22301c", 6000, ["#2f4425", "#18220f", "#3c5530", "#2a2a18"], "grass", 2), rep),
  concrete: (rep: [number, number] = [6, 6]) =>
    canvasTex(`conc${rep}`, 512, 512, (g) => speckle(g, 512, 512, "#3b4048", 4000, ["#2d3138", "#4a5059", "#353a41"], "conc", 2.5), rep),
  stone: () =>
    canvasTex("stone", 256, 256, (g) => {
      speckle(g, 256, 256, "#8a8f95", 2500, ["#6d7278", "#a3a8ad", "#7b8086"], "stone", 1.5);
      g.strokeStyle = "rgba(60,64,70,0.35)";
      for (let i = 0; i < 6; i++) {
        g.lineWidth = 1 + random(`sv${i}`) * 1.5;
        g.beginPath();
        g.moveTo(random(`sa${i}`) * 256, 0);
        g.bezierCurveTo(random(`sb${i}`) * 256, 90, random(`sc${i}`) * 256, 170, random(`sd${i}`) * 256, 256);
        g.stroke();
      }
    }),
  wood: (dark = false) =>
    canvasTex(`wood${dark}`, 512, 128, (g) => {
      g.fillStyle = dark ? "#2e1a0f" : "#5a341c";
      g.fillRect(0, 0, 512, 128);
      for (let i = 0; i < 70; i++) {
        g.strokeStyle = i % 2 ? "rgba(20,10,4,0.35)" : "rgba(140,90,50,0.25)";
        g.lineWidth = 0.5 + random(`wl${i}`) * 2;
        const y = random(`wy${i}`) * 128;
        g.beginPath();
        g.moveTo(0, y);
        for (let x = 0; x <= 512; x += 32) g.lineTo(x, y + Math.sin(x * 0.02 + i) * 3);
        g.stroke();
      }
    }),
  marble: () =>
    canvasTex("marble", 256, 256, (g) => {
      speckle(g, 256, 256, "#1f2228", 1200, ["#2b2f36", "#15171b"], "mar", 2);
      g.strokeStyle = "rgba(200,200,210,0.18)";
      for (let i = 0; i < 8; i++) {
        g.lineWidth = 0.6 + random(`mv${i}`);
        g.beginPath();
        g.moveTo(0, random(`ma${i}`) * 256);
        g.bezierCurveTo(90, random(`mb${i}`) * 256, 170, random(`mc${i}`) * 256, 256, random(`md${i}`) * 256);
        g.stroke();
      }
    }),
  // zacht rond puntje voor deeltjes en gloed
  dot: () =>
    canvasTex("dot", 64, 64, (g) => {
      const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
      r.addColorStop(0, "rgba(255,255,255,1)");
      r.addColorStop(0.35, "rgba(255,255,255,0.6)");
      r.addColorStop(1, "rgba(255,255,255,0)");
      g.fillStyle = r;
      g.fillRect(0, 0, 64, 64);
    }),
  // vlam: verloop van wit-geel onderin naar transparant oranje bovenin
  flame: () =>
    canvasTex("flame", 32, 256, (g) => {
      const l = g.createLinearGradient(0, 256, 0, 0);
      l.addColorStop(0, "rgba(255,250,220,1)");
      l.addColorStop(0.25, "rgba(255,200,80,0.95)");
      l.addColorStop(0.6, "rgba(255,100,20,0.6)");
      l.addColorStop(1, "rgba(180,30,0,0)");
      g.fillStyle = l;
      g.fillRect(0, 0, 32, 256);
    }),
};

// Zachte gloed (sprite) – bijvoorbeeld rond vuur of een scherm
export const Glow: React.FC<{ position: [number, number, number]; size: number; color: string; opacity?: number }> = ({
  position,
  size,
  color,
  opacity = 0.6,
}) => (
  <sprite position={position} scale={[size, size, 1]}>
    <spriteMaterial map={TEX.dot()} color={color} transparent opacity={opacity} depthWrite={false} blending={THREE.AdditiveBlending} />
  </sprite>
);
