// Buildings shared by the places: flat-roof blocks, towers, gabled houses, chalets, water tower.
// Every building is a group with its pivot at the foot, so it can collapse (E.falls) if the
// place says so: o.fall = { rank, strength: { gravity: .9 }, mode } (rank = order of scripted falls).
import * as THREE from 'three';
import { rng } from './util.js';

function maybeFall(E, g, o, h, w, d) {
  if (!o.fall) return;
  E.falls.push({ g, h, w: Math.max(w, d), cx: o.x, cz: o.z, base: o.y ?? 0, ry: o.ry ?? 0, ...o.fall });
}

export function block(E, o) {
  const { shadowed, facadeMats, facadeBox } = E;
  const { x, z, w, d, floors = 4, color = 0x9c4a3a, kind = 'win', shop = true, storey = 3.5, roof } = o;
  const g = new THREE.Group(); g.position.set(x, o.y ?? 0, z); g.rotation.y = o.ry ?? 0; E.scene.add(g);
  const gfH = shop ? 4.2 : 0;
  if (shop) { const gf = shadowed(new THREE.Mesh(facadeBox(w, gfH, d), facadeMats(color, 'shop', roof))); gf.position.y = gfH / 2; g.add(gf); }
  const h = floors * storey, m = new THREE.Mesh(facadeBox(w, h, d, 5, storey), facadeMats(color, kind, roof));
  m.position.y = gfH + h / 2; m.castShadow = o.cast ?? true; m.receiveShadow = true; g.add(m);
  const H = gfH + h;
  if (o.cornice !== false) { const c = new THREE.Mesh(new THREE.BoxGeometry(w + .6, .5, d + .6), E.lam(new THREE.Color(color).multiplyScalar(.7))); c.position.y = H + .25; g.add(c); }
  // rooftop details that can break off: chimneys, water tanks
  const R = rng(Math.round(x * 13 + z * 7));
  if (o.chimneys) for (let i = 0; i < o.chimneys; i++) {
    const ch = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1, 2.4, 1), E.lam(0x7d4a3a))); ch.position.set((R() - .5) * (w - 2), H + 1.2, (R() - .5) * (d - 2)); g.add(ch);
    E.breaks.push({ src: ch, strength: { gravity: .5 + R() * .35, wind: .9 + R() * .5 }, k: .02, lift: .1, mu: .7, spin: .4, hx: .5, hy: 1.2, hz: .5, heavy: 1 });
  }
  if (o.balconies) for (let f = 1; f < floors; f += 2) for (const sx of [-.25, .25]) {
    const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.6, .25, 1.2), E.lam(0xb9b2a4)));
    const face = o.balconies; b.position.set(face[0] ? face[0] * (w / 2 + .6) : sx * w, gfH + f * storey, face[1] ? face[1] * (d / 2 + .6) : sx * d);
    if (face[0]) b.rotation.y = Math.PI / 2; g.add(b);
    E.breaks.push({ src: b, strength: { gravity: .62 + R() * .3, wind: .8 + R() * .4 }, k: .015, lift: .1, mu: .7, spin: .5, hx: 1.3, hy: .15, hz: .6, heavy: 1 });
  }
  maybeFall(E, g, o, H, w, d);
  return { g, h: H, m };
}

export function tower(E, o) {
  const { x, z, w, h, color = 0xb9bcbc } = o;
  const g = new THREE.Group(); g.position.set(x, o.y ?? 0, z); E.scene.add(g);
  const m = new THREE.Mesh(E.facadeBox(w, h, o.d ?? w, 4), E.facadeMats(color, 'tower'));
  m.position.y = h / 2; m.castShadow = true; m.receiveShadow = true; g.add(m);
  maybeFall(E, g, o, h, w, o.d ?? w);
  return { g, h };
}

// gabled house (village, suburb): walls + pitched roof; snow = white roof layer
export function house(E, o) {
  const { shadowed, lam } = E;
  const { x, z, w = 8, d = 10, h = 6, color = 0xd2c6ae, roof = 0x7a4a3a, kind = 'win' } = o;
  const g = new THREE.Group(); g.position.set(x, o.y ?? 0, z); g.rotation.y = o.ry ?? 0; E.scene.add(g);
  const walls = shadowed(new THREE.Mesh(E.facadeBox(w, h, d, 4, 3), E.facadeMats(color, kind)));
  walls.position.y = h / 2; g.add(walls);
  const rh = o.roofH ?? w * .45;
  const shape = new THREE.Shape(); shape.moveTo(-w / 2 - .6, 0); shape.lineTo(w / 2 + .6, 0); shape.lineTo(0, rh); shape.closePath();
  const rg = new THREE.ExtrudeGeometry(shape, { depth: d + 1.2, bevelEnabled: false }); rg.translate(0, 0, -(d + 1.2) / 2);
  const rmat = lam(o.snow ? 0xe9eef2 : roof); E.frost.push(rmat);
  const r = shadowed(new THREE.Mesh(rg, rmat)); r.position.y = h; g.add(r);
  if (o.chimney !== false) { const ch = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.8, 2, .8), lam(0x6d5a4a))); ch.position.set(w * .22, h + rh * .7, d * .2); g.add(ch);
    E.breaks.push({ src: ch, strength: { gravity: .55 + (x % 1 + 1) % 1 * .3, wind: .7 }, k: .02, lift: .1, mu: .7, spin: .4, hx: .4, hy: 1, hz: .4, heavy: 1 }); }
  maybeFall(E, g, o, h + rh, w, d);
  return { g, h: h + rh, walls };
}

export function waterTower(E, o) {
  const { shadowed, lam } = E, g = new THREE.Group(); g.position.set(o.x, o.y ?? 0, o.z); E.scene.add(g);
  const legM = lam(0x5b4f45), tankM = lam(0x8a6a4e);
  const H = o.h ?? 18;
  for (const [sx, sz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
    const l = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.25, .3, H, 5), legM)); l.position.set(sx * 2.4, H / 2, sz * 2.4); l.rotation.set(sz * .05, 0, -sx * .05); g.add(l);
  }
  for (const y of [H * .35, H * .7]) { const r = new THREE.Mesh(new THREE.BoxGeometry(5.4, .2, 5.4), legM); r.position.y = y; g.add(r); }
  const tank = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(4, 4, 6, 10), tankM)); tank.position.y = H + 3; g.add(tank);
  const cap = shadowed(new THREE.Mesh(new THREE.ConeGeometry(4.3, 2.4, 10), lam(0x5f4a3a))); cap.position.y = H + 7.2; g.add(cap);
  maybeFall(E, g, { ...o, fall: o.fall }, H + 8, 9, 9);
  return { g };
}
