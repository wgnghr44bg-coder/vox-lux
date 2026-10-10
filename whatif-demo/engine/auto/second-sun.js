// AUTO BLOCK second-sun: a second sun in the sky - a bright disc with a glow that rises or appears, adds its own
// warm light (a second set of soft shadows) and makes the day brighter and hotter-looking (two suns, a star
// passing close). Works with any place and force; pair it with the heat force for a burning world.
// Use in scenario.js:  auto: [{ block: 'second-sun', from: 6, full: 14, until: 1e9, az: 1.1, el: .35, size: 1, color: 0xffc27a, light: 1 }]
//   from/full/until: s it appears / is at full strength / fades; az: direction in radians (0 = -z, + = towards +x);
//   el: height above the horizon in radians; size: 1 = as big as our Sun; color: its colour (orange = cooler star);
//   rise: [el0, el1] instead of el lets it climb between from and full.
export default function build(E, TL, o, F) {
  const THREE = E.THREE, C = h => new THREE.Color(h);
  const from = o.from ?? 0, full = o.full ?? from + 8, until = o.until ?? 1e9, az = o.az ?? 1.1, col = C(o.color ?? 0xffc27a);
  const level = t => t < from ? 0 : Math.min(1, (t - from) / Math.max(.1, full - from)) * (t > until ? Math.max(0, 1 - (t - until) / 4) : 1);
  const elAt = t => o.rise ? o.rise[0] + (o.rise[1] - o.rise[0]) * Math.min(1, Math.max(0, (t - from) / Math.max(.1, full - from))) : (o.el ?? .35);
  const DIST = 3000, ang = .0093 * (o.size ?? 1) * 3.2;            // our Sun is 0.53 degrees; drawn larger, as the eye (and a film) sees it
  const sky = new THREE.Group(); E.scene.add(sky);
  const disc = new THREE.Mesh(new THREE.CircleGeometry(DIST * ang, 32), new THREE.MeshBasicMaterial({ color: 0xfffaf0, fog: false, depthWrite: false }));
  const glow = new THREE.Mesh(new THREE.CircleGeometry(DIST * ang * 6, 48), new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
    uniforms: { col: { value: col }, k: { value: 0 } },
    vertexShader: 'varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'uniform vec3 col; uniform float k; varying vec2 vUv; void main() { float d = length(vUv - 0.5) * 2.0; float a = (pow(max(0.0, 1.0 - d), 3.0) * 1.4 + pow(max(0.0, 1.0 - d * 4.0), 1.5)) * k; gl_FragColor = vec4(col * a, a); }' }));
  disc.renderOrder = glow.renderOrder = -2; sky.add(glow); sky.add(disc);
  const light = new THREE.DirectionalLight(col, 0); light.castShadow = false; E.scene.add(light); E.scene.add(light.target);
  const dirAt = t => { const el = elAt(t); return new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)); };
  // the sky and the light: brighter, warmer, a glow on that side of the horizon
  (E.lookMods ||= []).push((t, L) => {
    const k = level(t); if (k <= 0) return;
    L.hor = L.hor.clone().lerp(col.clone().lerp(C(0xffffff), .5), .35 * k); L.top = L.top.clone().lerp(C(0x7fa6cf), .25 * k);
    L.hemi = (L.hemi ?? 1.4) + .5 * k * (o.light ?? 1); L.hemiColor = (L.hemiColor ?? C(0xffffff)).clone().lerp(col, .35 * k);
    L.fogColor = (L.fogColor || L.hor).clone().lerp(col.clone().lerp(C(0xffffff), .6), .25 * k); L.stars = (L.stars ?? 0) * (1 - k);
    L.dark = (L.dark ?? 0) * (1 - k);
  });
  return (t, tv) => {
    const k = level(t); sky.visible = k > .01; light.intensity = 2.2 * k * (o.light ?? 1); if (!sky.visible) return;
    const c = E.camera.position, d = dirAt(t);
    sky.position.copy(c).addScaledVector(d, DIST); sky.lookAt(c);
    disc.scale.setScalar(.4 + .6 * k); glow.material.uniforms.k.value = k;
    light.position.copy(c).addScaledVector(d, 200); light.target.position.copy(c);
  };
}
