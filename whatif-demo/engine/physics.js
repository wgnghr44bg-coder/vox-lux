// Rigid-ish debris physics: everything is simulated once up front and stored at 30 fps,
// so any frame can be rendered on its own (several render workers, re-renders of a tail).
// The force supplies the field: gravity g(t), air velocity air(t), water level waterY(t), current.
import * as THREE from 'three';
import { clamp, noise, lerp } from './util.js';

const _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _p = new THREE.Vector3(), _e = new THREE.Euler();

export function simulate(E, F, STOP) {
  const FPS = E.FPS, NF = Math.ceil(STOP * FPS) + 2, SUB = 4, dt = 1 / (FPS * SUB);
  E.NF = NF;
  for (const b of E.bodies) { b.arr = new Float32Array(NF * 7); b.vel = [0, 0, 0]; b.w = [0, 0, 0]; b.live = false; b.done = false; }
  let posed = -1;
  for (let f = 0; f < NF; f++) {
    for (let sub = 0; sub < SUB; sub++) {
      const t = (f * SUB + sub) * dt, fl = F.field(t), g = fl.g, air = fl.air, wy = fl.waterY, cur = fl.current || [0, 0, 0];
      for (const b of E.bodies) {
        if (b.done) continue;
        if (!b.live) {
          if (b.drive && t < b.tRel) { const d = b.drive(t); b.p = d.p; b.r = d.r; b.v0 = d.v; continue; }
          if (t < b.tRel) continue;
          b.live = true; b.tRelReal = t;
          if (b.kind === 'part') {
            if (posed !== f) { E.poseAll(t); posed = f; }
            b.src.matrixWorld.decompose(_p, _q, _s); _e.setFromQuaternion(_q);
            b.p = [_p.x, _p.y, _p.z]; b.r = [_e.x, _e.y, _e.z];
            if (b.obj && !b.keepScale) b.obj.scale.copy(_s);
          }
          b.vel = [...b.v0];
        }
        const p = b.p, v = b.vel, r = b.r, wv = b.w;
        const gust = 1 + .25 * noise(t * 1.3, p[0] + b.k * 50);
        const rx = air[0] * gust - v[0], ry = air[1] - v[1], rz = air[2] * gust - v[2], sp = Math.hypot(rx, ry, rz);
        let ax = b.k * sp * rx + b.k * sp * 1.2 * noise(t * 2.1, p[2] * .3 + b.hx * 9) * (sp > 1 ? 1 : 0),
            ay = b.k * sp * ry - g + b.k * b.lift * sp * sp * (.6 + .4 * noise(t * 1.7, p[0] * .7)),
            az = b.k * sp * rz;
        // water: buoyancy and heavy drag toward the current
        const sub_ = clamp((wy - (p[1] - b.hy)) / (2 * b.hy + .01));
        if (sub_ > 0) {
          ay += g * sub_ / b.density;
          const kw = 1.6 * sub_;
          ax += kw * (cur[0] - v[0]); ay += kw * (cur[1] - v[1]) * 1.5; az += kw * (cur[2] - v[2]);
          if (!b.wet && v[1] < -4 && b.heavy) E.EVENTS.push({ t, kind: 'splash', x: p[0], y: wy, z: p[2], e: Math.min(1, b.heavy * Math.abs(v[1]) / 25) });
          b.wet = true;
        } else b.wet = false;
        const R = b.hy * Math.abs(Math.cos(r[0]) * Math.cos(r[2])) + b.hz * Math.abs(Math.sin(r[0])) + b.hx * Math.abs(Math.sin(r[2]));
        const gy = E.groundAt(p[0], p[2]);
        const onG = p[1] <= gy + R + .01;
        if (onG && Math.abs(v[1]) < .5) {
          const ah = Math.hypot(ax, az), vh = Math.hypot(v[0], v[2]);
          if (vh < .05 && ah < b.mu * g) { ax = 0; az = 0; v[0] = v[2] = 0; }
          else if (vh > 0) { const fr = b.mu * g * .7; ax -= fr * v[0] / vh; az -= fr * v[2] / vh; }
        }
        v[0] += ax * dt; v[1] += ay * dt; v[2] += az * dt;
        p[0] += v[0] * dt; p[1] += v[1] * dt; p[2] += v[2] * dt;
        if (p[1] < gy + R) {
          if (v[1] < -3 && b.heavy && sub_ <= 0) E.EVENTS.push({ t, kind: 'impact', x: p[0], y: p[1], z: p[2], e: Math.min(1, b.heavy * Math.abs(v[1]) / 30), heavy: b.heavy });
          p[1] = gy + R; v[1] = Math.abs(v[1]) > 1 ? -v[1] * b.bounce : 0;
          wv[0] *= .6; wv[2] *= .6;
        }
        if (E.collide) E.collide(p, v, b);
        const vh = Math.hypot(v[0], v[2]);
        wv[0] += (v[2] * b.spin * .25 - wv[0]) * dt * 1.5;
        wv[2] += (-v[0] * b.spin * .25 + noise(t, b.hz * 7) * b.spin * vh * .05 - wv[2]) * dt * 1.5;
        wv[1] += (noise(t * .7, b.hx * 13) * b.spin * vh * .05 - wv[1]) * dt;
        if (onG && vh < 2) for (const i of [0, 2]) { wv[i] *= .9; const q = Math.round(r[i] / (Math.PI / 2)) * Math.PI / 2; r[i] += (q - r[i]) * .04; }
        if (sub_ > .5) for (const i of [0, 1, 2]) wv[i] *= .97;
        r[0] += wv[0] * dt; r[1] += wv[1] * dt; r[2] += wv[2] * dt;
        if (Math.abs(p[2]) > 900 || p[1] > 220 || p[1] < -60) b.done = true;
      }
    }
    for (const b of E.bodies) b.arr.set([b.p[0], b.p[1], b.p[2], b.r[0], b.r[1], b.r[2], b.live && !b.done ? 1 : b.done ? 2 : 0], f * 7);
  }
}

