// Optional "film look" (TL.post): soft ambient occlusion, a gentle glow on bright lights, warm/cool grade,
// a little haze contrast and a vignette, ACES tone mapping. Off unless the scenario sets post: true (or an object).
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const Grade = {
  uniforms: { tDiffuse: { value: null }, contrast: { value: 1.08 }, saturation: { value: 1.12 }, vignette: { value: .32 },
              lift: { value: new THREE.Vector3(.0, .005, .02) }, gain: { value: new THREE.Vector3(1.03, 1.0, .97) } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform float contrast, saturation, vignette; uniform vec3 lift, gain; varying vec2 vUv;
    void main(){ vec4 c = texture2D(tDiffuse, vUv); vec3 x = c.rgb * gain + lift * (1. - c.rgb);
      float l = dot(x, vec3(.2126, .7152, .0722)); x = mix(vec3(l), x, saturation); x = (x - .5) * contrast + .5;
      vec2 d = vUv - .5; x *= 1. - vignette * smoothstep(.25, .85, length(d * vec2(1.15, 1.)));
      gl_FragColor = vec4(clamp(x, 0., 1.), c.a); }`,
};

export function createPost(E, W, H, opt = {}) {
  const r = E.renderer;
  r.shadowMap.type = opt.softShadows ? THREE.VSMShadowMap : THREE.PCFSoftShadowMap; r.shadowMap.needsUpdate = true;
  if (opt.softShadows) { E.sun.shadow.radius = 3; E.sun.shadow.blurSamples = 16; E.sun.shadow.map?.dispose(); E.sun.shadow.map = null; }
  r.toneMapping = opt.tone === 'agx' ? THREE.AgXToneMapping : THREE.ACESFilmicToneMapping;
  const comp = new EffectComposer(r, new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 }));
  comp.setPixelRatio(1); comp.setSize(W, H);
  comp.addPass(new RenderPass(E.scene, E.camera));
  if (opt.ao !== false) { const ao = new GTAOPass(E.scene, E.camera, W, H); ao.blendIntensity = opt.ao ?? .85; comp.addPass(ao); }
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), opt.bloom ?? .45, .55, .82); comp.addPass(bloom);
  comp.addPass(new OutputPass());
  const grade = new ShaderPass(Grade); if (opt.vignette != null) grade.uniforms.vignette.value = opt.vignette;
  if (opt.saturation != null) grade.uniforms.saturation.value = opt.saturation;
  if (opt.contrast != null) grade.uniforms.contrast.value = opt.contrast;
  comp.addPass(grade);
  return { render: () => comp.render(), bloom };
}
