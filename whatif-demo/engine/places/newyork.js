// NEW YORK STREET (baksteen, okt 2026): the avenue of places/street.js in New York style – no sea, glass and beige
// towers on the left (x < 0), red-brick walk-ups on the right with black fire escapes, green awnings and water tanks on
// the roofs, yellow taxis, yellow traffic-light housings, a hot dog cart and fire hydrants on the pavement, and the
// Chrysler Building's crown and spire far down the avenue. Everything that breaks or falls in street.js still does
// (beats windows, walls, floors, falls, powerOut); fire escapes and water tanks ride along with their floor.
//   Pavement right: x 10..16 (trees at 12.4, free lane 14..15.8); facades at x ±16.6. The avenue runs toward -z.
//   E.pigeonPerch: spots on the right pavement for TL.animals birds (perch + land/fly).
// Beats: as street.js. Shots: as street.js + 'chrysler'.
import * as THREE from 'three';
import { build as buildStreet } from './street.js';
import { rng } from '../util.js';

export function build(E, TL, F) {
  TL.streetStyle = 'newyork';
  const P = buildStreet(E, TL, F);
  const { scene, lam, shadowed } = E, R = rng(808), WALK = 16;
  const black = lam(0x1d1d1f), awning = lam(0x2f6b3e), tank = lam(0x7a5636), steel = lam(0x3a3836);

  // ground beyond the end of the avenue (the street place ends in the sea)
  { const g = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1400), lam(0x4a4a48)); g.rotation.x = -Math.PI / 2; g.position.set(0, -.02, -1200); g.receiveShadow = true; scene.add(g); }

  // dress the near buildings
  for (const b of E.nearBuildings || []) {
    const face = b.s * WALK;                                   // the facade plane toward the street
    if (b.s > 0) {
      // green awning over the shop front
      const a = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.4, .12, Math.min(8, b.len * .6)), awning));
      a.position.set(face - b.s * .7, 3.6, b.cz); a.rotation.z = b.s * .32; scene.add(a);
      // fire escape: a platform + railing + ladder per floor, fixed to that floor (falls with it)
      if (R() < .75) b.floors.forEach((m, f) => {
        const lx = face - b.s * .55 - m.position.x, w = Math.min(6, b.len * .45), zc = (R() - .5) * 2;
        const plat = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.1, .08, w), black)); plat.position.set(lx, -1.7, zc); m.add(plat);
        const rail = new THREE.Mesh(new THREE.BoxGeometry(.05, .9, w), black); rail.position.set(lx - b.s * .52, -1.25, zc); m.add(rail);
        const lad = new THREE.Mesh(new THREE.BoxGeometry(.5, .06, 3.6), black); lad.position.set(lx, -.1, zc); lad.rotation.x = (f % 2 ? 1 : -1) * .78; m.add(lad);
      });
      // a wooden water tank on some roofs (on the top floor: it comes down with it)
      const top = b.floors[b.floors.length - 1];
      if (top && R() < .55) {
        const g = new THREE.Group(); g.position.set((R() - .5) * 4, 1.75, (R() - .5) * (b.len * .4)); top.add(g);
        for (const [x, z] of [[-.9, -.9], [.9, -.9], [-.9, .9], [.9, .9]]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.15, 2.4, .15), steel)); l.position.set(x, 1.2, z); g.add(l); }
        const c = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 3, 10), tank)); c.position.y = 3.9; g.add(c);
        const r = shadowed(new THREE.Mesh(new THREE.ConeGeometry(1.65, 1.3, 10), lam(0x4a3a2c))); r.position.y = 6.05; g.add(r);
      }
    }
  }

  // the Chrysler Building, far down the avenue: setback shaft, terraced crown of arches, needle spire
  { const g = new THREE.Group(); g.position.set(-4, 0, -640); scene.add(g);
    const stone = lam(0xc7c2b6), silver = lam(0xd6dade, { emissive: 0x222428 });
    const shaft = (w, h, y) => { const m = new THREE.Mesh(E.facadeBox(w, h, w, 4), E.facadeMats(0xc7c2b6, 'tower')); m.position.y = y + h / 2; g.add(m); return y + h; };
    let y = shaft(60, 60, 0); y = shaft(46, 120, y); y = shaft(36, 60, y);
    for (let i = 0; i < 6; i++) { const r = 17 - i * 2.6, h = 9; const c = new THREE.Mesh(new THREE.CylinderGeometry(r * .82, r, h, 8), silver); c.position.y = y + h / 2; g.add(c);
      for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2, tri = new THREE.Mesh(new THREE.ConeGeometry(1.4, 4, 3), lam(0x2a2c30)); tri.position.set(Math.sin(a) * r * .88, y + 4.5, Math.cos(a) * r * .88); g.add(tri); }
      y += h; }
    const spire = new THREE.Mesh(new THREE.ConeGeometry(2.4, 55, 8), silver); spire.position.y = y + 27.5; g.add(spire);
    void stone; }

  // pavement props: fire hydrants, a hot dog cart with a blue/yellow umbrella
  for (const [x, z] of [[10.7, 18], [10.7, -14], [-10.7, 4], [10.7, -46]]) {
    const h = new THREE.Group(); h.position.set(x, .2, z); scene.add(h); const red = lam(0xc4302b);
    const body = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.16, .2, .7, 8), red)); body.position.y = .35; h.add(body);
    const cap = new THREE.Mesh(new THREE.SphereGeometry(.17, 8, 5, 0, Math.PI * 2, 0, Math.PI / 2), red); cap.position.y = .7; h.add(cap);
    const nub = new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, .5, 6), red); nub.rotation.z = Math.PI / 2; nub.position.y = .45; h.add(nub);
  }
  { const g = new THREE.Group(); g.position.set(11.4, .2, 15); scene.add(g);
    const box = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.9, .9, 1.8), lam(0xeeeeea))); box.position.y = .75; g.add(box);
    const top = new THREE.Mesh(new THREE.BoxGeometry(.95, .08, 1.85), lam(0xb9bcbc)); top.position.y = 1.24; g.add(top);
    const stripe = new THREE.Mesh(new THREE.BoxGeometry(.92, .18, 1.82), lam(0x2d5aa8)); stripe.position.y = 1.0; g.add(stripe);
    for (const z of [-.6, .6]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(.28, .28, .1, 10), black); w.rotation.z = Math.PI / 2; w.position.set(-.5, .28, z); g.add(w); }
    const pole = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, 1.5, 6), steel); pole.position.y = 2.0; g.add(pole);
    for (let k = 0; k < 8; k++) { const seg = shadowed(new THREE.Mesh(new THREE.ConeGeometry(1.2, .5, 8, 1, true, k / 8 * Math.PI * 2, Math.PI / 4), lam(k % 2 ? 0xf2c218 : 0x2d5aa8, { side: THREE.DoubleSide })));
      seg.position.y = 2.85; g.add(seg); }
    // a little steam from the cart
    E.hotdogCart = g;
  }
  E.pigeonPerch = Array.from({ length: 14 }, (_, i) => [13.6 + (i % 4) * .45, .26, 19 - Math.floor(i / 4) * .9 - (i % 2) * .3]);

  E.brandSpot = null;   // no logo billboard in New York (eigenaar, okt 2026)
  P.shots.chrysler = { pos: [2, 3, 30], look: [-4, 160, -640], drift: [0, 0, -1], fov: 40 };
  return P;
}
