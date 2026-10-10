// ANIMALS (baksteen Dieren): low-poly dog, fox, deer and birds that walk, trot, sniff, graze, sit and fly.
// Scenario: TL.animals = [
//   { kind: 'dog' | 'fox' | 'deer', path: [[t, x, z], ...], n: 1, spread: 1.5, lag: .4, color, scale, y,
//     act: 'sniff' | 'graze' | 'sit' | 'look'  (what it does when it stands still), antlers: true (deer),
//     leash: [x, z] (dog: an empty leash from its collar to that spot on the ground; leashHand: [x, y, z] + leashDrop: t = held until t),
//     acts: [[t, act], ...] (change what it does over time), shot: { name, from: [dx, dy, dz], fov } },
//   { kind: 'birds', n: 14, center: [x, y, z], radius: 12, perch: [[x, y, z], ...], land: t, fly: t, color },
// ]
// Path: waypoints in video time; between two equal points the animal stands still and does `act`.
// Before the first and after the last waypoint it stays there (visible: false with `hide: [a, b]`).
import * as THREE from 'three';
import { rng, hash, smooth, clamp, lerp } from './util.js';
import { isBig, bigAnimals } from './big-animals.js';   // dinosaurs, elephants, mammoths (baksteen Grote dieren)

const KINDS = {
  dog:  { len: .62, h: .5, leg: .32, neck: .2, head: .2, snout: .12, tail: .32, colors: [0x6b4a32, 0x2a2622, 0xb08a5a, 0xd8cdb8, 0x8a6a48], ears: 'flop', bush: false },
  fox:  { len: .55, h: .4, leg: .36, neck: .18, head: .18, snout: .14, tail: .45, colors: [0xbd5f26, 0xc66a2c], ears: 'point', bush: true, socks: 0x2b211b, tip: 0xece4d6 },
  lion: { len: 1.7, h: 1.0, leg: .55, neck: .25, head: .38, snout: .16, tail: .8, colors: [0xc49a5a, 0xb88a4e], ears: 'flop', bush: false, mane: 0x6a4424, tip: 0x3a2818 },   // Colosseum (ancient.js)
  horse: { len: 1.9, h: 1.3, leg: .95, neck: .7, head: .5, snout: .25, tail: .6, colors: [0x6a4a32, 0x3a2c22, 0x8a6a48, 0xd8cdb8], ears: 'point', bush: false, mane: 0x2a201a },
  deer: { len: 1.05, h: 1.0, leg: .7, neck: .45, head: .26, snout: .14, tail: .1, colors: [0x8a6646, 0x7d5c3f], ears: 'deer', bush: false, rump: 0xe8e0d0 },
};

