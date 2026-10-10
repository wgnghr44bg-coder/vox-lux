// AUTO BLOCK lightning: a real lightning strike in all its stages, slow enough to see (slow motion is up to the story):
// 1. the stepped leader: a faint violet channel that steps down from the cloud in jumps of ~50 m, branching;
// 2. the upward streamer: a short spark that rises from the target (a person, a tree, a tower) to meet it;
// 3. the return stroke: the whole channel blazes white, the scene flashes, thunder (E.EVENTS 'thunder');
// 4. restrikes: the same channel flashes again (dt seconds later); then it fades.
// Use in scenario.js:  auto: [{ block: 'lightning', target: 'hero', at: 30, leader: 4, streamer: 1, restrikes: [.4, 1.1] }]
//   target: 'hero' (the hero's head, see hero.js) or [x, y, z]; at: s of the return stroke (the flash);
//   leader: s the stepped leader takes to come down (slow motion: 2-8 s); streamer: s the upward spark grows before it;
//   restrikes: extra flashes after `at`; from: [x, y, z] in the cloud (default 700 m above, a little to the side);
//   width: 1 = normal; seed: another shape. Several entries = several strikes (e.g. far away earlier in the story).
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE, R = rng(o.seed ?? 97);
  const at = o.at ?? 10, leader = o.leader ?? 3, streamT = o.streamer ?? .8, restrikes = o.restrikes ?? [.35];
  const tgt = o.target === 'hero' && E.hero ? E.hero.top : (Array.isArray(o.target) ? o.target : [0, (E.groundAt?.(0, 0) ?? 0), 0]);
  // from the cloud base (so the whole leader is visible), in front of the hero (where its cameras look), else towards -z
  const fa = E.hero && o.target === 'hero' ? E.hero.face ?? 0 : 0, ahead = 60 + R() * 70, side = (R() - .5) * 80;
  const from = o.from ?? [tgt[0] - Math.sin(fa) * ahead + Math.cos(fa) * side, tgt[1] + 330, tgt[2] - Math.cos(fa) * ahead - Math.sin(fa) * side];
  // the channel: a jagged path from the cloud down to the target (midpoint displacement), plus branches
  const jag = (a, b, depth, rough) => {
    if (depth === 0) return [a, b];
    const m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2], L = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
    m[0] += (R() - .5) * L * rough; m[1] += (R() - .5) * L * rough * .3; m[2] += (R() - .5) * L * rough;
    const l = jag(a, m, depth - 1, rough), r = jag(m, b, depth - 1, rough); return l.concat(r.slice(1));
  };
  const main = jag(from, tgt, 7, .5);                                    // 129 points from top to bottom
  const segs = [];                                                       // [p, q, order along the way 0..1, width, isMain]
  for (let i = 0; i < main.length - 1; i++) segs.push([main[i], main[i + 1], i / (main.length - 1), 1, true]);
  for (let k = 0; k < 9; k++) {                                          // branches leave the channel and die out
    const i0 = Math.floor((.05 + R() * .7) * (main.length - 1)), p = main[i0], dir = [(R() - .5) * 2, -.6 - R() * .8, (R() - .5) * 2];
    const len = 30 + R() * 90, end = [p[0] + dir[0] * len, p[1] + dir[1] * len, p[2] + dir[2] * len];
    const br = jag(p, end, 5, .45);
    for (let i = 0; i < br.length - 1; i++) segs.push([br[i], br[i + 1], i0 / (main.length - 1) + i / br.length * .25, .45 * (1 - i / br.length), false]);
  }
  // the upward streamer from the target (a few metres)
  const up = jag(tgt, [tgt[0] + (R() - .5) * 2, tgt[1] + 9, tgt[2] + (R() - .5) * 2], 4, .35);
  // drawn as thin boxes (a core and a wide soft glow), one instance per segment
  const N = segs.length + up.length;
  const core = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }), N);
  const glow = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: 0x9fb6ff, transparent: true, opacity: .25, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }), N);
  core.frustumCulled = glow.frustumCulled = false; E.scene.add(core); E.scene.add(glow);
  const light = new THREE.PointLight(0xdfe8ff, 0, 400, 1.2); light.position.set(tgt[0], tgt[1] + 20, tgt[2]); E.scene.add(light);
  const W = o.width ?? 1;
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), c = new THREE.Vector3(), Y = new THREE.Vector3(0, 1, 0), d = new THREE.Vector3();
  const cam = E.camera.position;
  const place = (im, i, p, qq, w) => {
    // seen from close by a metre-wide channel fills the screen: keep it about the same size on screen (thin near the camera)
    const mx = (p[0] + qq[0]) / 2 - cam.x, my = (p[1] + qq[1]) / 2 - cam.y, mz = (p[2] + qq[2]) / 2 - cam.z;
    w *= Math.min(1, Math.hypot(mx, my, mz) / 60);
    d.set(qq[0] - p[0], qq[1] - p[1], qq[2] - p[2]); const L = d.length() || .001;
    q.setFromUnitVectors(Y, d.normalize()); c.set((p[0] + qq[0]) / 2, (p[1] + qq[1]) / 2, (p[2] + qq[2]) / 2); s.set(w, L, w);
    m4.compose(c, q, s); im.setMatrixAt(i, m4);
  };
  // events: thunder follows the flash (light is instant, sound takes ~3 s per km), camera shake
  const dist = o.thunderDelay ?? .15;
  for (const dt of [0, ...restrikes]) (E.EVENTS ||= []).push({ t: at + dt + dist, kind: 'thunder', e: dt ? .6 : 1.3 });
  (E.EVENTS ||= []).push({ t: at, kind: 'impact', e: 1.2, x: tgt[0], z: tgt[2] });
  const flashAt = t => { let k = 0; for (const dt of [0, ...restrikes]) { const a = t - at - dt; if (a >= 0 && a < .6) k = Math.max(k, (dt ? .7 : 1) * Math.exp(-a * 9)); } return k; };
  return (t, tv) => {
    const lead = Math.min(1, Math.max(0, (t - (at - leader - streamT)) / Math.max(.1, leader)));   // how far the leader has come down
    const st = Math.min(1, Math.max(0, (t - (at - streamT)) / Math.max(.05, streamT)));            // the streamer grows up
    const fl = flashAt(t), after = t - at, show = t > at - leader - streamT && after < 2.2;
    core.visible = glow.visible = show; light.intensity = fl * 25;
    if (!show) return;
    const stroke = after >= 0, fade = stroke ? Math.max(0, 1 - after / 2.2) : 1;
    for (let i = 0; i < segs.length; i++) {
      const [p, qq, ord, w, isMain] = segs[i];
      // before the stroke: only what the leader reached, thin and violet-dim; at the stroke the main channel is thick and bright
      const vis = stroke ? (isMain ? 1 : Math.max(0, 1 - after * 3)) : ord <= lead ? 1 : 0;
      const ww = vis * W * w * (stroke ? (isMain ? .3 + .7 * fl : .2) * (.4 + .6 * fade) : .45);   // metres: thin, the glow makes it bright
      place(core, i, p, qq, ww); place(glow, i, p, qq, ww * (stroke ? 4 : 4.5));
    }
    for (let i = 0; i < up.length - 1; i++) {
      const vis = !stroke && i / (up.length - 1) <= st ? 1 : stroke ? Math.max(0, 1 - after * 4) : 0;
      place(core, segs.length + i, up[i], up[i + 1], vis * W * .05); place(glow, segs.length + i, up[i], up[i + 1], vis * W * .3);
    }
    core.instanceMatrix.needsUpdate = glow.instanceMatrix.needsUpdate = true;
    core.material.color.setRGB(stroke ? 1 : .82, stroke ? 1 : .78, 1); core.material.opacity = stroke ? Math.max(.25, fade) : .85;
    glow.material.opacity = stroke ? .12 + .3 * fl : .22;
    // the whole scene flashes white with the stroke (and each restrike)
    if (fl > 0) { E.hemi.intensity += fl * 4.5; E.hemi.color.lerp(new THREE.Color(0xe4ecff), fl * .9); E.renderer.toneMappingExposure += fl * .75; }
  };
}
