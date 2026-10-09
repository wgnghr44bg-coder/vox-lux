// Small brick "alarm": a siren pole (horn speakers, rotating amber light) and a roadblock (striped barriers,
// blinking lamps, a patrol car with a red/blue light bar). Usable in any place; both switch on at time `on`.
// Sound: the scenario adds TL.audio.siren = [[a, b], ...] (make_audio.py: rising and falling wail).
//   sirenPole(E, TL, x, z, { on, y })        roadblock(E, TL, x, z, { on, ry, y })
import * as THREE from 'three';

const blink = (t, on, hz, ph = 0) => t > on && Math.sin((t - on) * hz * Math.PI * 2 + ph) > 0;

export function sirenPole(E, TL, x, z, o = {}) {
  const { lam, shadowed } = E, g = new THREE.Group(), on = o.on ?? 1e9; g.position.set(x, o.y ?? E.groundAt(x, z), z); E.scene.add(g);
  const pole = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.12, .16, 11, 6), lam(0x6d6a62))); pole.position.y = 5.5; g.add(pole);
  const box = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.6, .8, .4), lam(0x9a9a92))); box.position.set(0, 2.2, .25); g.add(box);
  for (let k = 0; k < 4; k++) {        // four horn speakers, one per direction
    const h = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.42, .12, .9, 8, 1, true), lam(0xc9c6bc, { side: THREE.DoubleSide })));
    h.rotation.z = Math.PI / 2; const p = new THREE.Group(); p.rotation.y = k * Math.PI / 2; p.position.y = 10.4; h.position.x = .55; p.add(h); g.add(p);
  }
  const lampM = new THREE.MeshBasicMaterial({ color: 0x5a4a2a }), lamp = new THREE.Mesh(new THREE.CylinderGeometry(.2, .2, .35, 8), lampM); lamp.position.y = 11.2; g.add(lamp);
  E.updates.push(t => lampM.color.setHex(blink(t, on, 1.4) ? 0xffb02e : 0x5a4a2a));
  return g;
}

export function roadblock(E, TL, x, z, o = {}) {
  const { lam, shadowed } = E, g = new THREE.Group(), on = o.on ?? 1e9; g.position.set(x, o.y ?? E.groundAt(x, z), z); g.rotation.y = o.ry ?? 0; E.scene.add(g);
  // striped barrier boards on A-frames (texture: red/white stripes)
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 8; const c = cv.getContext('2d');
  for (let i = 0; i < 8; i++) { c.fillStyle = i % 2 ? '#e8e4da' : '#b8352b'; c.beginPath(); c.moveTo(i * 8, 0); c.lineTo(i * 8 + 8, 0); c.lineTo(i * 8 + 4, 8); c.lineTo(i * 8 - 4, 8); c.fill(); }
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const stripe = lam(0xffffff, { map: tex }), leg = lam(0xd8d4c8), lamps = [];
  const appear = o.appear ?? on - 1;               // the block is there from shortly before `on` (set appear: -1 to always show)
  [[-2.4, 0], [2.4, 0]].forEach(([dx]) => {
    const b = new THREE.Group(); b.position.set(0, 0, dx); g.add(b);
    const board = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.12, .4, 3.6), stripe)); board.position.y = 1; b.add(board);
    const board2 = board.clone(); board2.position.y = .45; b.add(board2);
    for (const sz of [-1.5, 1.5]) for (const sx of [-.35, .35]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.08, 1.25, .08), leg)); l.position.set(sx * .6, .6, sz); l.rotation.z = sx * .5; b.add(l); }
    const m = new THREE.MeshBasicMaterial({ color: 0x4a2a1a }), lmp = new THREE.Mesh(new THREE.SphereGeometry(.13, 8, 6), m); lmp.position.set(0, 1.35, 1.6); b.add(lmp); lamps.push(m);
  });
  // patrol car with a light bar, parked across the lane behind the barriers
  const car = new THREE.Group(); car.position.set(7, .75, 0); car.rotation.y = Math.PI / 2 + .3; g.add(car);
  const hull = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.9, .8, 4.6), lam(0xe6e2d8))); hull.position.y = -.05; car.add(hull);
  const cab = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.7, .65, 2.5), lam(0x2f4a3a))); cab.position.set(0, .65, .1); car.add(cab);
  const win = new THREE.Mesh(new THREE.BoxGeometry(1.72, .44, 2.3), lam(0x39444c)); win.position.set(0, .66, .1); car.add(win);
  const stripeC = new THREE.Mesh(new THREE.BoxGeometry(1.92, .16, 4.62), lam(0x2f4a3a)); stripeC.position.y = .02; car.add(stripeC);
  const wg = new THREE.CylinderGeometry(.36, .36, .26, 8); wg.rotateZ(Math.PI / 2);
  for (const [wx, wz] of [[-.9, 1.4], [.9, 1.4], [-.9, -1.4], [.9, -1.4]]) { const w = new THREE.Mesh(wg, lam(0x1c1d1f)); w.position.set(wx, -.42, wz); car.add(w); }
  const red = new THREE.MeshBasicMaterial({ color: 0x3a1a1a }), blue = new THREE.MeshBasicMaterial({ color: 0x1a1f3a });
  const r = new THREE.Mesh(new THREE.BoxGeometry(.7, .16, .3), red); r.position.set(-.4, 1.06, .1); car.add(r);
  const bl = new THREE.Mesh(new THREE.BoxGeometry(.7, .16, .3), blue); bl.position.set(.4, 1.06, .1); car.add(bl);
  // blinking: a little point light so the barriers and the road catch the colour (also in daylight, after bloom)
  const PL = new THREE.PointLight(0xff3020, 0, 18, 1.8); PL.position.set(7, 2.2, 0); g.add(PL);
  E.updates.push(t => {
    g.visible = t > appear;
    const a = blink(t, on, 1.6), b = blink(t, on, 1.6, Math.PI);
    red.color.setHex(a ? 0xff3a2a : 0x3a1a1a); blue.color.setHex(b ? 0x3a6bff : 0x1a1f3a);
    PL.color.setHex(a ? 0xff3020 : 0x3050ff); PL.intensity = t > on ? 25 : 0;
    lamps.forEach((m, i) => m.color.setHex(blink(t, on, 1, i * Math.PI) ? 0xffa030 : 0x4a2a1a));
  });
  return g;
}