function quadruped(E, kind, seed, o) {
  const K = KINDS[kind], R = rng(seed), { lam, shadowed } = E, S = m => shadowed(m);
  const col = o.color ?? K.colors[Math.floor(R() * K.colors.length)], fur = lam(col), dark = lam(new THREE.Color(col).multiplyScalar(.55));
  const g = new THREE.Group(); E.scene.add(g); g.scale.setScalar((o.scale ?? 1) * (.9 + R() * .2));
  const body = new THREE.Group(); body.position.y = K.leg + K.h * .25; g.add(body);
  const ell = new THREE.IcosahedronGeometry(1, 1);      // body: chest a bit bigger than the hips, soft low-poly ellipsoids
  const chest = S(new THREE.Mesh(ell, fur)); chest.scale.set(K.h * .26, K.h * .3, K.len * .36); chest.position.z = K.len * .17; body.add(chest);
  const hips = S(new THREE.Mesh(ell, fur)); hips.scale.set(K.h * .24, K.h * .26, K.len * .34); hips.position.set(0, .01, -K.len * .17); body.add(hips);
  if (kind === 'fox') { const bib = new THREE.Mesh(ell, E.lam(K.tip)); bib.scale.set(K.h * .16, K.h * .2, K.len * .14); bib.position.set(0, -K.h * .06, K.len * .4); body.add(bib); }
  if (K.rump) { const r = new THREE.Mesh(new THREE.CircleGeometry(K.h * .2, 8), lam(K.rump)); r.position.z = -K.len / 2 - .005; r.rotation.y = Math.PI; body.add(r); }
  const neck = new THREE.Group(); neck.position.set(0, K.h * .12, K.len / 2 - .04); body.add(neck);
  const nk = S(new THREE.Mesh(new THREE.CylinderGeometry(K.h * .13, K.h * .18, K.neck, 6), fur)); nk.position.y = K.neck / 2; neck.add(nk);
  neck.rotation.x = kind === 'deer' ? .35 : .7;
  const head = new THREE.Group(); head.position.y = K.neck; neck.add(head);
  const hd = S(new THREE.Mesh(new THREE.BoxGeometry(K.head * .8, K.head * .75, K.head), fur)); head.add(hd);
  if (K.mane && kind === 'lion') { const mn = S(new THREE.Mesh(new THREE.IcosahedronGeometry(K.head * .85, 0), lam(K.mane))); mn.scale.set(1, 1.05, .7); mn.position.z = -K.head * .3; head.add(mn); }
  else if (K.mane) { const mn = S(new THREE.Mesh(new THREE.BoxGeometry(.06, K.neck * .9, .18), lam(K.mane))); mn.position.set(0, K.neck * .5, -K.h * .1); neck.add(mn); }
  const sn = S(new THREE.Mesh(new THREE.BoxGeometry(K.head * .45, K.head * .4, K.snout), kind === 'fox' ? lam(K.tip) : fur)); sn.position.set(0, -K.head * .15, K.head / 2 + K.snout / 2 - .01); head.add(sn);
  const nose = new THREE.Mesh(new THREE.BoxGeometry(.04, .035, .02), lam(0x151312)); nose.position.set(0, -K.head * .05, K.head / 2 + K.snout); head.add(nose);
  for (const sx of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.BoxGeometry(.02, .02, .01), new THREE.MeshBasicMaterial({ color: 0x111111 })); eye.position.set(sx * K.head * .3, K.head * .12, K.head / 2 + .002); head.add(eye);
    let ear;
    if (K.ears === 'point') { ear = S(new THREE.Mesh(new THREE.ConeGeometry(.045, .11, 4), dark)); ear.position.set(sx * K.head * .26, K.head * .45, -.02); }
    else if (K.ears === 'deer') { ear = S(new THREE.Mesh(new THREE.ConeGeometry(.05, .16, 4), fur)); ear.position.set(sx * K.head * .45, K.head * .4, -.05); ear.rotation.z = -sx * 1; }
    else { ear = S(new THREE.Mesh(new THREE.BoxGeometry(.05, .12, .08), dark)); ear.position.set(sx * K.head * .42, K.head * .15, -.02); ear.rotation.z = sx * .25; }
    head.add(ear);
    if (kind === 'deer' && o.antlers) { const a = new THREE.Group(); a.position.set(sx * .06, K.head * .4, -.02); a.rotation.z = -sx * .35; head.add(a);
      const am = lam(0xcdbfa6), main = S(new THREE.Mesh(new THREE.CylinderGeometry(.012, .02, .42, 4), am)); main.position.y = .21; a.add(main);
      for (const [y, r] of [[.16, .9], [.3, .7]]) { const tn = new THREE.Mesh(new THREE.CylinderGeometry(.008, .014, .16, 4), am); tn.position.set(0, y, .05); tn.rotation.x = r; a.add(tn); } }
  }
  const tail = new THREE.Group(); tail.position.set(0, K.h * .12, -K.len / 2); body.add(tail);
  const tg = K.bush ? new THREE.ConeGeometry(.07, K.tail, 6) : new THREE.CylinderGeometry(.02, .035, K.tail, 5);
  const tl = S(new THREE.Mesh(tg, fur)); tl.position.y = K.tail / 2; if (K.bush) tl.rotation.x = Math.PI; tail.add(tl);
  if (K.tip) { const tp = new THREE.Mesh(new THREE.ConeGeometry(.05, .1, 6), lam(K.tip)); tp.position.y = K.tail; tail.add(tp); }
  tail.rotation.x = kind === 'deer' ? -2.6 : kind === 'fox' ? -2.1 : -2.3;
  const legs = [[1, 1], [-1, 1], [1, -1], [-1, -1]].map(([sx, sz]) => {
    const p = new THREE.Group(); p.position.set(sx * K.h * .17, K.leg, sz * (K.len / 2 - .07)); g.add(p);
    const l = S(new THREE.Mesh(new THREE.CylinderGeometry(K.h * .07, K.h * .04, K.leg, 5), fur)); l.position.y = -K.leg / 2; p.add(l);
    if (K.socks) { const sk = new THREE.Mesh(new THREE.CylinderGeometry(K.h * .052, K.h * .042, K.leg * .45, 5), lam(K.socks)); sk.position.y = -K.leg * .77; p.add(sk); }
    const paw = new THREE.Mesh(new THREE.BoxGeometry(K.h * .1, K.h * .05, K.h * .14), kind === 'deer' ? lam(0x2b2420) : K.socks ? lam(K.socks) : fur); paw.position.set(0, -K.leg + K.h * .025, K.h * .03); p.add(paw);
    return { p, front: sz > 0, side: sx };
  });
  let leash = null;
  if (o.leash) {            // a lead on the ground: from the collar to its loop where the owner dropped it
    leash = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()]), 12, .012, 4), lam(0xa3352b));
    E.scene.add(leash);
    const loop = new THREE.Mesh(new THREE.TorusGeometry(.09, .012, 4, 10), lam(0xa3352b)); loop.rotation.x = Math.PI / 2; loop.position.set(o.leash[0], .03, o.leash[1]); E.scene.add(loop);
    if (o.leashHand) E.updates.push(t => { loop.visible = t >= (o.leashDrop ?? 1e9) + .4; });
  }
  const ph = R() * 6, act = o.act ?? (kind === 'deer' ? 'graze' : 'sniff');
  const A = { g, kind, update(t, F, tv) {
    const s = o.pathAt(t);
    g.visible = s.visible !== false; if (!g.visible) { if (leash) leash.visible = false; return; }
    const gy = (E.groundAt?.(s.x, s.z) ?? 0) + (o.y ?? 0);
    g.position.set(s.x, gy, s.z); g.rotation.y = s.rot;
    const sp = s.speed, gait = sp > (kind === 'deer' ? 3 : 2.2) ? 2 : sp > .15 ? 1 : 0;   // stand / walk / run
    const freq = gait === 2 ? 2.2 + sp * .5 : 1.4 + sp * 1.4, amp = gait === 2 ? .75 : gait ? .45 : 0, tt = t * freq * 2;
    legs.forEach((L, i) => { const off = gait === 2 ? (L.front ? 0 : Math.PI * .8) + (L.side > 0 ? .3 : 0) : (i === 0 || i === 3 ? 0 : Math.PI);
      L.p.rotation.x = Math.sin(tt + off + ph) * amp; });
    body.position.y = K.leg + K.h * .25 + (gait === 2 ? Math.abs(Math.sin(tt + ph)) * .06 : gait ? Math.abs(Math.sin(tt + ph)) * .015 : 0);
    body.rotation.x = gait === 2 ? Math.sin(tt + ph) * .06 : 0;
    // standing still: sniff/graze (head down, now and then up), sit (dog), look (head up, turning)
    let actNow = act; for (const [ta, x] of o.acts || []) if (t >= ta) actNow = x;   // o.acts = [[t, 'sit'], [t2, 'look']]
    const idle = gait === 0 ? smooth(0, .6, s.still ?? 1) : 0, a = s.act ?? actNow;
    const up = Math.sin(t * .5 + ph) > .55 ? 1 : 0, nb = kind === 'deer' ? .35 : .7;
    let nx = nb, hy = 0;
    if (a === 'graze' || a === 'sniff') nx = lerp(nb, a === 'graze' ? 2.0 : 1.55, idle * (1 - up * .8));
    else if (a === 'look') { nx = lerp(nb, nb - .25, idle); hy = Math.sin(t * .4 + ph) * .7 * idle; }
    neck.rotation.x = nx; head.rotation.y = hy; head.rotation.x = a === 'sniff' ? -.2 * idle : 0;
    const sit = a === 'sit' && kind !== 'deer' ? idle : 0;
    body.rotation.x += -sit * .55; body.position.y -= sit * K.leg * .45;
    legs.forEach(L => { if (!L.front) { L.p.rotation.x = L.p.rotation.x * (1 - sit) - sit * 1.3; L.p.position.y = K.leg * (1 - sit * .45); } });
    neck.rotation.x -= sit * .35;
    tail.rotation.x = (kind === 'deer' ? -2.6 : kind === 'fox' ? -2.1 + (gait ? .5 : 0) : -2.3 + (gait ? -.4 : 0)) + (kind === 'dog' ? Math.sin(t * (gait ? 9 : 4) + ph) * .1 : 0);
    tail.rotation.z = kind === 'dog' ? Math.sin(t * (gait ? 9 : 5) + ph) * .35 : Math.sin(t * 1.3 + ph) * .1;
    if (leash) {               // collar -> ground -> the dropped loop
      leash.visible = true; g.updateMatrixWorld(true);
      const c = new THREE.Vector3(0, K.neck * .3, 0); neck.localToWorld(c);
      const gEnd = new THREE.Vector3(o.leash[0], .03, o.leash[1]), d = o.leashHand ? smooth(o.leashDrop ?? 1e9, (o.leashDrop ?? 1e9) + .45, t) : 1;
      const end = o.leashHand ? new THREE.Vector3(...o.leashHand).lerp(gEnd, d) : gEnd, mid = c.clone().lerp(end, .45); mid.y = lerp(Math.min(c.y, end.y) - .15, .03, d);   // held in a hand, then dropped
      leash.geometry.dispose(); leash.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([c, c.clone().lerp(mid, .5).setY(c.y * .35), mid, end]), 14, .012, 4);
    }
  } };
  E.animals.push(A); return A;
}