// write the simulated pose of every body for video time t
export function poseBodies(E, t, F) {
  const f = clamp(t, 0, (E.NF - 2) / E.FPS) * E.FPS, i0 = Math.min(E.NF - 2, Math.floor(f)), fr = f - i0;
  const w = F.level(t), D = E.DUMMY;
  for (const b of E.bodies) {
    const A = b.arr, o0 = i0 * 7, o1 = o0 + 7, st = A[o0 + 6];
    const px = lerp(A[o0], A[o1], fr), py = lerp(A[o0 + 1], A[o1 + 1], fr), pz = lerp(A[o0 + 2], A[o1 + 2], fr);
    const rx = lerp(A[o0 + 3], A[o1 + 3], fr), ry = lerp(A[o0 + 4], A[o1 + 4], fr), rz = lerp(A[o0 + 5], A[o1 + 5], fr);
    const visible = st === 1 || (st === 0 && !b.hidden);
    let wx = 0, wz = 0;
    // buildings (floors, bridge deck) never wobble before they tear loose
    if (st === 0 && F.wobble && b.kind !== 'floor' && b.kind !== 'deck') { const a = F.wobble(t) * (b.wob ?? 1); wx = a * Math.sin(t * 13 + b.hx * 40); wz = a * Math.sin(t * 9 + b.hz * 30); }
    if (b.kind === 'part') { b.src.visible = st === 0; b.obj.visible = st === 1; if (st === 1) { b.obj.position.set(px, py, pz); b.obj.rotation.set(rx, ry, rz); } continue; }
    if (b.obj) { b.obj.visible = visible; b.obj.position.set(px, py, pz); b.obj.rotation.set(rx + wx, ry, rz + wz); if (b.onPose) b.onPose(t, st, w); }
    else if (b.inst) {
      const s = visible ? b.inst.scale : 0, sv = b.inst.sv;
      D.position.set(px, py, pz); D.rotation.set(rx + wx, ry, rz + wz);
      if (sv) D.scale.set(visible ? sv[0] : 0, visible ? sv[1] : 0, visible ? sv[2] : 0); else D.scale.set(s, s, s);
      D.updateMatrix(); b.inst.im.setMatrixAt(b.inst.i, D.matrix);
    }
  }
  for (const k in E.IM) { E.IM[k].instanceMatrix.needsUpdate = true; if (E.IM[k].instanceColor) E.IM[k].instanceColor.needsUpdate = true; }
}
