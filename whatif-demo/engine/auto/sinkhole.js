// AUTO BLOCK sinkhole: the ground opens - a round hole grows in a street or square, its edge breaks off and falls
// in, dust rises; the inside shows layered earth walls and darkness below.
// Use in scenario.js:  auto: [{ block: 'sinkhole', pos: [0, 0, -60], at: 12, open: 8, r: 18, depth: 45 }]
//   pos: centre on the ground; at: s it starts (first cracks); open: s until it reaches radius r (metres);
//   depth: metres. Cars and people standing where the hole opens tip over and drop in (swallow: false switches
//   that off). Gives E.EVENTS { kind: 'collapse' } (rumble, sound) when it opens.
// How the hole is drawn: the ground is one flat surface, so the mouth marks its pixels in the stencil buffer and
// the walls and the bottom are drawn only there (anything standing in front of the hole stays in front).
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE, R = rng(57);
  const [cx, cy0, cz] = o.pos ?? [0, 0, 0], cy = (E.groundAt?.(cx, cz) ?? cy0) + .06;
  const at = o.at ?? 0, open = o.open ?? 8, RMAX = o.r ?? 18, D = o.depth ?? 45;
  const rAt = t => t < at ? 0 : RMAX * (1 - Math.pow(1 - Math.min(1, (t - at) / open), 2.2)) ;   // fast first, then slower
  const g = new THREE.Group(); g.position.set(cx, cy, cz); E.scene.add(g);
  // 1. the mouth: invisible, only writes 1 into the stencil where the ground is visible
  const mouthMat = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false, stencilWrite: true, stencilRef: 1,
    stencilFunc: THREE.AlwaysStencilFunc, stencilZPass: THREE.ReplaceStencilOp });
  const mouth = new THREE.Mesh(new THREE.CircleGeometry(1, 28), mouthMat); mouth.rotation.x = -Math.PI / 2; mouth.renderOrder = 50; g.add(mouth);
  // 2. inside the mouth the depth is reset to 'far away', so the walls and bottom can hide each other normally
  const resetMat = new THREE.ShaderMaterial({ colorWrite: false, depthWrite: true, depthFunc: THREE.AlwaysDepth,
    stencilWrite: true, stencilRef: 1, stencilFunc: THREE.EqualStencilFunc,
    vertexShader: 'void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: 'void main() { gl_FragDepth = 1.0; gl_FragColor = vec4(0.0); }' });
  const reset = new THREE.Mesh(mouth.geometry, resetMat); reset.rotation.x = -Math.PI / 2; reset.renderOrder = 51; g.add(reset);
  // 3. inside (only where the stencil is 1): earth walls and a dark bottom, with a normal depth test
  const inside = (o2 = {}) => new THREE.MeshBasicMaterial({ vertexColors: true, fog: false,
    stencilWrite: true, stencilRef: 1, stencilFunc: THREE.EqualStencilFunc, ...o2 });
  const bottom = new THREE.Mesh(new THREE.CircleGeometry(1, 28), inside()); bottom.rotation.x = -Math.PI / 2; bottom.renderOrder = 52; g.add(bottom);
  { const c = new Float32Array(bottom.geometry.attributes.position.count * 3).fill(.05); bottom.geometry.setAttribute('color', new THREE.BufferAttribute(c, 3)); }
  const SEG = 28, RINGS = 8, wallGeo = new THREE.CylinderGeometry(1, 1, 1, SEG, RINGS, true); wallGeo.translate(0, -.5, 0);
  { // earth layers: asphalt/paving on top, brown and ochre bands, darker with depth (and a little uneven)
    const p = wallGeo.attributes.position, c = new Float32Array(p.count * 3), bands = [0x6e6a64, 0x9a7650, 0xb08a5c, 0x8c6844, 0x9c8060, 0x7a5c40, 0x5e4732, 0x3a2d20];
    for (let i = 0; i < p.count; i++) {
      const d = -p.getY(i), b = Math.min(bands.length - 1, Math.floor(d * bands.length)), col = new THREE.Color(bands[b]);
      col.multiplyScalar(Math.exp(-d * 7) * (.8 + R() * .4) + .002);          // dark fast with depth: it looks deep
      c[i * 3] = col.r; c[i * 3 + 1] = col.g; c[i * 3 + 2] = col.b;
      if (p.getY(i) < -.01 && p.getY(i) > -.99) { const a = Math.atan2(p.getZ(i), p.getX(i)), w = 1 + (R() - .5) * .14; p.setX(i, Math.cos(a) * w); p.setZ(i, Math.sin(a) * w); }
    }
    wallGeo.setAttribute('color', new THREE.BufferAttribute(c, 3));
  }
  const wall = new THREE.Mesh(wallGeo, inside({ side: THREE.BackSide })); wall.renderOrder = 52; g.add(wall);
  // 4. the edge breaking off: chunks of road/earth tip over the rim and drop in
  const NC = 90, chunks = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), E.lam(0x575450), NC); chunks.castShadow = true; g.add(chunks);
  const CH = [];
  for (let i = 0; i < NC; i++) { const a = R() * Math.PI * 2, rr = RMAX * (.15 + .85 * Math.sqrt(R())); CH.push({ a, rr, s: [1 + R() * 2.5, .5 + R() * .8, 1 + R() * 2], spin: (R() - .5) * 4, tFall: null }); }
  for (const c of CH) { let lo = at, hi = at + open; for (let k = 0; k < 30; k++) { const m = (lo + hi) / 2; if (rAt(m) < c.rr) lo = m; else hi = m; } c.tFall = hi; }
  (E.EVENTS ||= []).push({ t: at + .3, kind: 'collapse', e: 1.6, x: cx, z: cz });
  // dust rising out of the hole while it grows
  (E.emitters ||= []).push((tv, add) => {
    const t = Math.min(tv, TL.beats.stop), r = rAt(t), grow = t > at && t < at + open + 3 ? 1 - Math.max(0, t - at - open) / 3 : 0;
    if (grow <= 0) return;
    for (let k = 0; k < 10; k++) {
      const ph = ((tv * .4 + k * .1) % 1), a = k * 2.4 + Math.floor(tv * .4) * 1.3, rr = r * (.4 + .6 * ((k * 37) % 10) / 10);
      add(cx + Math.cos(a) * rr, cy + 1 + ph * (8 + r * .8), cz + Math.sin(a) * rr, 4 + ph * 8, Math.sin(ph * Math.PI) * .45 * grow, .55, .47, .38, k);
    }
  });
  // when the edge reaches a distance (inverse of rAt): for things that fall in
  const tAt = dist => { if (dist >= RMAX) return 1e9; let lo = at, hi = at + open; for (let k = 0; k < 30; k++) { const m = (lo + hi) / 2; if (rAt(m) < dist) lo = m; else hi = m; } return hi; };
  const swallow = (obj, t) => {          // runs after the engine posed it this frame: tip over towards the centre and drop
    const x = obj.position.x - cx, z = obj.position.z - cz, d = Math.hypot(x, z), dt = t - tAt(d);
    if (dt <= 0) return;
    obj.position.y -= 4.9 * dt * dt; obj.rotation.x += Math.min(1.3, dt * 1.6) * (z > 0 ? -1 : 1) * .8; obj.rotation.z += Math.min(1.3, dt * 1.6) * (x > 0 ? 1 : -1) * .5;
    if (obj.position.y < cy - 25) obj.visible = false;
  };
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), sc = new THREE.Vector3(), p = new THREE.Vector3();
  return (t, tv) => {
    if (o.swallow !== false && t > at) {
      for (const b of E.bodies) if (b.obj && b.kind === 'car' && b.obj.visible) swallow(b.obj, Math.min(t, TL.beats.stop));
      for (const pp of E.people || []) if (pp.g?.visible) swallow(pp.g, Math.min(t, TL.beats.stop));
    }
    const r = rAt(Math.min(t, TL.beats.stop)); g.visible = r > .05; if (!g.visible) return;
    mouth.scale.set(r, r, 1); reset.scale.set(r, r, 1); bottom.scale.set(r * .92, r * .92, 1); bottom.position.y = -D; wall.scale.set(r, D, r);
    CH.forEach((c, i) => {
      const dt = t - c.tFall; let y = 0, tilt = 0, out = 0;
      if (dt > 0) { tilt = Math.min(1.4, dt * 1.6); y = -4.9 * dt * dt; out = Math.min(2, dt * 1.5); }
      const show = c.tFall < at + open + 5 && (dt > 0 ? y > -6 : true) && t >= at - 1;   // vanish once it is in the dark
      p.set(Math.cos(c.a) * (c.rr - out), y + c.s[1] * .5 - .3, Math.sin(c.a) * (c.rr - out));
      e.set(Math.sin(c.a) * tilt, c.spin * Math.max(0, dt) * .3, -Math.cos(c.a) * tilt); q.setFromEuler(e);
      sc.set(...c.s).multiplyScalar(show && dt > -0.5 && dt < 2 ? 1 : 0);                    // only the rim pieces near the edge show
      m4.compose(p, q, sc); chunks.setMatrixAt(i, m4);
    });
    chunks.instanceMatrix.needsUpdate = true;
  };
}