// waypoints [[t, x, z], ...] -> position, heading, speed, how long it has stood still
function waypoints(pts, hide) {
  return t => {
    if (hide && (t < hide[0] || t > hide[1])) return { visible: false };
    let i = 0; while (i < pts.length - 2 && t > pts[i + 1][0]) i++;
    const [ta, xa, za] = pts[i], [tb, xb, zb] = pts[Math.min(i + 1, pts.length - 1)];
    const k = tb > ta ? clamp((t - ta) / (tb - ta)) : 1, dist = Math.hypot(xb - xa, zb - za);
    const kk = k < 1 && k > 0 ? k * k * (3 - 2 * k) * .25 + k * .75 : k;   // soft start/stop
    const x = lerp(xa, xb, kk), z = lerp(za, zb, kk);
    let rot, speed = dist > .05 && k > 0 && k < 1 ? dist / (tb - ta) : 0, still = 0;
    if (speed > 0) rot = Math.atan2(xb - xa, zb - za);
    else {   // standing: face the way it came (or the way it will go)
      let j = i; while (j > 0 && Math.hypot(pts[j][1] - pts[j - 1][1], pts[j][2] - pts[j - 1][2]) < .05) j--;
      const p = pts[Math.max(0, j - 1)], q = pts[j];
      rot = j > 0 ? Math.atan2(q[1] - p[1], q[2] - p[2]) : pts.length > 1 ? Math.atan2(pts[pts.length - 1][1] - xa, pts[pts.length - 1][2] - za) : 0;
      let ts = ta; for (let m = i; m > 0 && Math.hypot(pts[m][1] - pts[m - 1][1], pts[m][2] - pts[m - 1][2]) < .05; m--) ts = pts[m - 1][0];
      still = t - (k >= 1 ? tb : ts);
      if (t < pts[0][0]) still = 9;
    }
    return { x, z, rot, speed, still };
  };
}

