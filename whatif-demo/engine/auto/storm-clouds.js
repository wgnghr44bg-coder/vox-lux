// AUTO BLOCK storm-clouds: a low, dark, rolling cloud deck that moves in and darkens the whole place
// (hurricane, endless rain, lightning storm). Works with 'rain' and TL.lightning (fences.js).
// Use in scenario.js:  auto: [{ block: 'storm-clouds', from: 2, full: 15, until: 1e9, strength: 1, height: 220, wind: [8, -3] }]
//   from/full/until: s; strength 0..1.5 (1.5 = hurricane: very low, black, fast); height: cloud base in metres
//   above the ground; wind: [vx, vz] m/s how the clouds drift.
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE, R = rng(31), C = h => new THREE.Color(h);
  const from = o.from ?? 0, full = o.full ?? from + 12, until = o.until ?? 1e9, max = o.strength ?? 1;
  const level = t => t < from ? 0 : Math.min(1, (t - from) / Math.max(.1, full - from)) * max * (t > until ? Math.max(0, 1 - (t - until) / 8) : 1);
  const N = 520, SPAN = 3200, base = o.height ?? 220, wind = o.wind ?? [8, -3];
  // one instanced puff: a flattened low-poly blob; many of them make a lumpy ceiling
  const geo = new THREE.IcosahedronGeometry(1, 1);
  const mat = new THREE.MeshLambertMaterial({ color: 0x8a9096, emissive: 0x3c4146, flatShading: true, transparent: true, opacity: .96 });
  const puffs = new THREE.InstancedMesh(geo, mat, N); puffs.frustumCulled = false; E.scene.add(puffs);
  const P = [];
  for (let i = 0; i < N; i++) P.push({ x: (R() - .5) * SPAN, z: (R() - .5) * SPAN, y: R() * 70, s: 70 + R() * 120, f: .25 + R() * .2, r: R() * 6, sh: .75 + R() * .35 });
  const tint = new THREE.Color();
  for (let i = 0; i < N; i++) puffs.setColorAt(i, tint.setScalar(P[i].sh));
  // the light: grey sky, no sun, near fog, dim and cold
  (E.lookMods ||= []).push((t, L) => {
    const k = Math.min(1, level(t)), d = Math.max(0, level(t) - 1) * 2;      // d: extra darkness of a hurricane
    if (k <= 0) return;
    const sky = C(0x7a8288).lerp(C(0x5c646a), d);   // grey, never black: the sky shows under the cloud deck
    L.top = L.top.clone().lerp(sky, k); L.hor = L.hor.clone().lerp(C(0x8a9196).lerp(C(0x6a7177), d), k);   // the horizon under the clouds stays lighter
    L.fogColor = L.hor.clone();          // far clouds melt into the horizon (no dark band)
    L.fogNear = (L.fogNear ?? 200) * (1 - k * .6); L.fogFar = Math.min(L.fogFar ?? 1600, 1600 - k * 700);
    L.sun = (L.sun ?? 2) * (1 - k * .8); L.sunDisc = C(0); L.hemi = (L.hemi ?? 1.4) * (1 - k * .3); L.hemiColor = C(0xb8c0c6);
    L.stars = 0;
  });
  const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(), p = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  return (t, tv) => {
    const k = level(t); puffs.visible = k > .02; if (!puffs.visible) return;
    const c = E.camera.position, gy = E.groundAt?.(c.x, c.z) ?? 0, h = gy + base * (1 - .45 * Math.max(0, k - 1)) + (1 - Math.min(1, k)) * 260;
    const wrap = v => ((v % SPAN) + SPAN * 1.5) % SPAN - SPAN / 2, sp = 1 + Math.max(0, k - 1) * 3;
    mat.color.setHex(0x8a9096).multiplyScalar(1 - Math.max(0, k - 1) * .6); mat.emissive.setHex(0x3c4146).multiplyScalar(1 - Math.max(0, k - 1) * .5); mat.opacity = Math.min(.96, k * 1.2);
    for (let i = 0; i < N; i++) {
      const a = P[i], x = c.x + wrap(a.x + wind[0] * tv * sp - c.x), z = c.z + wrap(a.z + wind[1] * tv * sp - c.z);
      const far = Math.hypot(x - c.x, z - c.z), shrink = Math.max(0, Math.min(1, (1500 - far) / 400));   // the farthest puffs fade out (no hard edge at the horizon)
      q.setFromAxisAngle(up, a.r + tv * .01 * sp); s.set(a.s * shrink, a.s * a.f * shrink, a.s * .8 * shrink);
      m.compose(p.set(x, h + a.y, z), q, s); puffs.setMatrixAt(i, m);
    }
    puffs.instanceMatrix.needsUpdate = true;
  };
}
