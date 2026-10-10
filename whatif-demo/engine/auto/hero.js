// AUTO BLOCK hero: "you" - one person close to the camera that the story happens to, with poses over time:
// stand, hair (hair stands on end, arms a little out: charged air), brace (arms up, shielding), struck (lit up from
// inside, sparks crawl over the skin), fall (falls backwards), lie (on the ground), marks (branching red Lichtenberg
// marks on the skin, for a close-up afterwards). Other blocks can use E.hero (head position) as a target.
// Use in scenario.js:  auto: [{ block: 'hero', pos: [0, 0, 20], face: 0, coat: 0x2c4f9e,
//                              poses: [[0, 'stand'], [at('hair').s, 'hair'], [at('hit').s, 'struck'], [at('hit').s + 1.2, 'fall'], [at('marks').s, 'marks']] }]
//   pos: feet on the ground (y follows the ground); face: direction the hero looks (radians, 0 = towards -z);
//   poses: [[t, pose], ...]; 'marks' keeps the hero lying and shows the marks.
//   Gives the director standpoints: auto-hero-back (over the shoulder), auto-hero-close (face), auto-hero-wide.
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE, R = rng(83), lam = E.lam, S = m => E.shadowed(m);
  const [x, , z] = o.pos ?? [0, 0, 0], gy = E.groundAt?.(x, z) ?? 0, face = o.face ?? 0;
  const skin = lam(o.skin ?? 0xa86f4c), coat = lam(o.coat ?? 0x2c4f9e), pants = lam(o.pants ?? 0x8a6a4a), hairM = lam(o.hair ?? 0x1d1712);
  const root = new THREE.Group(); root.position.set(x, gy, z); root.rotation.y = face; E.scene.add(root);
  const body = new THREE.Group(); root.add(body);                       // tilts as a whole when falling
  const box = (w, h, d, m, px, py, pz, parent = body) => { const b = S(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m)); b.position.set(px, py, pz); parent.add(b); return b; };
  // legs and torso (blocky, a little stylised, real size ~1.78 m)
  const legs = [-1, 1].map(s => { const g = new THREE.Group(); g.position.set(s * .11, .86, 0); body.add(g); box(.16, .84, .2, pants, 0, -.42, 0, g); box(.17, .08, .28, lam(0x222222), 0, -.84, -.04, g); return g; });
  const torso = box(.5, .62, .28, coat, 0, 1.18, 0);
  const arms = [-1, 1].map(s => { const g = new THREE.Group(); g.position.set(s * .32, 1.44, 0); body.add(g); box(.13, .6, .15, coat, 0, -.28, 0, g); box(.11, .14, .12, skin, 0, -.62, 0, g); return g; });
  const head = new THREE.Group(); head.position.set(0, 1.62, 0); body.add(head);
  box(.24, .28, .25, skin, 0, 0, 0, head); box(.25, .07, .26, hairM, 0, .15, .01, head);
  // hair: short spikes that stand up when the air is charged
  const spikes = [];
  for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2, r = .07 + (i % 3) * .025, s = box(.035, .12, .035, hairM, Math.cos(a) * r, .2, Math.sin(a) * r, head); spikes.push({ m: s, a, r }); }
  // glow when struck: a slightly larger white shell around every part, additive
  const glowMat = new THREE.MeshBasicMaterial({ color: 0x7f9dff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
  const glows = [];
  const parts = []; body.traverse(m => { if (m.isMesh) parts.push(m); });   // collect first: adding while traversing never ends
  for (const m of parts) { const g = new THREE.Mesh(m.geometry, glowMat); g.scale.setScalar(1.08); m.add(g); glows.push(g); }
  // sparks crawling over the skin: short jagged line segments, regenerated every frame from a seed (deterministic)
  const NS = 60, spk = new Float32Array(NS * 6), sparkGeo = new THREE.BufferGeometry(); sparkGeo.setAttribute('position', new THREE.BufferAttribute(spk, 3));
  const sparks = new THREE.LineSegments(sparkGeo, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .95, blending: THREE.AdditiveBlending, depthWrite: false }));
  sparks.frustumCulled = false; body.add(sparks);
  // Lichtenberg marks: branching lines on the back and arm (fern pattern), seen in a close-up
  const marks = new THREE.Group(); marks.visible = false; body.add(marks);
  { const pts = [], grow = (px, py, ang, len, depth) => {
      if (depth > 5 || len < .01) return;
      const qx = px + Math.cos(ang) * len, qy = py + Math.sin(ang) * len; pts.push(px, py, 0, qx, qy, 0);
      grow(qx, qy, ang + (R() - .5) * .5, len * .78, depth + 1);
      if (R() < .75) grow(qx, qy, ang + (R() < .5 ? -1 : 1) * (.5 + R() * .5), len * .6, depth + 1);
    };
    for (let k = 0; k < 5; k++) grow((R() - .5) * .1, .95 + R() * .05, -Math.PI / 2 + (R() - .5) * 1.4, .09, 0);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
    const lm = new THREE.LineBasicMaterial({ color: 0xc8564a });
    const back = new THREE.LineSegments(g, lm); back.position.set(0, .28, .145); marks.add(back);      // on the back of the torso
    const front = new THREE.LineSegments(g, lm); front.position.set(0, .28, -.145); marks.add(front);
  }
  const poses = (o.poses || [[0, 'stand']]).slice().sort((a, b) => a[0] - b[0]);
  const poseAt = t => { let p = poses[0], prev = null; for (const q of poses) { if (t >= q[0]) { prev = p; p = q; } } return { name: p[1], since: t - p[0] }; };
  const fallAt = (poses.find(p => p[1] === 'fall') || [1e9])[0];
  // where other blocks aim (lightning): the top of the head, in world coordinates
  const headWorld = new THREE.Vector3();
  E.hero = { root, headAt: () => { root.updateMatrixWorld(true); return head.getWorldPosition(headWorld).clone(); }, pos: [x, gy, z] };
  E.hero.top = [x, gy + 1.85, z]; E.hero.face = face;
  const smooth = (a, b, v) => { const u = Math.min(1, Math.max(0, (v - a) / (b - a))); return u * u * (3 - 2 * u); };
  return (t, tv) => {
    const { name, since } = poseAt(t);
    const hair = name === 'hair' ? smooth(0, 1.5, since) : name === 'brace' || name === 'struck' ? 1 : 0;
    for (const s of spikes) { s.m.scale.y = 1 + 1.6 * hair; s.m.position.y = .2 + .16 * hair; s.m.rotation.set(Math.sin(s.a) * .5 * hair, 0, -Math.cos(s.a) * .5 * hair); }
    // arms: a little out when charged, up when bracing, flung out when struck
    const out = name === 'hair' ? .25 * smooth(0, 1.5, since) : name === 'struck' ? .9 : name === 'brace' ? .4 : 0, up = name === 'brace' ? 2.4 : 0;
    arms.forEach((a, i) => { a.rotation.z = (i ? 1 : -1) * out; a.rotation.x = -up; });
    // struck: glow flickers, sparks over the body
    const lit = name === 'struck' ? Math.max(0, 1 - since * .8) * (.6 + .4 * Math.abs(Math.sin(tv * 60))) : 0;
    glowMat.opacity = .45 * lit; sparks.visible = lit > .05;
    if (sparks.visible) {
      const r2 = rng(1 + Math.floor(tv * 30));
      for (let i = 0; i < NS; i++) { const j = i * 6, px = (r2() - .5) * .6, py = .1 + r2() * 1.7, pz = (r2() < .5 ? -1 : 1) * .17;
        spk[j] = px; spk[j + 1] = py; spk[j + 2] = pz; spk[j + 3] = px + (r2() - .5) * .25; spk[j + 4] = py + (r2() - .5) * .25; spk[j + 5] = pz; }
      sparkGeo.attributes.position.needsUpdate = true;
    }
    // falling backwards and lying still
    const f = smooth(fallAt, fallAt + .9, t);
    body.rotation.x = 1.5 * f; body.position.y = .12 * f; body.position.z = .4 * f;
    legs.forEach((l, i) => { l.rotation.x = (i ? .15 : -.1) * f; });
    marks.visible = name === 'marks' || (name === 'lie' && poses.some(p => p[1] === 'marks' && p[0] <= t));
  };
}
