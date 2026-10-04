// Handheld POV camera that looks at what happens, like a person standing there.
// Shots (TL.shots + place.shots) give the standpoint and the base direction. On top of that:
//  - every EVENT (impact, collapse, splash, snap, tear, glass) is a look target with a place,
//    a time and a weight; heavy bodies that break loose are followed while they move;
//    sky objects (E.skyObjects) pull the gaze up; TL.looks = [[t, [x,y,z], seconds, weight]] adds manual ones;
//  - the camera reacts 0.2-0.4 s late, turns with a slightly underdamped spring (a little
//    overshoot), stays >= 1.5 s on a target unless something much bigger happens, then looks around;
//  - never more than 70° from the base direction, never below -35° (no staring into the ground);
//  - always a soft handheld motion: breathing, small jitter, now and then a few degrees of roll,
//    plus shake that grows with the disaster and hard jolts on big hits.
// The gaze is simulated once over the whole video (deterministic), so any frame renders on its own.
import * as THREE from 'three';
import { clamp, hash, noise, smooth, lerp } from './util.js';

const D2R = Math.PI / 180;
const WEIGHT = { fire: 2.5, impact: 1, collapse: 4, splash: 2.2, snap: 1.2, tear: 1.6, glass: 1.4, crack: 1, sky: 3, look: 6, mover: 1.4 };
const HOLD = { fire: 3, impact: 1.6, collapse: 3.5, splash: 2.2, snap: 1.6, tear: 2, glass: 2, crack: 1.6, look: 2.5 };

