// AUTO BLOCK aurora: northern lights - glowing green curtains with purple tops that ripple across the night sky
// (solar storm, Earth losing its magnetic field). Optionally turns the place into a dark night first.
// Use in scenario.js:  auto: [{ block: 'aurora', from: 8, full: 20, until: 1e9, strength: 1, az: 0, night: true }]
//   from/full/until: s (fades in from -> full, gone after until); strength 0..1.5 (1.5 = a once-in-centuries storm,
//   reaching overhead and turning red); az: centre direction in radians (0 = -z, + = towards +x); night: dark sky.
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE, R = rng(23), C = h => new THREE.Color(h);
  const from = o.from ?? 0, full = o.full ?? from + 12, until = o.until ?? 1e9, max = o.strength ?? 1, az0 = o.az ?? 0;
  const level = t => t < from || t > until + 3 ? 0 : Math.min(1, (t - from) / Math.max(.1, full - from)) * max * (t > until ? 1 - (t - until) / 3 : 1);
  const DIST = 2600, COLS = 90, group = new THREE.Group(); E.scene.add(group);
  // 5 curtains: ribbons hanging from the sky, bottom green, top purple (red in a big storm); additive glow
  const curtains = [];
  for (let k = 0; k < 5; k++) {
    const geo = new THREE.BufferGeometry(), pos = new Float32Array((COLS + 1) * 2 * 3), col = new Float32Array((COLS + 1) * 2 * 3), idx = [];
    for (let i = 0; i < COLS; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    geo.setIndex(idx); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const mat = new THREE.MeshBasicMaterial({ vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false, side: THREE.DoubleSide });
    const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false; mesh.renderOrder = -1; group.add(mesh);
    curtains.push({ geo, pos, col, az: az0 + (k - 2) * .38 + (R() - .5) * .2, width: .55 + R() * .35, el: .14 + R() * .1, h: .16 + R() * .12, ph: R() * 6, sp: .12 + R() * .1 });
  }
  if (o.night) (E.lookMods ||= []).push((t, L) => {       // a clear dark night, lit faintly by the aurora itself
    const g = Math.min(1, level(t));
    L.top = C(0x050a14); L.hor = C(0x0b1626).lerp(C(0x123a2c), g * .5); L.stars = 1; L.fogColor = C(0x0a1422).lerp(C(0x10302a), g * .4);
    L.hemi = .5 + g * .5; L.hemiColor = C(0x6a8aa0).lerp(C(0x5fd39a), g * .5); L.groundColor = C(0x1c1e22);
    L.sun = .35; L.sunColor = C(0x9fb8d8); L.sunDisc = C(0); L.dark = 1; L.haze = 0; L.dustLight = .5;
  });
  const green = C(0x37f08a), top = C(0x9a5cff), red = C(0xff4a5a), tmp = new THREE.Color();
  return (t, tv) => {
    const k = level(t); group.visible = k > .01; if (!group.visible) return;
    const c = E.camera.position; group.position.copy(c);
    const storm = Math.max(0, Math.min(1, (k - 1) * 2)), topC = top.clone().lerp(red, storm);
    for (const q of curtains) {
      for (let i = 0; i <= COLS; i++) {
        const u = i / COLS, a = q.az + (u - .5) * q.width * (1 + storm * .6);
        const wave = Math.sin(u * 9 + tv * q.sp * 6 + q.ph) * .025 + Math.sin(u * 23 - tv * q.sp * 9) * .01;   // ripples run along it
        const el0 = q.el + wave + storm * .25, el1 = el0 + q.h * (1 + storm) * (.7 + .3 * Math.sin(u * 5 + tv * .7 + q.ph));
        const fade = Math.sin(u * Math.PI) ** 1.5 * (.55 + .45 * Math.sin(u * 13 + tv * q.sp * 4 + q.ph)) * Math.min(1, k);
        for (const [j, el, cc] of [[0, el0, green], [1, el1, topC]]) {
          const p = (i * 2 + j) * 3, ce = Math.cos(el) * DIST;
          q.pos[p] = Math.sin(a) * ce; q.pos[p + 1] = Math.sin(el) * DIST - c.y; q.pos[p + 2] = -Math.cos(a) * ce;
          tmp.copy(cc).multiplyScalar(fade * (j ? .55 : 1)); q.col[p] = tmp.r; q.col[p + 1] = tmp.g; q.col[p + 2] = tmp.b;
        }
      }
      q.geo.attributes.position.needsUpdate = q.geo.attributes.color.needsUpdate = true;
    }
  };
}