// a flock: circles around `center` with a little chaos, lands on the perches at `land`, takes off at `fly`
function birds(E, seed, o) {
  const R = rng(seed), n = o.n ?? 12, [cx, cy, cz] = o.center, rad = o.radius ?? 12, col = o.color ?? 0x2c2c30;
  const mat = E.lam(col), wingGeo = new THREE.PlaneGeometry(.26, .1); wingGeo.translate(.13, 0, 0);
  for (let i = 0; i < n; i++) {
    const g = new THREE.Group(); E.scene.add(g); g.scale.setScalar(.9 + R() * .3);
    const b = new THREE.Mesh(new THREE.SphereGeometry(.07, 6, 4), mat); b.scale.set(1, .9, 2.1); g.add(b);
    const hd = new THREE.Mesh(new THREE.SphereGeometry(.045, 6, 4), mat); hd.position.set(0, .05, .13); g.add(hd);
    const bk = new THREE.Mesh(new THREE.ConeGeometry(.012, .05, 4), E.lam(0x8a7a4a)); bk.rotation.x = Math.PI / 2; bk.position.set(0, .045, .18); g.add(bk);
    const tl = new THREE.Mesh(new THREE.PlaneGeometry(.08, .12), mat); tl.rotation.x = -Math.PI / 2; tl.position.set(0, 0, -.18); g.add(tl);
    const wings = [-1, 1].map(sx => { const w = new THREE.Mesh(wingGeo, new THREE.MeshLambertMaterial({ color: col, side: THREE.DoubleSide })); w.rotation.x = -Math.PI / 2; w.scale.x = sx; g.add(w); return w; });
    const ph = R() * 6, sp = .35 + R() * .2, rr = rad * (.6 + R() * .6), hh = (R() - .5) * 4, perch = o.perch?.[i % (o.perch?.length || 1)];
    const land = (o.land ?? 1e9) + R() * 1.5, fly = (o.fly ?? 1e9) + R() * .6, start = o.from ?? -1e9;
    const orbit = t => [cx + Math.cos(t * sp + ph) * rr + Math.sin(t * 1.3 + ph) * 1.5, cy + hh + Math.sin(t * .9 + ph * 2) * 1.2, cz + Math.sin(t * sp + ph) * rr * .7];
    E.animals.push({ g, kind: 'bird', update(t) {
      g.visible = t >= start;
      let p = orbit(t), flying = 1;
      if (perch) {
        const pp = [perch[0] + (hash(i, 5) - .5) * .8, perch[1], perch[2] + (hash(i, 6) - .5) * .8];
        const kIn = smooth(land, land + 2.5, t), kOut = smooth(fly, fly + 2, t), k = kIn * (1 - kOut);
        const q = kOut > 0 ? orbit(t) : p;
        p = [lerp(q[0], pp[0], k), lerp(q[1], pp[1], k) + Math.sin(k * Math.PI) * 1.5, lerp(q[2], pp[2], k)];
        flying = k > .97 ? 0 : 1;
      }
      const p2 = orbit(t + .05); g.position.set(...p);
      g.rotation.set(0, flying ? Math.atan2(p2[0] - p[0], p2[2] - p[2]) : hash(i, 8) * 6, 0);
      const flap = flying ? Math.sin(t * 22 + ph) * .9 : -.05;
      wings[0].rotation.y = -flap; wings[1].rotation.y = flap;
      if (!flying) { wings[0].rotation.set(-Math.PI / 2, .15, -1.3); wings[1].rotation.set(-Math.PI / 2, -.15, 1.3); hd.rotation.y = Math.sin(t * 1.7 + ph) * .6; }
      else { wings[0].rotation.x = wings[1].rotation.x = -Math.PI / 2; wings[0].rotation.z = wings[1].rotation.z = 0; }
    } });
  }
}