export function createCamera(E, TL, P, F) {
  const FPS = E.FPS, STOP = TL.beats.stop, N = Math.ceil(TL.T_END * FPS) + 2, cam = E.camera;
  cam.rotation.order = 'YXZ';
  const shotAt = t => { let s = TL.shots[0]; for (const x of TL.shots) if (t >= x[0]) s = x; return { name: s[1], start: s[0], shot: P.shots[s[1]] }; };
  const posAt = (sh, t) => { const d = sh.shot.drift || [0, 0, 0], k = (t - sh.start) / 10, p = sh.shot.pos; return [p[0] + d[0] * k, p[1] + d[1] * k, p[2] + d[2] * k]; };
  const lookAtBase = (sh, t) => { const d = sh.shot.lookDrift || sh.shot.drift || [0, 0, 0], k = (t - sh.start) / 10, l = sh.shot.look; return [l[0] + d[0] * k, l[1] + d[1] * k, l[2] + d[2] * k]; };
  const dirOf = (from, to) => { const dx = to[0] - from[0], dy = to[1] - from[1], dz = to[2] - from[2];
    return [Math.atan2(-dx, -dz), Math.atan2(dy, Math.hypot(dx, dz)), Math.hypot(dx, dy, dz)]; };
  const wrap = a => Math.atan2(Math.sin(a), Math.cos(a));
  const bodyPos = (b, t) => { const f = Math.min(E.NF - 1, Math.max(0, Math.round(t * FPS))) * 7; return [b.arr[f], b.arr[f + 1], b.arr[f + 2]]; };

  // ---------- look targets ----------
  const T = [];
  for (const ev of E.EVENTS) {
    if (!(ev.kind in HOLD) || ev.t > STOP) continue;
    if (ev.kind === 'collapse') {
      const f = E.falls.find(f => f.cx === ev.x && f.cz === ev.z);
      T.push({ kind: 'collapse', t: ev.t, until: ev.t + HOLD.collapse, w: WEIGHT.collapse * (ev.e || 1),
        pos: t => [ev.x, (f ? f.base + Math.max(4, f.h * .45 - Math.max(0, t - ev.t) * 3) : 10), ev.z] });
    } else if (ev.x != null) {
      T.push({ kind: ev.kind, t: ev.t, until: ev.t + HOLD[ev.kind], w: WEIGHT[ev.kind] * (ev.e ?? .5) * (ev.heavy ? 1 + ev.heavy * .3 : 1),
        pos: () => [ev.x, (ev.y ?? 1) + 1, ev.z] });
    }
  }
  for (const b of E.bodies) if (b.heavy >= 2 && b.tRelReal != null && b.tRelReal < STOP && b.kind !== 'car') {
    T.push({ kind: 'mover', t: b.tRelReal, until: Math.min(STOP, b.tRelReal + 3), w: WEIGHT.mover * b.heavy, pos: t => bodyPos(b, t) });
  }
  for (const o of E.skyObjects || []) T.push({ kind: 'sky', t: o.t0, until: o.t1, w: (o.weight ?? WEIGHT.sky), pos: o.pos, sky: true });
  for (const [t, p, hold = 2.5, w = WEIGHT.look] of TL.looks || []) T.push({ kind: 'look', t, until: t + hold, w, pos: () => p });
  T.forEach((x, i) => { x.delay = .2 + hash(i, 77) * .2; });
  E.lookTargets = T;

  // ---------- simulate the gaze ----------
  const yawA = new Float32Array(N), pitchA = new Float32Array(N), tgtA = new Int16Array(N).fill(-1);
  let yaw = 0, pitch = 0, vy = 0, vp = 0, cur = null, curSince = 0, curVal = 0, lastShot = null;
  const SUB = 4, dt = 1 / FPS / SUB;
  for (let f = 0; f < N; f++) {
    const t = f / FPS, ts = Math.min(t, STOP), sh = shotAt(t), pos = posAt(sh, t);
    const [by, bp] = dirOf(pos, lookAtBase(sh, t));
    if (sh.start !== lastShot) { yaw = by; pitch = bp; vy = vp = 0; cur = null; lastShot = sh.start; }
    // pick the most important visible target
    let best = null, bestVal = 0, bestDir = null;
    for (const c of T) {
      if (ts < c.t + c.delay || ts > c.until || t > STOP + .5) continue;
      const [ty, tp, dist] = dirOf(pos, c.pos(ts));
      const dy = wrap(ty - by);
      if (Math.abs(dy) > 70 * D2R || tp < -35 * D2R || tp > 75 * D2R) continue;
      const val = c.w / (1 + dist / 90) * (c === cur ? 1.15 : 1);
      if (val > bestVal) { best = c; bestVal = val; bestDir = [ty, tp]; }
    }
    if (cur && (ts > cur.until || !best && ts > cur.until - .01)) cur = null;
    if (best && best !== cur && (!cur || (t - curSince >= 1.5 && bestVal > curVal) || bestVal > curVal * 2.5)) { cur = best; curSince = t; }
    let dyaw, dpitch;
    if (cur) {
      const [ty, tp, dist] = dirOf(pos, cur.pos(ts)); curVal = cur.w / (1 + dist / 90);
      dyaw = by + clamp(wrap(ty - by), -70 * D2R, 70 * D2R); dpitch = clamp(tp, -35 * D2R, 75 * D2R);
    } else {   // idle: look around a little, like a person taking it in
      dyaw = by + (noise(t * .11, 3.1) * 9 + noise(t * .23, 7.7) * 4) * D2R;
      dpitch = bp + noise(t * .17, 1.3) * 3 * D2R;
    }
    tgtA[f] = cur ? T.indexOf(cur) : -1;
    // underdamped spring: faster in the climax
    const hot = smooth(TL.beats.climax - 2, TL.beats.climax, t) * (1 - smooth(STOP, STOP + 2, t));
    const wn = lerp(cur ? 5.5 : 2.2, 8, hot), zeta = .62;
    for (let s = 0; s < SUB; s++) {
      vy += (-(wn * wn) * wrap(yaw - dyaw) - 2 * zeta * wn * vy) * dt; yaw += vy * dt;
      vp += (-(wn * wn) * (pitch - dpitch) - 2 * zeta * wn * vp) * dt; pitch += vp * dt;
    }
    yaw = by + clamp(wrap(yaw - by), -72 * D2R, 72 * D2R); pitch = clamp(pitch, -36 * D2R, 76 * D2R);
    yawA[f] = yaw; pitchA[f] = pitch;
  }

  // ---------- per frame ----------
  const _l = new THREE.Vector3();
  return {
    targetAt: tv => tgtA[Math.min(N - 1, Math.round(tv * FPS))],
    apply(tv) {
      const t = Math.min(tv, STOP), sh = shotAt(tv), pos = posAt(sh, tv);
      const f = clamp(tv * FPS, 0, N - 2), i = Math.floor(f), fr = f - i;
      let ya = yawA[i] + wrap(yawA[i + 1] - yawA[i]) * fr, pa = lerp(pitchA[i], pitchA[i + 1], fr);
      // shake grows with the disaster; hard jolts on big hits
      let shake = (F.rumble ? F.rumble(t) : 0) * (sh.shot.shake ?? 1) * 1.5;
      for (const ev of E.EVENTS) {
        if (ev.t > t || t - ev.t > 2 || ev.t > STOP) continue;
        const a = t - ev.t, dist = ev.x == null ? 30 : Math.hypot(ev.x - pos[0], ev.z - pos[2]);
        const amp = { impact: ev.e * .5, collapse: .6 * (ev.e || 1), splash: .2 * ev.e, snap: .12, crack: .06, glass: .05, tear: .08 }[ev.kind] || 0;
        shake += amp * Math.exp(-a * 5) / (1 + Math.max(0, dist - 15) / 30);
      }
      shake = Math.min(shake, .45);
      const calm = 1 - smooth(TL.beats.end - 1, TL.beats.end + 1, tv) * .6;
      // handheld: breathing, jitter, a little roll now and then
      const breathe = Math.sin(tv * 2 * Math.PI * .24) * .45 * D2R;
      const jy = (noise(tv * 1.7, 11) * .35 + noise(tv * 4.3, 5) * .12) * D2R * calm, jp = (noise(tv * 1.9, 21) * .3 + noise(tv * 4.9, 9) * .1) * D2R * calm;
      const roll = (noise(tv * .13, 41) * 2.2 + noise(tv * .9, 3) * .3) * D2R * calm;
      const sx = Math.sin(tv * 37.1) * .6 + Math.sin(tv * 23.3) * .4, sy = Math.sin(tv * 31.7) * .6 + Math.sin(tv * 19.9) * .4;
      ya += jy + sx * shake * .02; pa += breathe + jp + sy * shake * .02;
      cam.fov = sh.shot.fov || 60; cam.updateProjectionMatrix();
      cam.position.set(pos[0] + noise(tv * .5, 2) * .05 + sx * shake * .25, pos[1] + Math.sin(tv * 2 * Math.PI * .24) * .03 + sy * shake * .25, pos[2] + noise(tv * .5, 6) * .05);
      cam.rotation.set(pa, ya, roll + sx * shake * .03);
      // a point 60 m ahead (used to aim the sun's shadow map)
      _l.set(-Math.sin(ya) * Math.cos(pa), Math.sin(pa), -Math.cos(ya) * Math.cos(pa)).multiplyScalar(60).add(cam.position);
      return _l;
    },
  };
}
