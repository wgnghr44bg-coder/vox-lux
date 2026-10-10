// AUTO BLOCK rain: falling rain streaks around the camera, from a drizzle to a downpour.
// Use in scenario.js:  auto: [{ block: 'rain', from: 4, full: 20, until: 1e9, strength: 1 }]
//   from: s when the first drops fall; full: s when it pours (strength 0..1.5); until: s when it stops.
//
// ---- HOW AN AUTO BLOCK WORKS (every file in engine/auto/ follows this; the example is this file) ----
// export default function build(E, TL, o, F) is called once while the scene is built.
//   E.THREE        three.js;  E.scene: add your objects here;  E.camera: the camera (position follows the shots)
//   E.lam(color)   flat-shaded low-poly material (always use it, matte colours, no neon);  E.shadowed(mesh)
//   E.groundAt?.(x, z)  ground height at x, z (if the place gives it);  F.field(t).waterY: water height at time t
//   o              the entry from TL.auto (your own options, e.g. pos: [x, y, z], at: seconds)
// It may return update(t, tv): called every frame with the video time t (t stops at the end of the story, tv runs on).
// Rules: low-poly (few faces, flat shading), real scale in metres, deterministic (no Math.random: use a seeded rng
// like below), no heavy loops per frame (< 5000 objects; use InstancedMesh or one geometry for many small things).
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE, N = 6000, R = rng(17), SPAN = 60, TOP = 26;
  const from = o.from ?? 0, full = o.full ?? from + 10, until = o.until ?? 1e9, max = o.strength ?? 1;
  // one geometry with N short line segments (streaks), moved as a whole around the camera
  const pos = new Float32Array(N * 6), base = [];
  for (let i = 0; i < N; i++) base.push([(R() - .5) * SPAN, R() * TOP, (R() - .5) * SPAN, 1.1 + R() * .9]);
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.LineBasicMaterial({ color: 0xc9d3da, transparent: true, opacity: .55, fog: true });
  const lines = new THREE.LineSegments(geo, mat); lines.frustumCulled = false; E.scene.add(lines);
  const level = t => t < from || t > until ? 0 : Math.min(1, (t - from) / Math.max(.1, full - from)) * max;
  return (t, tv) => {
    const k = level(t); lines.visible = k > 0.02; if (!lines.visible) return;
    const c = E.camera.position, n = Math.floor(N * Math.min(1, k)), fall = 14 * tv, slant = .18;
    for (let i = 0; i < N; i++) {
      const j = i * 6;
      if (i >= n) { pos.fill(0, j, j + 6); continue; }
      const [x, y0, z, len] = base[i], y = ((y0 - fall) % TOP + TOP) % TOP + c.y - 6;
      const wrap = v => ((v % SPAN) + SPAN * 1.5) % SPAN - SPAN / 2;          // keep every drop in a box around the camera
      const px = c.x + wrap(x - c.x), pz = c.z + wrap(z - c.z);
      pos[j] = px; pos[j + 1] = y; pos[j + 2] = pz; pos[j + 3] = px + slant * len; pos[j + 4] = y - len * (1 + k * .6); pos[j + 5] = pz;
    }
    geo.attributes.position.needsUpdate = true; mat.opacity = .45 + .35 * Math.min(1, k);
  };
}