// scenario -> animals (+ an optional close shot on each)
export function animals(E, TL, shots) {
  (TL.animals || []).forEach((A, ai) => {
    if (A.kind === 'birds') return birds(E, 300 + ai, A);
    if (isBig(A.kind)) return bigAnimals(E, TL, A);
    const n = A.n ?? 1;
    for (let i = 0; i < n; i++) {
      const ox = i ? (hash(ai * 10 + i, 1) - .5) * 2 * (A.spread ?? 1.5) : 0, oz = i ? (hash(ai * 10 + i, 2) - .5) * 2 * (A.spread ?? 1.5) : 0, lag = i * (A.lag ?? .35);
      const wp = waypoints(A.path.map(([t, x, z]) => [t + lag, x + ox, z + oz]), A.hide);
      quadruped(E, A.kind, 600 + ai * 20 + i, { ...A, leash: i === 0 ? A.leash : null, antlers: A.antlers && i === 0, pathAt: wp, color: A.colors?.[i] ?? A.color });
    }
    if (A.shot && shots) { const [, x, z] = A.path[A.shot.at ?? 0], [dx, dy, dz] = A.shot.from, gy = E.groundAt?.(x, z) ?? 0;
      shots[A.shot.name] = { pos: [x + dx, gy + dy, z + dz], look: [x, gy + (A.shot.lookY ?? .5), z], drift: A.shot.drift || [0, 0, 0], fov: A.shot.fov ?? 45 }; }
  });
}
