// AUTO BLOCK tsunami-wave: a giant wall of water rolling in from the sea (asteroid in the ocean, a dam breaking,
// ice sliding into the sea). It grows as it reaches shallow water, breaks with a white crest and spray, and the
// camera shakes when it hits. Pair it with the water/tide force to flood the land after it (forceParams).
// Use in scenario.js:  auto: [{ block: 'tsunami-wave', at: 20, arrive: 14, from: [0, -1800], to: [0, 40],
//                              height: [12, 35], width: 2600, run: 60 }]
//   at: s it appears far out; arrive: s until its front reaches `to` (the shore / where it breaks);
//   from/to: [x, z] where the front starts and where it hits; height: [far out, at the shore] in metres;
//   width: length of the wave front in metres; run: metres it keeps rolling inland after `to` while it collapses.
//   Gives E.EVENTS { kind: 'splash' } when it hits (camera shake, sound).
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE, R = rng(41), C = h => new THREE.Color(h);
  const at = o.at ?? 0, arrive = o.arrive ?? 14, from = o.from ?? [0, -1800], to = o.to ?? [0, 0];
  const [h0, h1] = Array.isArray(o.height) ? o.height : [(o.height ?? 30) * .4, o.height ?? 30];
  const W = o.width ?? 2600, run = o.run ?? 60, collapse = 6;
  const dx = to[0] - from[0], dz = to[1] - from[1], dist = Math.hypot(dx, dz) || 1, ang = Math.atan2(dx, dz);
  // profile across the wave (u: metres behind the front, y: height as a fraction of the crest), front at u = 0
  const prof = [[-.10, 0], [0, .05], [.02, .35], [.05, .7], [.02, .92], [-.06, 1.02], [.08, 1.0], [.25, .9], [.6, .6], [1.2, .3], [2.4, .08], [3.6, 0]];
  const COLS = 80, ROWS = prof.length, geo = new THREE.BufferGeometry(), pos = new Float32Array(COLS * ROWS * 3), col = new Float32Array(COLS * ROWS * 3), idx = [];
  for (let i = 0; i < COLS - 1; i++) for (let j = 0; j < ROWS - 1; j++) { const a = i * ROWS + j, b = a + ROWS; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  geo.setIndex(idx); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const body = C(0x2f6670), face = C(0x5aa3a6), foam = C(0xeef4f4), tmp = new THREE.Color(), jag = [], streak = [];
  for (let i = 0; i < COLS; i++) { jag.push((R() - .5) * .12); streak.push(R()); }
  for (let i = 0; i < COLS; i++) for (let j = 0; j < ROWS; j++) {
    const k = (i * ROWS + j) * 3, y = prof[j][1];
    // white crest, a light turquoise face with foam streaks running down it, darker water behind
    tmp.copy(j >= 3 && j <= 6 ? foam : j <= 2 ? face.clone().lerp(foam, streak[i] > .55 ? .25 + y * .8 : y * .3) : body.clone().lerp(face, .45 * y));
    col[k] = tmp.r; col[k + 1] = tmp.g; col[k + 2] = tmp.b;
  }
  // a little self-light: a wave seen against the sun would otherwise turn almost black
  const mat = new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true, side: THREE.DoubleSide, emissive: 0x1b3f43 });
  const wave = new THREE.Mesh(geo, mat); wave.castShadow = true; wave.frustumCulled = false;
  const g = new THREE.Group(); g.add(wave); g.rotation.y = ang; E.scene.add(g);      // local +z = direction of travel
  // spray: white puffs riding on the crest
  const NS = 320, spray = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), new THREE.MeshLambertMaterial({ color: 0xf4f8f8, emissive: 0x8d9a9c, flatShading: true, transparent: true, opacity: .8, depthWrite: false }), NS); spray.frustumCulled = false; g.add(spray);
  const S = []; for (let i = 0; i < NS; i++) S.push({ x: (R() - .5) * W * .9, ph: R(), s: .6 + R() * .8 });
  const tHit = at + arrive;
  (E.EVENTS ||= []).push({ t: tHit, kind: 'splash', e: 4, x: to[0], z: to[1] });
  const ease = u => u * u * (3 - 2 * u) * .3 + u * .7;                 // a little slow at first, then fast
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), sc = new THREE.Vector3(), p = new THREE.Vector3();
  return (t, tv) => {
    g.visible = t >= at && t < tHit + collapse + 4; if (!g.visible) return;
    const u = Math.min(1, (t - at) / arrive), after = Math.max(0, t - tHit), fall = Math.min(1, after / collapse);
    const front = ease(u) * dist + Math.min(1, after / collapse) * run;   // metres travelled along the path
    const H = (h0 + (h1 - h0) * u * u) * (1 - .85 * fall), wy = F?.field?.(Math.min(t, TL.beats.stop))?.waterY ?? E.waterBase ?? 0;
    const fx = from[0] + Math.sin(ang) * front, fz = from[1] + Math.cos(ang) * front;
    g.position.set(fx, wy, fz);
    const thick = Math.max(H * 2.2, 40), lean = .05 + .2 * u + .6 * fall;      // it leans forward and topples at the end
    for (let i = 0; i < COLS; i++) {
      const x = (i / (COLS - 1) - .5) * W, edge = Math.min(1, (1 - Math.abs(i / (COLS - 1) - .5) * 2) * 6);   // ends taper into the sea
      for (let j = 0; j < ROWS; j++) {
        const k = (i * ROWS + j) * 3, [pu, py] = prof[j], y = py * H * edge * (1 + jag[i] * (py > .8 ? 1 : 0));
        pos[k] = x; pos[k + 1] = y - .3; pos[k + 2] = -pu * thick + y * lean * (j >= 4 && j <= 6 ? 1 : .3);
      }
    }
    geo.attributes.position.needsUpdate = true; geo.computeVertexNormals();
    for (let i = 0; i < NS; i++) {
      const a = S[i], ph = (tv * .7 + a.ph) % 1, r = (3 + 6 * a.s) * (H / 30) * (.6 + ph);
      // mist on the crest: it rises a little and blows back over the wave, then fades
      p.set(a.x, H * (.98 + ph * .18), H * lean * .6 - ph * 8); sc.set(r * 1.6, r * .7, r).multiplyScalar((1 - ph) * (u > .15 ? 1 : 0) * (1 - fall * .5));
      m4.compose(p, q, sc); spray.setMatrixAt(i, m4);
    }
    spray.instanceMatrix.needsUpdate = true;
  };
}
