// SINKHOLE (baksteen, from sinkhole-downtown/ – eigenaar 11 okt 2026): the ground opens and a deep pit grows.
// Works on any flat place: the ground (every low, flat mesh around the hole) is cut away by a shader inside the
// hole edge, pieces of that ground (same colour) break off at the edge and fall, the walls show soil layers that
// get dark with depth, and everything standing near the edge (props, trees, lamps, buildings, parked or stopped
// cars) tips over and drops in when the edge reaches it. People should be gone by then (beats.shelter); the
// console reports how close anyone came.
// The counter is the DEPTH in meters (TL.counter); TL.forceParams:
//   radius: [[t, r], ...]   hole radius in meters over time (width = 2 r), required
//   center: [x, z]           default [0, -2]
//   pipe:   [x, z]           water seeps up here from beats.pipe (the leaking pipe); default near the center
// Beats: pipe (water at the manhole), cracks (cracks run over the road), drop (the first collapse: sound + shake;
// default = when the radius first grows).
import * as THREE from 'three';
import { baseForce } from './base.js';
import { smooth, hash, clamp, monotone, rng } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {}, B = TL.beats;
  const [CX, CZ] = P.center || [0, -2];
  const Rt = monotone(P.radius || [[0, 0], [1, 0]]);
  const maxR = Math.max(...(P.radius || [[0, 0]]).map(p => p[1]));
  const RTAB = []; for (let t = 0; t <= TL.T_END + .1; t += 1 / 60) RTAB.push(Rt(t));
  const dRt = t => (Rt(t + .1) - Rt(Math.max(0, t - .1))) / .2;
  const F = baseForce(E, TL, 'sinkhole');
  const depthAt = F.counter;
  const edgeK = a => 1 + .13 * (.55 * Math.sin(3 * a + 1) + .3 * Math.sin(5 * a + 2.3) + .15 * Math.sin(11 * a + .7));
  const edgeAt = (x, z, t) => Rt(t) * edgeK(Math.atan2(z - CZ, x - CX));
  const edgeTime = (x, z, jit = 0) => { const need = (Math.hypot(x - CX, z - CZ) + jit) / edgeK(Math.atan2(z - CZ, x - CX));
    for (let i = 0; i < RTAB.length; i++) if (RTAB[i] >= need && RTAB[i] > .05) return i / 60; return 1e9; };
  const tDrop = B.drop ?? edgeTime(CX, CZ);
  F.level = t => clamp(dRt(t) / 6) * .8 + (t > tDrop ? .2 * Math.exp(-(t - tDrop) / 4) : 0);   // sound: the ground on the move
  Object.assign(F, { edgeAt, edgeTime, center: [CX, CZ], fallMode: 'sink' });

  F.attach = () => {
    const y0 = E.groundAt(CX, CZ) ?? 0, scene = E.scene, reach = maxR * 1.2 + 4;
    // ---- 1. cut the ground: low flat meshes near the hole get a shader that discards inside the edge ----
    const U = { holeC: { value: new THREE.Vector2(CX, CZ) }, holeR: { value: 0 } };
    const ground = [], box = new THREE.Box3();
    scene.updateMatrixWorld(true);
    scene.traverse(o => {
      if (!o.isMesh || o.isInstancedMesh || !o.geometry) return;
      box.setFromObject(o);
      if (box.max.y > y0 + .6 || box.min.y < y0 - 3) return;
      if (box.max.x < CX - reach || box.min.x > CX + reach || box.max.z < CZ - reach || box.min.z > CZ + reach) return;
      const patch = m => { const c = m.clone(); c.customProgramCacheKey = () => 'sinkhole';
        c.onBeforeCompile = sh => {
          sh.uniforms.holeC = U.holeC; sh.uniforms.holeR = U.holeR;
          sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vHoleW;')
            .replace('#include <project_vertex>', '#include <project_vertex>\n vHoleW = (modelMatrix * vec4(transformed, 1.0)).xz;');
          sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec2 vHoleW; uniform vec2 holeC; uniform float holeR;')
            .replace('void main() {', `void main() { { vec2 d = vHoleW - holeC; float a = atan(d.y, d.x);
              float k = 1. + .13 * (.55 * sin(3. * a + 1.) + .3 * sin(5. * a + 2.3) + .15 * sin(11. * a + .7));
              if (holeR > .01 && length(d) < holeR * k) discard; }`);
        }; return c; };
      o.material = Array.isArray(o.material) ? o.material.map(patch) : patch(o.material);
      ground.push(o);
    });
    E.updates.push(t => { U.holeR.value = Rt(t); });

    // ---- 2. pieces of ground that break off at the edge (colour of the ground right there) ----
    const ray = new THREE.Raycaster(), down = new THREE.Vector3(0, -1, 0), pts = [], S = 1.4;
    for (let x = CX - maxR * 1.16; x <= CX + maxR * 1.16; x += S) for (let z = CZ - maxR * 1.16; z <= CZ + maxR * 1.16; z += S) {
      const tf = edgeTime(x, z, -.2); if (tf > TL.T_END) continue;
      ray.set(new THREE.Vector3(x, y0 + 5, z), down); const hit = ray.intersectObjects(ground, false)[0];
      const m = hit && (Array.isArray(hit.object.material) ? hit.object.material[2] ?? hit.object.material[0] : hit.object.material);
      pts.push({ x, z, y: hit ? hit.point.y : y0, tf, col: new THREE.Color(m?.color ?? 0x3c3e41), ph: hash(x * 7, z * 3), pile: [hash(x, z + 9), hash(x + 3, z)] });
    }
    const pieces = new THREE.InstancedMesh(new THREE.BoxGeometry(S * 1.02, .7, S * 1.02), E.lam(0xffffff), Math.max(1, pts.length));
    pieces.frustumCulled = false; pieces.receiveShadow = true; scene.add(pieces);
    pts.forEach((p, k) => pieces.setColorAt(k, p.col));
    const D = new THREE.Object3D(), C = new THREE.Color();
    E.updates.push(t => {
      const depth = depthAt(t), R0 = Rt(t);
      pts.forEach((p, k) => {
        const a = t - p.tf; let s = 1, x = p.x, y = p.y - .35, z = p.z, rx = 0, rz = 0, dark = 1;
        if (a < 0) s = 0;
        else { const d = Math.hypot(x - CX, z - CZ) || 1, ux = (x - CX) / d, uz = (z - CZ) / d, fall = .5 * 9.8 * a * a;
          if (fall > Math.min(depth + 2, 30)) { const r = R0 * .55 * Math.sqrt(p.pile[0]), an = p.pile[1] * 6.28; x = CX + Math.cos(an) * r; z = CZ + Math.sin(an) * r; y = y0 - depth + .4; rx = p.ph * 2; rz = p.pile[0] * 2; dark = .08; }
          else { y -= fall; x -= ux * Math.min(3, a * 2); z -= uz * Math.min(3, a * 2); rx = uz * Math.min(1.4, a * 1.9) * (p.ph > .5 ? 1 : -.6); rz = -ux * Math.min(1.4, a * 1.9); dark = fall > 20 ? .08 : 1 - .65 * clamp(fall / 20); } }
        D.position.set(x, y, z); D.rotation.set(rx, 0, rz); D.scale.setScalar(s); D.updateMatrix(); pieces.setMatrixAt(k, D.matrix);
        pieces.setColorAt(k, C.copy(p.col).multiplyScalar(dark));
      });
      pieces.instanceMatrix.needsUpdate = true; pieces.instanceColor.needsUpdate = true;
    });

    // ---- 3. the pit: walls with soil layers (darker with depth), a muddy floor with rubble ----
    const wg = new THREE.CylinderGeometry(1, 1, 1, 96, 24, true); wg.translate(0, -.5, 0);
    { const p = wg.attributes.position, col = new Float32Array(p.count * 3), c = new THREE.Color();
      const layers = P.layers || [[0, 0x6e5a44], [.02, 0x8a6f4f], [.12, 0x9c8a6c], [.3, 0x7d6a55], [.48, 0xa8987a], [.66, 0x6a5a4a], [.85, 0x584a3e]];
      for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), u = -p.getY(i), a = Math.atan2(z, x), k = edgeK(a);
        p.setX(i, x * k); p.setZ(i, z * k);
        let L = layers[0][1]; for (const [d, h] of layers) if (u >= d) L = h;
        c.setHex(L).multiplyScalar(((P.wallLight ?? .8) * Math.exp(-u * 5.5) + .012) * (.86 + .22 * Math.sin(a + 2.2)) * (.92 + .16 * hash(Math.round(a * 40), Math.round(u * 24))));
        col.set([c.r, c.g, c.b], i * 3); }
      wg.setAttribute('color', new THREE.BufferAttribute(col, 3)); }
    const wall = new THREE.Mesh(wg, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide, fog: false })); scene.add(wall);
    const floor = new THREE.Group(); scene.add(floor);
    { const sh = new THREE.Shape(); for (let i = 0; i <= 96; i++) { const a = i / 96 * Math.PI * 2, k = edgeK(a); i ? sh.lineTo(Math.cos(a) * k, Math.sin(a) * k) : sh.moveTo(Math.cos(a) * k, Math.sin(a) * k); }
      const g = new THREE.ShapeGeometry(sh); g.rotateX(Math.PI / 2);
      floor.add(new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0x0b0907, side: THREE.DoubleSide, fog: false })));
      const R = rng(17), im = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(1, 0), E.lam(0x231e1a), 140), d = new THREE.Object3D();
      for (let i = 0; i < 140; i++) { const a = R() * 6.28, r = Math.sqrt(R()) * .8; d.position.set(Math.cos(a) * r, 0, Math.sin(a) * r); d.rotation.set(R() * 3, R() * 3, R() * 3);
        const s = .02 + R() * .05; d.scale.set(s, s * .6, s * 1.2); d.updateMatrix(); im.setMatrixAt(i, d.matrix); }
      im.frustumCulled = false; floor.add(im); }
    E.updates.push(t => { const R0 = Rt(t), dp = depthAt(t); wall.visible = floor.visible = R0 > .05;
      wall.scale.set(R0, dp + .3, R0); wall.position.set(CX, y0 + .3, CZ); floor.scale.set(R0 * 1.08, 1, R0 * 1.08); floor.position.set(CX, y0 - dp - .1, CZ); });

    // ---- 4. the warning signs: water at the manhole, cracks over the road ----
    const [PX, PZ] = P.pipe || [CX + 2.5, CZ - 1];
    const puddle = new THREE.Mesh(new THREE.CircleGeometry(1, 28), new THREE.MeshLambertMaterial({ color: 0x2c3438, transparent: true, opacity: .75 }));
    puddle.rotation.x = -Math.PI / 2; puddle.position.set(PX, y0 + .03, PZ); scene.add(puddle);
    const manhole = new THREE.Mesh(new THREE.CircleGeometry(.6, 16), E.lam(0x2a2b2d)); manhole.rotation.x = -Math.PI / 2; manhole.position.set(PX, y0 + .025, PZ); scene.add(manhole);
    const cracks = [];
    if (B.cracks != null) { const R = rng(23), mat = new THREE.MeshBasicMaterial({ color: 0x141312 }), geo = new THREE.PlaneGeometry(1, 1); geo.rotateX(-Math.PI / 2);
      const line = (x, z, ang, len, w, t0, dur) => { let px = x, pz = z, a = ang; const n = Math.ceil(len / 1.2);
        for (let k = 0; k < n; k++) { a += (R() - .5) * .7; const nx = px + Math.cos(a) * 1.2, nz = pz + Math.sin(a) * 1.2;
          const m = new THREE.Mesh(geo, mat); m.position.set((px + nx) / 2, y0 + .04, (pz + nz) / 2); m.rotation.y = -a; m.scale.set(1.35, 1, w * (1 - k / n * .6)); scene.add(m);
          cracks.push({ m, t0: t0 + k / n * dur, tf: edgeTime(m.position.x, m.position.z, -.4) }); px = nx; pz = nz; } };
      for (let i = 0; i < 9; i++) { const a = i / 9 * 6.28 + R() * .5; line(CX + Math.cos(a) * 2, CZ + Math.sin(a) * 2, a, 9 + R() * 12, .16 + R() * .12, B.cracks + R() * 1.2, 2 + R() * 1.5); }
      for (let i = 0; i < 4; i++) { const a = R() * 6.28; line(CX + Math.cos(a) * 9, CZ + Math.sin(a) * 9, a + 1.57, 10, .12, B.cracks + 1.5 + R(), 2.5); }
      E.EVENTS.push({ t: B.cracks, kind: 'rift', e: .7, x: CX, z: CZ }); }
    E.updates.push(t => {
      const g = smooth(B.pipe ?? 1e9, B.cracks ?? (B.pipe ?? 1e9) + 8, t), R0 = Rt(t);
      puddle.visible = t > (B.pipe ?? 1e9) && R0 < .5; puddle.scale.setScalar(.3 + g * 4.2); manhole.visible = Rt(t) < .5;
      for (const c of cracks) { const k = smooth(c.t0, c.t0 + .35, t); c.m.visible = k > 0 && t < c.tf; c.m.scale.x = 1.35 * k; }
    });

    // ---- 5. everything standing near the edge tips over and drops in ----
    const peopleG = new Set(E.people.map(p => p.g)), bodyObj = new Set(E.bodies.map(b => b.obj).filter(Boolean));
    const mine = new Set([pieces, wall, floor, puddle, manhole, ...cracks.map(c => c.m)]);
    const fallers = [];
    for (const o of [...scene.children]) {
      if (mine.has(o) || peopleG.has(o) || bodyObj.has(o) || ground.includes(o) || o.isLight || o.isCamera || o.isPoints || o.isInstancedMesh || o === E.sky) continue;
      box.setFromObject(o); if (box.isEmpty()) continue;
      const sx = box.max.x - box.min.x, sz = box.max.z - box.min.z; if (sx > 70 || sz > 70) continue;
      const x = o.position.x, z = o.position.z, tf = edgeTime(x, z, (hash(Math.round(x), Math.round(z)) - .5) * .8);
      if (tf > TL.T_END) continue;
      const big = sx > 8 || sz > 8;
      fallers.push({ o, x, z, tf, big, home: o.position.clone(), q: o.quaternion.clone() });
      if (big) E.EVENTS.push({ t: tf, kind: 'collapse', e: .7, x, z });
    }
    { let last = -1; for (const f of fallers.filter(f => !f.big).sort((a, b) => a.tf - b.tf)) if (f.tf - last > .5) { last = f.tf; E.EVENTS.push({ t: f.tf + .4, kind: 'drop', e: .7, x: f.x, z: f.z }); } }
    // cars (physics bodies): the first frame the edge reaches them
    // bodies with an object (cars, bins, chairs): the first frame the edge reaches them (after the physics has run)
    let cars = null;
    const findCars = () => { cars = [];
      for (const b of E.bodies) if (b.obj && b.arr) for (let f = 0; f < E.NF; f++) {
        const t = f / E.FPS, x = b.arr[f * 7], z = b.arr[f * 7 + 2];
        if (Math.hypot(x - CX, z - CZ) < edgeAt(x, z, t) + .5) { cars.push({ o: b.obj, x, z, tf: t, home: new THREE.Vector3(x, b.arr[f * 7 + 1], z), q: null, big: false }); break; }
      } };
    const Q = new THREE.Quaternion(), AX = new THREE.Vector3(), V = new THREE.Vector3();
    const pose = (f, t) => {
      if (t < f.tf - 1.6) return;
      const d = Math.hypot(f.x - CX, f.z - CZ) || 1, ux = (f.x - CX) / d, uz = (f.z - CZ) / d;
      const a = Math.max(0, t - f.tf), ang = Math.min(f.big ? .8 : 1.3, smooth(f.tf - 1.6, f.tf, t) * .06 + .5 * (f.big ? .45 : 1.6) * a * a + (f.big ? .02 : .3) * a);
      const drop = a > 0 ? Math.min(depthAt(t) + 40, .5 * (f.big ? 3.2 : 9.8) * a * a) : 0;
      AX.set(-uz, 0, ux).normalize(); Q.setFromAxisAngle(AX, ang);
      if (!f.q) f.q = f.o.quaternion.clone();
      f.o.quaternion.copy(Q).multiply(f.q);
      V.set(0, f.home.y - y0, 0).applyQuaternion(Q);            // turn about the foot of the object
      f.o.position.set(f.home.x - ux * Math.min(4, a * 1.6) + V.x, y0 + V.y - drop, f.home.z - uz * Math.min(4, a * 1.6) + V.z);
      f.o.visible = drop < depthAt(t) - 2 || drop < 3;
    };
    (E.afterPose ||= []).push(t => { if (!cars) findCars(); for (const f of fallers) pose(f, t); for (const c of cars) { if (t >= c.tf - 1.6) { c.q = c.o.quaternion.clone(); pose(c, t); } } });

    // ---- 6. dust: a burst at the drop, then from the edge wherever the hole grows ----
    E.emitters.push((tv, add) => {
      const t = tv, rate = 70;
      if (B.pipe != null && t > B.pipe && Rt(t) < .5) for (let k = 0; k < 26; k++) { const a = (t * 1.3 + hash(k, 2)) % 1;
        add(PX + (hash(k, 3) - .5) * .9, y0 + .05 + a * .45, PZ + (hash(k, 4) - .5) * .9, .28, (1 - a) * .35 * smooth(B.pipe, B.pipe + 2, t), .8, .85, .88, hash(k, 5) * 6); }
      for (let k = Math.max(0, Math.floor((t - 8) * rate)); k <= t * rate; k++) {
        const b = k / rate + hash(k, 1) / rate, a = t - b; if (a < 0 || b < tDrop) continue;
        const w = Math.max(clamp(dRt(b) / 6) * .45, Math.exp(-(b - tDrop) / 1.1) * .5); if (hash(k, 2) > w + .04) continue;
        const ang = hash(k, 3) * 6.28, r0 = Rt(b) * edgeK(ang) * (.6 + hash(k, 4) * .45);
        add(CX + Math.cos(ang) * (r0 + a * .8), y0 - 6 + a * (3 + hash(k, 5) * 4) + 6 * (1 - Math.exp(-a)), CZ + Math.sin(ang) * (r0 + a * .8),
          5 + a * 2.2 + hash(k, 6) * 4, smooth(0, .6, a) * (1 - smooth(3, 7, a)) * .07, .66, .6, .52, hash(k, 7) * 6 + a * .05);
      }
    });
    E.EVENTS.push({ t: tDrop, kind: 'collapse', e: 1, x: CX, z: CZ });
    for (let t = tDrop + 2; t < TL.T_END; t += .9) { const e = clamp(dRt(t) / 6); if (e > .1) E.EVENTS.push({ t, kind: 'slide', e, x: CX, z: CZ }); }

    // ---- 7. safety: how close does anyone get to the edge? ----
    let worst = 1e9;
    for (let t = 0; t < TL.T_END; t += .2) for (const p of E.people) { const s = p.path?.(t, F, p); if (!s || s.visible === false) continue;
      worst = Math.min(worst, Math.hypot(s.x - CX, s.z - CZ) - edgeAt(s.x, s.z, t)); }
    console.log(`sinkhole: closest person to the edge ${worst.toFixed(1)} m, ${fallers.length} things fall in, ${pts.length} pieces of ground`);
    window.SINK_SAFETY = worst;
  };
  return F;
}
