// FENCES (baksteen Hekken): enclosures for a zoo, safari or dinosaur park – usable in any place.
//   TL.fences = [{ pts: [[x, z], ...], h: 6, double: 3 (second fence 3 m outside), electric: true, lamps: 4 (every 4th post),
//                  color, closed: false, sag: [[t, i, k]] (post i leans k 0..1 from time t: an animal pushes it) }]
//   TL.towers = [{ at: [x, z], ry, h: 9, name: 'tower' (adds shots: <name> on the platform, <name>-view looking at it) }]
//   TL.gates  = [{ at: [x, z], ry, w: 10, h: 8, sign: 'PARK', open: [[t, 0..1], ...] }]
// Lamps on fences and towers light up in the dark (E.lights) and go out with beats.powerOut / powerOff.
// Electric fences hum (AUDIO.hum) while the power is on.
import * as THREE from 'three';
import { rng, smooth, monotone } from './util.js';

function meshTex() {          // chain-link: a diamond grid with alpha
  const cv = document.createElement('canvas'); cv.width = cv.height = 64; const x = cv.getContext('2d');
  x.strokeStyle = 'rgba(200,205,205,0.95)'; x.lineWidth = 2.2;
  x.beginPath(); x.moveTo(0, 0); x.lineTo(64, 64); x.moveTo(64, 0); x.lineTo(0, 64); x.stroke();
  const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function build(E, TL, shots) {
  const { scene, lam, shadowed } = E, gy = (x, z) => (E.groundAt ? E.groundAt(x, z) : 0);
  const B = TL.beats, powerOn = t => !(E.powerOut?.(t)) && !(B.powerOff && t > B.powerOff[1] + 1.5) && !(B.powerOut != null && t > B.powerOut);
  const tex = meshTex();
  const lampOn = 0xffe2a8, lampOff = 0x3a3a36;

  for (const Fz of TL.fences || []) {
    const h = Fz.h ?? 6, rows = Fz.double ? [0, Fz.double] : [0];
    const pts = Fz.closed ? [...Fz.pts, Fz.pts[0]] : Fz.pts;
    for (const off of rows) {
      const posts = [];
      for (let s = 0; s < pts.length - 1; s++) {
        const [x0, z0] = pts[s], [x1, z1] = pts[s + 1], L = Math.hypot(x1 - x0, z1 - z0), nx = (z1 - z0) / L, nz = -(x1 - x0) / L;
        const n = Math.max(1, Math.round(L / 4));
        for (let i = 0; i <= n; i++) { if (s > 0 && i === 0) continue; const u = i / n; posts.push([x0 + (x1 - x0) * u + nx * off, z0 + (z1 - z0) * u + nz * off]); }
      }
      const postMat = lam(Fz.color ?? 0x5d5f5c), postG = new THREE.CylinderGeometry(.13, .16, h + 1, 6);
      const sag = (Fz.sag || []).map(([t, i, k]) => ({ t, i, k }));
      const groups = posts.map(([x, z], i) => {
        const g = new THREE.Group(); g.position.set(x, gy(x, z), z); scene.add(g);
        const p = shadowed(new THREE.Mesh(postG, postMat)); p.position.y = (h + 1) / 2 - .5; g.add(p);
        if (Fz.electric) for (let k = 0; k < 5; k++) { const ins = new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, .14, 6), lam(0xd8d2b8)); ins.position.set(0, 1 + k * (h - 1.6) / 4, .12); g.add(ins); }
        if (Fz.lamps && i % Fz.lamps === 0 && off === 0) {
          const arm = new THREE.Mesh(new THREE.BoxGeometry(.1, .1, .9), postMat); arm.position.set(0, h + .3, .4); g.add(arm);
          const lm = new THREE.MeshBasicMaterial({ color: lampOff }), bulb = new THREE.Mesh(new THREE.BoxGeometry(.5, .18, .35), lm); bulb.position.set(0, h + .2, .85); g.add(bulb);
          E.lights.push({ mat: lm, on: lampOn, off: lampOff, at: 0 });
        }
        return g;
      });
      // panels between posts (chain-link or electric wires), re-shaped when a post leans
      for (let i = 0; i < posts.length - 1; i++) {
        const [xa, za] = posts[i], [xb, zb] = posts[i + 1], L = Math.hypot(xb - xa, zb - za);
        const pg = new THREE.Group(); pg.position.set(xa, gy(xa, za), za); pg.rotation.y = Math.atan2(-(zb - za), xb - xa); scene.add(pg);
        if (Fz.electric) for (let k = 0; k < 5; k++) { const w = new THREE.Mesh(new THREE.BoxGeometry(L, .03, .03), lam(0x9a9a92)); w.position.set(L / 2, 1 + k * (h - 1.6) / 4, .12); pg.add(w); }
        else { const t2 = tex.clone(); t2.needsUpdate = true; t2.repeat.set(L / .6, h / .6);
          const m = new THREE.Mesh(new THREE.PlaneGeometry(L, h), new THREE.MeshLambertMaterial({ map: t2, transparent: true, alphaTest: .3, side: THREE.DoubleSide, color: 0xb9bdbd })); m.position.set(L / 2, h / 2, 0); pg.add(m); }
        const top = new THREE.Mesh(new THREE.BoxGeometry(L, .08, .08), postMat); top.position.set(L / 2, h, 0); pg.add(top);
        const mine = sag.filter(s => s.i === i || s.i === i + 1);
        if (mine.length) E.updates.push(t => { let k = 0; for (const s of mine) k = Math.max(k, s.k * smooth(s.t, s.t + .8, t)); pg.rotation.z = 0; pg.rotation.x = k * .5; });
      }
      sag.forEach(s => { const g = groups[s.i]; if (g) E.updates.push(t => { g.rotation.x = s.k * .5 * smooth(s.t, s.t + .8, t); }); });
    }
    if (Fz.electric) (E.hum ??= []).push(1);
  }

  for (const [ti, T] of (TL.towers || []).entries()) {
    const [x, z] = T.at, h = T.h ?? 9, y0 = gy(x, z), g = new THREE.Group(); g.position.set(x, y0, z); g.rotation.y = T.ry ?? 0; scene.add(g);
    const wood = lam(0x6b5038), dark = lam(0x3f3226);
    for (const [sx, sz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.35, h, .35), wood)); l.position.set(sx * 1.8, h / 2, sz * 1.8); l.rotation.set(sz * .05, 0, -sx * .05); g.add(l); }
    for (let k = 1; k < 3; k++) for (const r of [0, Math.PI / 2]) { const br = new THREE.Mesh(new THREE.BoxGeometry(4.2, .18, .18), wood); br.position.y = k * h / 3; br.rotation.y = r; br.position.z = r ? 0 : 1.8; g.add(br); const b2 = br.clone(); b2.position.z = r ? 0 : -1.8; if (r) b2.position.x = 1.8, br.position.x = -1.8; g.add(b2); }
    const deck = shadowed(new THREE.Mesh(new THREE.BoxGeometry(5.2, .3, 5.2), wood)); deck.position.y = h; g.add(deck);
    const cabin = shadowed(new THREE.Mesh(E.facadeBox(4.4, 2.6, 4.4, 2.2, 2.6), E.facadeMats(0x7a5c40, 'chalet', 0x3f3226))); cabin.position.y = h + 1.45; g.add(cabin);
    const roof = shadowed(new THREE.Mesh(new THREE.ConeGeometry(4.2, 1.8, 4), dark)); roof.position.y = h + 3.6; roof.rotation.y = Math.PI / 4; g.add(roof);
    for (let k = 0; k < 8; k++) { const st = new THREE.Mesh(new THREE.BoxGeometry(1.1, .1, .5), wood); st.position.set(2.4, (k + .5) * h / 8, -1.5 + k * .4); g.add(st); }
    const lm = new THREE.MeshBasicMaterial({ color: lampOff }), spot = new THREE.Mesh(new THREE.BoxGeometry(.6, .4, .4), lm); spot.position.set(0, h + 3, 2.3); g.add(spot);
    E.lights.push({ mat: lm, on: 0xfff1cc, off: lampOff, at: 0 });
    if (T.name && shots) {
      const f = new THREE.Vector3(0, 0, 1).applyAxisAngle(new THREE.Vector3(0, 1, 0), T.ry ?? 0);
      shots[T.name] = { pos: [x + f.x * 2.6, y0 + h + 1.9, z + f.z * 2.6], look: [x + f.x * 80, y0, z + f.z * 80], drift: [0, 0, 0], fov: 55 };
      shots[T.name + '-view'] = { pos: [x + f.x * 40 + f.z * 18, y0 + 3, z + f.z * 40 - f.x * 18], look: [x, y0 + h * .8, z], drift: [0, 0, 0], fov: 50 };
    }
    void ti;
  }

  for (const G of TL.gates || []) {
    const [x, z] = G.at, w = G.w ?? 10, h = G.h ?? 8, y0 = gy(x, z), g = new THREE.Group(); g.position.set(x, y0, z); g.rotation.y = G.ry ?? 0; scene.add(g);
    const wood = lam(0x5a4430);
    for (const s of [-1, 1]) { const p = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.1, h + 2, 1.1), wood)); p.position.set(s * (w / 2 + .6), (h + 2) / 2, 0); g.add(p);
      const cap = new THREE.Mesh(new THREE.ConeGeometry(.9, 1, 4), wood); cap.position.set(s * (w / 2 + .6), h + 2.5, 0); cap.rotation.y = Math.PI / 4; g.add(cap); }
    const beam = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w + 2.4, 1.4, .8), wood)); beam.position.y = h + 1.2; g.add(beam);
    if (G.sign) { const cv = document.createElement('canvas'); cv.width = 512; cv.height = 96; const c = cv.getContext('2d');
      c.fillStyle = '#2d2219'; c.fillRect(0, 0, 512, 96); c.fillStyle = '#e9dcc0'; c.font = '600 58px PF, Georgia, serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(G.sign, 256, 52);
      const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; document.fonts?.ready.then(() => { c.fillStyle = '#2d2219'; c.fillRect(0, 0, 512, 96); c.fillStyle = '#e9dcc0'; c.fillText(G.sign, 256, 52); tx.needsUpdate = true; });
      const sm = new THREE.Mesh(new THREE.PlaneGeometry(w, w * 96 / 512), new THREE.MeshLambertMaterial({ map: tx })); sm.position.set(0, h + 1.2, .42); g.add(sm); }
    const open = monotone(G.open || [[0, 0]]);
    const doors = [-1, 1].map(s => { const hinge = new THREE.Group(); hinge.position.set(s * w / 2, 0, 0); g.add(hinge);
      const d = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w / 2, h, .35), lam(0x6b5038))); d.position.set(-s * w / 4, h / 2, 0); hinge.add(d);
      for (const yy of [.2, .5, .8]) { const plank = new THREE.Mesh(new THREE.BoxGeometry(w / 2, .25, .45), wood); plank.position.set(-s * w / 4, h * yy, 0); hinge.add(plank); }
      return { hinge, s }; });
    E.updates.push(t => { const k = open(t); for (const D of doors) D.hinge.rotation.y = D.s * k * 1.45; });
  }
  E.fencePowerOn = powerOn;
}
