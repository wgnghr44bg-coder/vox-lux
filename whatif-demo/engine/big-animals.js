// BIG ANIMALS (baksteen Grote dieren: dinosaurs, elephants, mammoths …): one rig for every species.
// Same scenario list as the small animals (animals.js: TL.animals); animals.js hands these kinds over to bigAnimals().
// A body is a smooth low-poly tube along a spine (tail tip -> neck end) that bends every frame
// (tail sway, neck turns towards what the animal looks at, breathing, walking bob), plus legs
// (2-bone IK + foot, walk cycle planted on the ground), a head with a jaw that opens (roar) and extras.
//
// Scenario: TL.animals = [{ kind, path: [[t, x, z], ...] | at: [x, z], rot, scale, herd: { n, spread, seed },
//   look: [[t, [x, y, z]] | [t, null]], roar: [t, ...], drink: [[a, b], ...], steps: true, prints: true (footprints), loud: 1, fly: {...} }]
//   kind: trex | sauropod | triceratops | raptor | velociraptor | pterosaur | shrew | elephant | mammoth
//   path: waypoints (the animal walks, legs follow the speed); without path it stands at `at` facing `rot`.
//   fly (pterosaur): { c: [x, y, z], r, period, dir } circles; or path with y: [[t, x, y, z], ...].
// Events: 'stomp' per footfall (sound, camera shake, puddle ripples), 'roar' (sound, the POV camera looks at it), 'call'.
// puddle(E, x, z, r): a puddle whose surface ripples at every stomp nearby.
import * as THREE from 'three';
import { rng, hash, clamp, smooth, lerp, monotone, noise } from './util.js';

const V = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
const UP = V(0, 1, 0), FWD = V(0, 0, 1);

// ---------- tube that can be re-shaped every frame ----------
function tube(rings, seg, colorFn, seed = 1) {
  const g = new THREE.BufferGeometry(), n = rings * seg;
  const pos = new Float32Array((n + 2) * 3), col = new Float32Array((n + 2) * 3), idx = [];
  for (let i = 0; i < rings - 1; i++) for (let j = 0; j < seg; j++) {
    const a = i * seg + j, b = i * seg + (j + 1) % seg, c = a + seg, d = b + seg; idx.push(a, c, b, b, c, d);
  }
  for (let j = 0; j < seg; j++) { idx.push(n, (j + 1) % seg, j); idx.push(n + 1, (rings - 1) * seg + j, (rings - 1) * seg + (j + 1) % seg); }
  g.setIndex(idx); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const jit = Float32Array.from({ length: n }, (_, k) => 1 + (hash(k, seed) - .5) * .09);
  const c = new THREE.Color();
  for (let i = 0; i < rings; i++) for (let j = 0; j < seg; j++) { colorFn(c, i / (rings - 1), j / seg); col.set([c.r, c.g, c.b], (i * seg + j) * 3); }
  colorFn(c, 0, .5); col.set([c.r, c.g, c.b], n * 3); colorFn(c, 1, .5); col.set([c.r, c.g, c.b], (n + 1) * 3);
  const T = V(), N = V(), B = V(), P = V();
  // pts: Vector3[rings], rx/ry: radii per ring, ref: the "up" of the cross-section
  g.shape = (pts, rx, ry, ref = UP) => {
    for (let i = 0; i < rings; i++) {
      T.subVectors(pts[Math.min(rings - 1, i + 1)], pts[Math.max(0, i - 1)]).normalize();
      N.copy(ref).addScaledVector(T, -ref.dot(T)); if (N.lengthSq() < 1e-6) N.set(1, 0, 0); N.normalize(); B.crossVectors(T, N);
      for (let j = 0; j < seg; j++) {
        const a = j / seg * Math.PI * 2, k = jit[i * seg + j];
        P.copy(pts[i]).addScaledVector(N, Math.cos(a) * ry[i] * k).addScaledVector(B, Math.sin(a) * rx[i] * k);
        pos.set([P.x, P.y, P.z], (i * seg + j) * 3);
      }
    }
    pos.set([pts[0].x, pts[0].y, pts[0].z], n * 3); pos.set([pts[rings - 1].x, pts[rings - 1].y, pts[rings - 1].z], (n + 1) * 3);
    g.attributes.position.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere();
  };
  return g;
}
const vcol = () => new THREE.MeshLambertMaterial({ color: 0xffffff, vertexColors: true, flatShading: true });
// box with a tapered front (heads, beaks): back w0 x h0, front w1 x h1, length L along +z
function wedge(w0, h0, w1, h1, L, dy = 0) {
  const g = new THREE.BoxGeometry(1, 1, L, 1, 1, 2), p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const u = p.getZ(i) / L + .5, w = lerp(w0, w1, u), h = lerp(h0, h1, u);
    p.setXYZ(i, p.getX(i) * w, p.getY(i) * h + dy * u, p.getZ(i)); }
  g.translate(0, 0, L / 2); g.computeVertexNormals(); return g;
}
function part(E, geo, color, p = [0, 0, 0], r = [0, 0, 0], s = [1, 1, 1], parent) {
  const m = E.shadowed(new THREE.Mesh(geo, E.lam(color))); m.position.set(...p); m.rotation.set(...r); m.scale.set(...s); parent?.add(m); return m;
}
// a static curved tube (horn, tusk): points + radii
function staticTube(E, pts, r, color, parent, seg = 6) {
  const g = tube(pts.length, seg, c => c.set(color)); g.shape(pts.map(p => V(...p)), r, r); const m = E.shadowed(new THREE.Mesh(g, vcol())); parent?.add(m); return m;
}
function teeth(E, g, n, x, y, z0, dz, up, color = 0xefe8d6, s = 1) {
  for (const sx of [-1, 1]) for (let k = 0; k < n; k++) part(E, new THREE.ConeGeometry(.055 * s, .2 * s, 3), color, [sx * x, y, z0 + k * dz], [up ? 0 : Math.PI, 0, 0], [1, 1, 1], g);
}
function eyes(E, g, x, y, z, r = .09) { for (const s of [-1, 1]) part(E, new THREE.IcosahedronGeometry(r, 0), 0x17140f, [s * x, y, z], [0, 0, 0], [1, 1, 1], g); }

// ---------- species ----------
// spine: [z, y, rx, ry] tail tip -> neck end (metres, +z forward); hip/neck: node index where the tail ends / the neck starts
// legs: hip/shoulder [x, y, z], L: [thigh, shin, foot], r: radii at hip, knee, ankle, toe, bend: +1 knee forward, digi: foot angle from vertical
const SPECIES = {
  trex: {
    mass: 1, stride: 2.4, duty: .6, bob: .06, tailSway: .5, neckTurn: .9, roarDur: 2.6, call: 'roar',
    colors: { top: 0x5f5a36, belly: 0xb4a57a, stripe: 0x433f26, stripes: 7 },
    spine: [[-7.4, 3.0, .05, .06], [-5.8, 3.3, .3, .34], [-4, 3.65, .58, .62], [-2.2, 3.95, .9, .95], [-.4, 4.1, 1.15, 1.3],
            [1.1, 4.0, 1.2, 1.5], [2.3, 4.15, 1.0, 1.2], [3.1, 4.55, .72, .82], [3.7, 5.0, .62, .66], [4.15, 5.3, .52, .55]],
    hip: 4, neck: 7,
    legs: [{ at: [-.85, 3.6, -.2], L: [1.55, 1.5, .8], r: [.95, .5, .22, .15], bend: 1, digi: 1.0, phase: 0 },
           { at: [.85, 3.6, -.2], L: [1.55, 1.5, .8], r: [.95, .5, .22, .15], bend: 1, digi: 1.0, phase: .5 }],
    arms: [{ at: [-.62, 3.75, 2.3], pts: [[0, 0, 0], [-.12, -.35, .2], [-.1, -.55, .45]], r: [.16, .1, .05] },
           { at: [.62, 3.75, 2.3], pts: [[0, 0, 0], [.12, -.35, .2], [.1, -.55, .45]], r: [.16, .1, .05] }],
    head(E, A) {
      const g = new THREE.Group(), c = A.colors.top, b = A.colors.belly;
      part(E, wedge(1.05, 1.15, .62, .62, 1.75, -.1), c, [0, .05, -.15], [0, 0, 0], [1, 1, 1], g);
      part(E, wedge(.95, .2, .5, .14, 1.3), A.colors.stripe, [0, .62, -.05], [0, 0, 0], [1, 1, 1], g);                    // brow ridge
      part(E, new THREE.BoxGeometry(.9, .06, 1.35), 0x4a2522, [0, -.42, .55], [0, 0, 0], [1, 1, 1], g);                    // mouth
      teeth(E, g, 7, .32, -.48, .2, .2, false);
      eyes(E, g, .42, .38, .55, .085);
      const jaw = new THREE.Group(); jaw.position.set(0, -.42, -.05); g.add(jaw);
      part(E, wedge(.92, .42, .5, .22, 1.6, .02), b, [0, -.18, 0], [0, 0, 0], [1, 1, 1], jaw);
      teeth(E, jaw, 6, .27, .06, .35, .2, true);
      A.jaw = (k) => { jaw.rotation.x = k * .62; };
      return g;
    },
  },
  sauropod: {
    mass: 1.7, stride: 2.2, duty: .65, bob: .05, tailSway: .35, neckTurn: .6, roarDur: 3, call: 'boom',
    colors: { top: 0x6f6a5c, belly: 0xa79f8a, stripe: 0x5a554a, stripes: 0 },
    spine: [[-17, 3.6, .08, .1], [-13, 5.0, .55, .6], [-9, 6.2, 1.05, 1.15], [-5, 7.0, 1.7, 1.8], [-2, 7.4, 2.1, 2.3],
            [1.2, 7.3, 2.3, 2.6], [3.8, 7.4, 1.95, 2.25], [5.8, 8.4, 1.25, 1.45], [8.0, 10.1, .9, .98], [10.2, 11.9, .66, .7],
            [12.2, 13.4, .5, .52], [13.8, 14.4, .4, .42]],
    hip: 4, neck: 7,
    legs: [{ at: [-1.5, 5.5, -2.2], L: [2.6, 2.3, .55], r: [1.05, .72, .58, .62], bend: 1, digi: 0, phase: 0, foot: 'pad' },
           { at: [-1.55, 5.6, 3.9], L: [2.6, 2.4, .5], r: [.85, .6, .52, .56], bend: -1, digi: 0, phase: .25, foot: 'pad' },
           { at: [1.5, 5.5, -2.2], L: [2.6, 2.3, .55], r: [1.05, .72, .58, .62], bend: 1, digi: 0, phase: .5, foot: 'pad' },
           { at: [1.55, 5.6, 3.9], L: [2.6, 2.4, .5], r: [.85, .6, .52, .56], bend: -1, digi: 0, phase: .75, foot: 'pad' }],
    head(E, A) {
      const g = new THREE.Group(), c = A.colors.top;
      part(E, wedge(.5, .55, .4, .32, 1.0, -.12), c, [0, 0, -.2], [.25, 0, 0], [1, 1, 1], g);
      eyes(E, g, .25, .18, .1, .06);
      const jaw = new THREE.Group(); jaw.position.set(0, -.2, -.1); g.add(jaw);
      part(E, wedge(.42, .16, .34, .1, .85), A.colors.belly, [0, -.05, 0], [.25, 0, 0], [1, 1, 1], jaw);
      A.jaw = k => { jaw.rotation.x = k * .45; };
      return g;
    },
  },
  triceratops: {
    mass: .7, stride: 1.5, duty: .62, bob: .04, tailSway: .3, neckTurn: .5, roarDur: 1.8, call: 'bellow',
    colors: { top: 0x6e5b3e, belly: 0xb09a74, stripe: 0x54452f, stripes: 5 },
    spine: [[-4.9, 1.5, .05, .07], [-3.6, 1.95, .35, .38], [-2.3, 2.35, .72, .78], [-1, 2.65, 1.15, 1.25],
            [.6, 2.5, 1.25, 1.35], [1.8, 2.25, 1.0, 1.1], [2.55, 2.05, .72, .78], [2.95, 1.98, .62, .64]],
    hip: 3, neck: 6,
    legs: [{ at: [-.8, 2.05, -1.0], L: [1.05, .85, .3], r: [.5, .34, .26, .3], bend: 1, digi: .15, phase: 0, foot: 'pad' },
           { at: [-.85, 1.65, 1.95], L: [.85, .7, .22], r: [.4, .3, .24, .27], bend: -1, digi: .1, phase: .25, foot: 'pad' },
           { at: [.8, 2.05, -1.0], L: [1.05, .85, .3], r: [.5, .34, .26, .3], bend: 1, digi: .15, phase: .5, foot: 'pad' },
           { at: [.85, 1.65, 1.95], L: [.85, .7, .22], r: [.4, .3, .24, .27], bend: -1, digi: .1, phase: .75, foot: 'pad' }],
    neckRest: -.25,
    head(E, A) {
      const g = new THREE.Group(), c = A.colors.top;
      part(E, wedge(.95, .95, .45, .55, 1.5, -.35), c, [0, 0, -.1], [0, 0, 0], [1, 1, 1], g);                       // face
      part(E, new THREE.ConeGeometry(.28, .7, 4), 0x3f362a, [0, -.45, 1.45], [Math.PI / 2 + .5, Math.PI / 4, 0], [1, 1, .8], g);  // beak
      const frill = part(E, new THREE.CylinderGeometry(1.45, 1.45, .14, 9, 1), A.colors.belly, [0, .75, -.35], [-1.05, 0, 0], [1, 1, .85], g);
      part(E, new THREE.CylinderGeometry(1.5, 1.5, .1, 9, 1), A.colors.stripe, [0, .72, -.42], [-1.05, 0, 0], [1, 1, .85], g);
      for (let k = 0; k < 9; k++) { const a = (k / 8 - .5) * 2.6; part(E, new THREE.ConeGeometry(.12, .35, 4), 0xd8cfb4,
        [Math.sin(a) * 1.45, .72 + Math.cos(a) * 1.45 * .55, -.42 - Math.cos(a) * .9], [-1.05 + Math.cos(a) * .2, 0, -a], [1, 1, 1], g); }
      for (const s of [-1, 1]) staticTube(E, [[s * .32, .35, .45], [s * .38, .7, .95], [s * .36, .95, 1.6]], [.14, .09, .02], 0xe2d8bc, g);   // brow horns
      staticTube(E, [[0, -.05, 1.05], [0, .15, 1.25], [0, .3, 1.35]], [.1, .06, .02], 0xe2d8bc, g);   // nose horn
      eyes(E, g, .43, .25, .35, .07);
      void frill; A.jaw = () => {};
      return g;
    },
  },
  raptor: {   // Utahraptor-size (about 5.5 m, as heavy as a horse), feathered
    mass: .12, stride: 1.1, duty: .55, bob: .05, tailSway: .12, neckTurn: 1.2, roarDur: 1.2, call: 'hiss', feathers: true,
    colors: { top: 0x5b4a3a, belly: 0xc7b79b, stripe: 0x2e2620, stripes: 9 },
    spine: [[-3.4, 1.55, .04, .05], [-2.4, 1.58, .1, .12], [-1.4, 1.62, .2, .23], [-.6, 1.66, .32, .35], [0, 1.66, .4, .44],
            [.6, 1.62, .38, .46], [1.0, 1.66, .3, .36], [1.25, 1.86, .2, .22], [1.42, 2.08, .15, .16], [1.56, 2.26, .13, .14]],
    hip: 4, neck: 7,
    legs: [{ at: [-.27, 1.5, 0], L: [.62, .58, .42], r: [.24, .14, .07, .05], bend: 1, digi: 1.05, phase: 0 },
           { at: [.27, 1.5, 0], L: [.62, .58, .42], r: [.24, .14, .07, .05], bend: 1, digi: 1.05, phase: .5 }],
    arms: [{ at: [-.25, 1.55, .95], pts: [[0, 0, 0], [-.12, -.2, .15], [-.1, -.35, .4]], r: [.08, .05, .03], wing: true },
           { at: [.25, 1.55, .95], pts: [[0, 0, 0], [.12, -.2, .15], [.1, -.35, .4]], r: [.08, .05, .03], wing: true }],
    head(E, A) {
      const g = new THREE.Group(), c = A.colors.top;
      part(E, wedge(.3, .3, .13, .14, .62, -.04), c, [0, .02, -.05], [0, 0, 0], [1, 1, 1], g);
      for (let k = 0; k < 4; k++) part(E, new THREE.ConeGeometry(.04, .22, 3), A.colors.stripe, [0, .2, -.05 - k * .07], [-.9, 0, 0], [1, 1, 1], g);
      eyes(E, g, .13, .1, .18, .035);
      teeth(E, g, 5, .055, -.1, .2, .07, false, 0xefe8d6, .45);
      const jaw = new THREE.Group(); jaw.position.set(0, -.1, -.02); g.add(jaw);
      part(E, wedge(.24, .1, .1, .05, .55), A.colors.belly, [0, -.04, 0], [0, 0, 0], [1, 1, 1], jaw);
      A.jaw = k => { jaw.rotation.x = k * .55; };
      return g;
    },
  },
  shrew: {   // a small furry mammal of the Cretaceous (about 12 cm)
    mass: 0, stride: .03, duty: .5, bob: .004, tailSway: .3, neckTurn: 1.2, roarDur: .4, call: null,
    colors: { top: 0x5a4636, belly: 0x9c8468, stripe: 0x4a392c, stripes: 0 },
    spine: [[-.14, .03, .004, .004], [-.09, .032, .006, .006], [-.045, .035, .022, .022], [-.015, .04, .03, .03], [.02, .04, .028, .028],
            [.045, .038, .021, .021], [.06, .039, .016, .016]],
    hip: 2, neck: 5,
    legs: [{ at: [-.016, .03, -.03], L: [.014, .013, .008], r: [.009, .006, .004, .004], bend: 1, digi: .6, phase: 0 },
           { at: [-.016, .03, .035], L: [.013, .012, .006], r: [.008, .005, .004, .004], bend: -1, digi: .3, phase: .5 },
           { at: [.016, .03, -.03], L: [.014, .013, .008], r: [.009, .006, .004, .004], bend: 1, digi: .6, phase: .5 },
           { at: [.016, .03, .035], L: [.013, .012, .006], r: [.008, .005, .004, .004], bend: -1, digi: .3, phase: 0 }],
    head(E, A) {
      const g = new THREE.Group();
      part(E, new THREE.ConeGeometry(.016, .045, 6), A.colors.top, [0, 0, .015], [Math.PI / 2, 0, 0], [1, 1, 1], g);
      part(E, new THREE.IcosahedronGeometry(.004, 0), 0x2a1d18, [0, 0, .038], [0, 0, 0], [1, 1, 1], g);
      for (const s of [-1, 1]) part(E, new THREE.CircleGeometry(.008, 6), 0x7a5e4a, [s * .011, .012, -.002], [0, s * .6, 0], [1, 1, 1], g);
      eyes(E, g, .009, .007, .012, .0025);
      A.jaw = () => {};
      return g;
    },
  },
  elephant: {
    mass: .6, stride: 1.4, duty: .6, bob: .04, tailSway: .5, neckTurn: .5, roarDur: 1.8, call: 'trumpet',
    colors: { top: 0x7b7670, belly: 0x8f8a83, stripe: 0x6d6862, stripes: 0 },
    spine: [[-2.0, 1.5, .03, .03], [-2.25, 2.3, .07, .07], [-1.7, 2.6, .9, 1.0], [-.2, 2.55, 1.15, 1.3], [1.1, 2.65, 1.05, 1.2],
            [1.8, 2.85, .75, .85], [2.15, 2.95, .65, .7]],
    hip: 2, neck: 5, tailHang: true,
    legs: [{ at: [-.6, 1.95, -1.4], L: [1.0, .85, .15], r: [.45, .32, .3, .34], bend: 1, digi: 0, phase: 0, foot: 'pad' },
           { at: [-.65, 2.0, 1.2], L: [1.05, .85, .15], r: [.42, .32, .3, .34], bend: -1, digi: 0, phase: .25, foot: 'pad' },
           { at: [.6, 1.95, -1.4], L: [1.0, .85, .15], r: [.45, .32, .3, .34], bend: 1, digi: 0, phase: .5, foot: 'pad' },
           { at: [.65, 2.0, 1.2], L: [1.05, .85, .15], r: [.42, .32, .3, .34], bend: -1, digi: 0, phase: .75, foot: 'pad' }],
    head(E, A) { return trunkHead(E, A, { ears: .95, tusk: .9 }); },
  },
};
SPECIES.velociraptor = { ...SPECIES.raptor, scale: .32 };     // turkey-size (about 15 kg)
SPECIES.mammoth = { ...SPECIES.elephant, call: 'trumpet', colors: { top: 0x4e3626, belly: 0x5e4330, stripe: 0x3e2a1d, stripes: 0 }, hair: true,
  spine: SPECIES.elephant.spine.map(([z, y, rx, ry], i) => [z, y + (i === 4 ? .35 : 0), rx * 1.08, ry * (i === 4 ? 1.25 : 1.08)]),
  head(E, A) { return trunkHead(E, A, { ears: .5, tusk: 1.9 }); } };

// elephant / mammoth head: dome, ears, tusks and a trunk that swings (a tube re-shaped every frame)
function trunkHead(E, A, o) {
  const g = new THREE.Group(), c = A.colors.top;
  part(E, new THREE.IcosahedronGeometry(.7, 1), c, [0, .1, .2], [0, 0, 0], [.95, 1.05, .9], g);
  for (const s of [-1, 1]) {
    part(E, new THREE.CircleGeometry(.75 * o.ears, 7), A.colors.stripe, [s * .62, -.05, -.05], [0, s * 1.25, 0], [1, 1.25, 1], g).material.side = THREE.DoubleSide;
    const L = o.tusk; staticTube(E, [[s * .3, -.35, .55], [s * .4, -.75, .55 + L * .45], [s * .3, -.6, .55 + L * .9], [s * .15, -.2, .5 + L * 1.05]].slice(0, L > 1.2 ? 4 : 3),
      [.1, .08, .05, .03].slice(0, L > 1.2 ? 4 : 3), 0xe9e0c8, g);
  }
  eyes(E, g, .48, .2, .5, .05);
  const R = 12, tg = tube(R, 7, (cc, u) => cc.set(c).multiplyScalar(1 - u * .15), 77), trunk = E.shadowed(new THREE.Mesh(tg, vcol())); g.add(trunk);
  const pts = Array.from({ length: R }, () => V()), rr = Array.from({ length: R }, (_, i) => lerp(.32, .09, i / (R - 1)));
  A.jaw = () => {};
  A.trunk = (t, raise) => {     // hangs and swings; raise 0..1 curls it up (trumpet)
    for (let i = 0; i < R; i++) { const u = i / (R - 1), sw = Math.sin(t * 1.3 - u * 2) * .18 * u;
      const down = lerp(-1.9, .2, raise * u) * u, fwd = .6 + u * lerp(.45, 1.4, raise);
      pts[i].set(sw, .05 + down, fwd + Math.sin(u * 2.5) * .15 * (1 - raise)); }
    tg.shape(pts, rr, rr, FWD);
  };
  return g;
}

// ---------- the walk path ----------
function track(o, TL, FPS) {
  const N = Math.ceil((TL.T_END + 1) * FPS) + 1, P = new Float32Array(N * 4);   // x, z, heading, distance
  const pts = o.path || [[0, ...(o.at || [0, 0])]];
  const fx = monotone(pts.map(p => [p[0], p[1]])), fz = monotone(pts.map(p => [p[0], p[2]]));
  let head = o.rot ?? 0, dist = 0, px = fx(0), pz = fz(0);
  for (let f = 0; f < N; f++) {
    const t = f / FPS, x = fx(t), z = fz(t), dx = x - px, dz = z - pz, d = Math.hypot(dx, dz);
    if (d > 1e-4) { const want = Math.atan2(dx, dz); let dd = Math.atan2(Math.sin(want - head), Math.cos(want - head)); head += dd * Math.min(1, .12 + d * 3); }
    if (o.face) for (const [tf, a] of o.face) if (t >= tf) head = a;
    dist += d; px = x; pz = z; P.set([x, z, head, dist], f * 4);
  }
  // heading: blend towards the next direction a little earlier (no snapping at waypoints)
  return { N, at: t => { const f = clamp(t * FPS, 0, N - 1.001), i = Math.floor(f), k = f - i, a = i * 4, b = a + 4;
    const dh = Math.atan2(Math.sin(P[b + 2] - P[a + 2]), Math.cos(P[b + 2] - P[a + 2]));
    return { x: lerp(P[a], P[b], k), z: lerp(P[a + 1], P[b + 1], k), head: P[a + 2] + dh * k, dist: lerp(P[a + 3], P[b + 3], k),
      speed: (P[Math.min(N - 1, i + 2) * 4 + 3] - P[Math.max(0, i - 2) * 4 + 3]) / (4 / FPS) }; } };
}

// ---------- one animal ----------
export function animal(E, TL, kind, o = {}) {
  const S = SPECIES[kind]; if (!S) throw new Error('unknown animal ' + kind);
  if (kind === 'pterosaur') return pterosaur(E, TL, o);
  const FPS = E.FPS, STOP = TL.beats.stop, sc = (o.scale ?? 1) * (S.scale ?? 1), seed = o.seed ?? 1, R = rng(seed * 31 + 7);
  const A = { colors: { ...S.colors, ...(o.colors || {}) } };
  const root = new THREE.Group(), body = new THREE.Group(); root.add(body); root.scale.setScalar(sc); E.scene.add(root);
  const tr = track(o, TL, FPS);

  // body tube
  const NS = S.spine.length, RINGS = 44, SEG = kind === 'shrew' ? 7 : 11;
  const ringU = i => i / (RINGS - 1) * (NS - 1);
  const top = new THREE.Color(A.colors.top), bel = new THREE.Color(A.colors.belly), str = new THREE.Color(A.colors.stripe);
  const bodyGeo = tube(RINGS, SEG, (c, u, a) => {
    const up = Math.cos(a * Math.PI * 2);                        // 1 = back, -1 = belly
    c.copy(bel).lerp(top, smooth(-.45, .35, up));
    if (S.colors.stripes && up > .1) { const s = Math.sin(u * Math.PI * 2 * S.colors.stripes * 1.6); if (s > .55) c.lerp(str, .7 * smooth(.1, .6, up)); }
    if (S.hair) c.multiplyScalar(.9 + hash(Math.round(u * 400), Math.round(a * 40)) * .2);
  }, seed);
  const bodyMesh = E.shadowed(new THREE.Mesh(bodyGeo, vcol())); body.add(bodyMesh);
  const nodes = S.spine.map(([z, y]) => V(0, y, z)), base = nodes.map(n => n.clone());
  const curve = new THREE.CatmullRomCurve3(nodes, false, 'centripetal');
  const rp = Array.from({ length: RINGS }, () => V()), rx = new Float32Array(RINGS), ry = new Float32Array(RINGS);
  const radius = (i, k) => { const u = ringU(i), a = Math.floor(u), b = Math.min(NS - 1, a + 1), f = u - a; return lerp(S.spine[a][k], S.spine[b][k], f); };

  // head
  const head = S.head(E, A); body.add(head);
  // legs and arms
  const legs = S.legs.map((L, li) => {
    const g = tube(5, kind === 'shrew' ? 5 : 8, (c, u, a) => c.copy(top).lerp(bel, smooth(.2, 1, u) * .35).multiplyScalar(Math.cos(a * Math.PI * 2) > 0 ? 1 : .92), seed + li * 13);
    const m = E.shadowed(new THREE.Mesh(g, vcol())); body.add(m);
    const toes = new THREE.Group(); body.add(toes);
    if (L.foot === 'pad') part(E, new THREE.CylinderGeometry(L.r[3] * 1.05, L.r[3] * 1.15, L.r[3] * .5, 8), A.colors.stripe, [0, L.r[3] * .25, 0], [0, 0, 0], [1, 1, 1], toes);
    else for (const t of [-.35, 0, .35]) part(E, new THREE.ConeGeometry(L.r[3] * .8, L.L[2] * .9, 4), A.colors.stripe, [t * L.r[3] * 3, L.r[3] * .5, L.L[2] * .4], [Math.PI / 2, 0, 0], [1, 1, .6], toes).rotation.y = t * .6;
    if (S.feathers) for (let k = 0; k < 3; k++) part(E, new THREE.ConeGeometry(L.r[0] * .7, L.L[0] * .9, 3), A.colors.top, [0, -k * .1, -.05], [2.6, 0, 0], [1, 1, .4], m);
    return { ...L, g, m, toes, pts: Array.from({ length: 5 }, () => V()), rr: [L.r[0] * .8, L.r[0], L.r[1], L.r[2], L.r[3]] };
  });
  const arms = (S.arms || []).map((Ar, ai) => {
    const pts = Ar.pts.map(p => V(Ar.at[0] + p[0], Ar.at[1] + p[1], Ar.at[2] + p[2]));
    const m = staticTube(E, Ar.pts.map(p => [Ar.at[0] + p[0], Ar.at[1] + p[1], Ar.at[2] + p[2]]), Ar.r, A.colors.top, body, 6);
    if (Ar.wing) for (let k = 0; k < 5; k++) part(E, new THREE.ConeGeometry(.05, .45 - k * .04, 3), k % 2 ? A.colors.stripe : A.colors.top,
      [pts[2].x, pts[2].y - .04 - k * .015, pts[2].z - .08 - k * .08], [2.2, 0, 0], [1, 1, .3], body);
    return { m, ai };
  });
  // feathers along the back and a tail fan (raptors)
  const tufts = [];
  if (S.feathers) for (let k = 0; k < 16; k++) { const u = .05 + k / 16 * .78; const f = part(E, new THREE.ConeGeometry(.07, .5, 3), k % 3 ? A.colors.top : A.colors.stripe, [0, 0, 0], [0, 0, 0], [1, 1, .35], body); tufts.push({ f, u, s: k < 5 ? 1.6 : 1 }); }
  if (S.hair) for (let k = 0; k < 26; k++) { const u = .2 + (k % 13) / 13 * .62, side = k < 13 ? -1 : 1; const f = part(E, new THREE.ConeGeometry(.22, 1.1, 3), A.colors.stripe, [0, 0, 0], [0, 0, 0], [1, 1, .5], body); tufts.push({ f, u, side, hair: true }); }

  // ---------- behaviour over time (precomputed: look direction, roar, drink) ----------
  const roars = (o.roar || []).map(t => +t), drinks = o.drink || [];
  const lookAt = o.look || [];
  const N = tr.N, yawA = new Float32Array(N), pitA = new Float32Array(N);
  { let y = 0, p = 0, vy = 0, vp = 0;
    for (let f = 0; f < N; f++) {
      const t = f / FPS, s = tr.at(t); let tgt = null;
      for (const [tl, pt] of lookAt) if (t >= tl) tgt = pt;
      let wy = noise(t * .17, seed) * .35, wp = noise(t * .13, seed + 4) * .12;
      if (tgt) { const hx = s.x + Math.sin(s.head) * S.spine[NS - 1][0] * sc, hz = s.z + Math.cos(s.head) * S.spine[NS - 1][0] * sc;
        const dx = tgt[0] - hx, dz = tgt[2] - hz, a = Math.atan2(dx, dz) - s.head;
        wy = clamp(Math.atan2(Math.sin(a), Math.cos(a)), -1.25, 1.25);
        wp = clamp(Math.atan2(tgt[1] - S.spine[NS - 1][1] * sc, Math.hypot(dx, dz)), -.6, .5); }
      for (const [a, b] of drinks) wp = lerp(wp, -1.1, smooth(a, a + 2, t) * (1 - smooth(b - 1.5, b, t)));
      for (const r of roars) { const k = smooth(r - .4, r + .2, t) * (1 - smooth(r + S.roarDur - .5, r + S.roarDur + .3, t)); wp = lerp(wp, .28, k); }
      const wn = 2.4, z = .8, dt = 1 / FPS;
      vy += (-(wn * wn) * (y - wy) - 2 * z * wn * vy) * dt; y += vy * dt;
      vp += (-(wn * wn) * (p - wp) - 2 * z * wn * vp) * dt; p += vp * dt;
      yawA[f] = y; pitA[f] = p;
    }
  }
  // footfalls -> events (sound, shake, ripples)
  if (o.steps !== false && S.mass > 0) {
    const cyc = S.stride / S.duty;
    legs.forEach(L => { let prev = null;
      for (let f = 0; f < N; f++) { const t = f / FPS; if (t > STOP) break; const s = tr.at(t), ph = Math.floor(s.dist / sc / cyc + L.phase);
        if (prev != null && ph !== prev && s.speed > .2 * sc) {
          E.EVENTS.push({ t, kind: 'stomp', e: S.mass * (o.loud ?? 1) * Math.min(1, sc), x: s.x, z: s.z });
          if (o.prints) {        // footprints left on the ground (show from the moment the foot lands)
            const lx = L.at[0] * sc, lz = (L.at[2] + S.stride / 2) * sc, c = Math.cos(s.head), si = Math.sin(s.head);
            const px = s.x + lx * c + lz * si, pz = s.z - lx * si + lz * c, pr = new THREE.Group();
            for (const a of [-.45, 0, .45]) { const toe = new THREE.Mesh(new THREE.CircleGeometry(.12 * sc * (S.legs.length > 2 ? 2 : 1), 5), new THREE.MeshLambertMaterial({ color: 0x2c2a26, transparent: true, opacity: .75 }));
              toe.rotation.x = -Math.PI / 2; toe.scale.y = S.legs.length > 2 ? 1 : 3; toe.position.set(Math.sin(a) * .3 * sc, 0, Math.cos(a) * .3 * sc); toe.rotation.z = -a; pr.add(toe); }
            pr.position.set(px, (E.groundAt ? E.groundAt(px, pz) : 0) + .04, pz); pr.rotation.y = s.head; pr.visible = false; E.scene.add(pr);
            const t0 = t; E.updates.push(tt => { pr.visible = tt >= t0; });
          }
        }
        prev = ph; } });
  }
  for (const r of roars) if (r < STOP && S.call) { const s = tr.at(r); E.EVENTS.push({ t: r, kind: 'roar', call: S.call, e: (o.loud ?? 1) * Math.min(1.2, sc * (S.mass || .3) + .3), x: s.x, y: S.spine[NS - 1][1] * sc, z: s.z, dur: S.roarDur }); }

  // ---------- pose ----------
  const q = new THREE.Quaternion(), qp = new THREE.Quaternion(), m4 = new THREE.Matrix4(), tmp = V(), tmp2 = V(), X = V(1, 0, 0);
  const hipY = S.spine[S.hip][1];
  function pose(t, ts) {
    const s = tr.at(t), f = Math.min(N - 1, Math.round(t * FPS));
    const ground = E.groundAt ? E.groundAt(s.x, s.z) : 0;
    root.position.set(s.x, (o.y ?? ground) + (o.lift ?? 0), s.z); root.rotation.y = s.head;
    const walk = smooth(.05, .4, s.speed / sc), cyc = S.stride / S.duty, ph = s.dist / sc / cyc;
    let roarK = 0; for (const r of roars) roarK = Math.max(roarK, smooth(r - .1, r + .35, t) * (1 - smooth(r + S.roarDur - .4, r + S.roarDur, t)));
    const yaw = yawA[f], pit = pitA[f] + (S.neckRest ?? 0), breath = Math.sin(ts * 2 * Math.PI / (3.2 + hash(seed, 3))) * .5 + .5;
    const bob = Math.abs(Math.sin(ph * Math.PI * (S.legs.length > 2 ? 2 : 2))) * S.bob * walk * hipY - S.bob * walk * hipY * .5;
    // spine
    for (let i = 0; i < NS; i++) {
      const b = base[i], n = nodes[i]; n.copy(b); n.y += bob;
      if (i < S.hip) {          // tail: sways side to side, a little up and down
        const u = (S.hip - i) / S.hip, sw = Math.sin(ts * (1.1 + walk * 1.6) + seed - u * 1.6) * S.tailSway * u * u * (b.z - base[S.hip].z) * -.18;
        n.x += sw * (1 + roarK * .6); n.y += Math.sin(ts * .9 + u * 2 + seed) * .03 * u * hipY;
        if (S.tailHang) n.x += Math.sin(ts * 2.2 + seed) * .08;
      }
      if (i >= S.neck) {        // neck bends towards the gaze, more towards the head
        const u = (i - S.neck + 1) / (NS - S.neck), k = u * (2 - u) * S.neckTurn;
        const o0 = base[S.neck - 1]; tmp.subVectors(b, o0);
        q.setFromAxisAngle(UP, yaw * k); qp.setFromAxisAngle(X, -pit * k * .8); tmp.applyQuaternion(qp).applyQuaternion(q);
        n.copy(o0).add(tmp); n.y += bob;
      }
    }
    curve.updateArcLengths?.();
    for (let i = 0; i < RINGS; i++) {
      const u = ringU(i) / (NS - 1); curve.getPoint(u, rp[i]);
      const chest = Math.exp(-(((ringU(i) - (S.hip + S.neck) / 2) / 1.6) ** 2));
      rx[i] = radius(i, 2) * (1 + breath * .025 * chest); ry[i] = radius(i, 3) * (1 + breath * .04 * chest);
    }
    bodyGeo.shape(rp, rx, ry);
    // head: at the neck end, facing along the last neck segment, with its own extra pitch
    const nE = nodes[NS - 1], nP = nodes[NS - 2]; tmp.subVectors(nE, nP).normalize();
    head.position.copy(nE); m4.lookAt(tmp, V(), UP); head.quaternion.setFromRotationMatrix(m4);
    qp.setFromAxisAngle(X, -(pit * (1 - S.neckTurn * .8) + roarK * .25 + Math.sin(ts * 23) * .02 * roarK)); head.quaternion.multiply(qp);
    qp.setFromAxisAngle(UP, yaw * (1 - S.neckTurn * .7)); head.quaternion.premultiply(qp);
    A.jaw(clamp(roarK * (1 + Math.sin(ts * 9) * .08) + (kind === 'shrew' ? 0 : Math.max(0, Math.sin(ts * .7 + seed)) * .04)));
    A.trunk?.(ts, roarK);
    // legs: stance foot slides back under the body (planted while it walks), swing foot lifts and comes forward
    for (const L of legs) {
      const u = ((ph + L.phase) % 1 + 1) % 1, stance = u < S.duty, half = S.stride / 2;
      let fz = stance ? lerp(half, -half, u / S.duty) : lerp(-half, half, smooth(0, 1, (u - S.duty) / (1 - S.duty)));
      let fy = stance ? 0 : Math.sin((u - S.duty) / (1 - S.duty) * Math.PI) * S.stride * .22;
      fz *= walk; fy *= walk;
      const hip = tmp.set(L.at[0], L.at[1] + bob, L.at[2]), toe = tmp2.set(L.at[0] * 1.05, fy, L.at[2] + fz + (L.bend > 0 ? .06 : 0) * L.L[0]);
      const ank = V(toe.x, toe.y + Math.cos(L.digi) * L.L[2], toe.z - Math.sin(L.digi) * L.L[2] * L.bend);
      const dy = ank.y - hip.y, dz = ank.z - hip.z, d = Math.min(Math.hypot(dy, dz), L.L[0] + L.L[1] - 1e-3);
      const a1 = Math.acos(clamp((L.L[0] ** 2 + d * d - L.L[1] ** 2) / (2 * L.L[0] * d), -1, 1)), th = Math.atan2(dz, dy);
      const kn = V(hip.x, hip.y + Math.cos(th - a1 * L.bend) * L.L[0], hip.z + Math.sin(th - a1 * L.bend) * L.L[0]);
      // if the leg cannot reach (body high), the ankle follows the shin
      const sh = V().subVectors(ank, kn); if (sh.length() > L.L[1]) ank.copy(kn).addScaledVector(sh.normalize(), L.L[1]);
      L.pts[0].set(hip.x, hip.y + L.r[0] * .45, hip.z + L.r[0] * .1); L.pts[1].copy(hip); L.pts[2].copy(kn); L.pts[3].copy(ank); L.pts[4].set(toe.x, toe.y + L.r[3] * .6, toe.z);
      L.g.shape(L.pts, L.rr, L.rr, FWD);
      L.toes.position.set(toe.x, toe.y, toe.z);
    }
    for (const T of tufts) {    // feathers / hair follow the back
      curve.getPoint(T.u, tmp); curve.getTangent(T.u, tmp2); const r = radius(Math.round(T.u * (RINGS - 1)), 3);
      if (T.hair) { const rxx = radius(Math.round(T.u * (RINGS - 1)), 2); T.f.position.set(tmp.x + T.side * rxx * .85, tmp.y - r * .2, tmp.z); T.f.rotation.set(0, 0, T.side * .25 + Math.PI); }
      else { T.f.position.set(tmp.x, tmp.y + r * .9, tmp.z); T.f.rotation.set(-Math.PI / 2 - .35 + Math.atan2(tmp2.y, tmp2.z), 0, 0); T.f.scale.set(T.s, T.s, .35); }
    }
    void arms;
  }
  E.updates.push((t, F, tv) => pose(Math.min(t, STOP), Math.min(tv, STOP + 30)));
  pose(0, 0);
  const obj = { kind, root, track: tr, scale: sc, headPos: t => { const s = tr.at(t); return [s.x + Math.sin(s.head) * S.spine[NS - 1][0] * sc, S.spine[NS - 1][1] * sc, s.z + Math.cos(s.head) * S.spine[NS - 1][0] * sc]; } };
  (E.bigAnimals ??= []).push(obj);
  return obj;
}

// ---------- pterosaur (Quetzalcoatlus: wingspan about 10 m) ----------
function pterosaur(E, TL, o) {
  const sc = o.scale ?? 1, seed = o.seed ?? 1, STOP = TL.beats.stop, col = 0x5a4e42, mem = 0x8a6e58;
  const root = new THREE.Group(); root.scale.setScalar(sc); E.scene.add(root);
  const bodyG = tube(10, 7, (c, u, a) => c.set(Math.cos(a * Math.PI * 2) > 0 ? col : 0xb9a88c), seed);
  bodyG.shape([V(0, 0, -.9), V(0, .02, -.6), V(0, .05, -.2), V(0, .06, .2), V(0, .08, .5), V(0, .3, .9), V(0, .55, 1.3), V(0, .7, 1.7), V(0, .78, 2.0), V(0, .8, 2.15)],
    [.03, .15, .24, .26, .22, .12, .1, .09, .085, .08], [.03, .16, .27, .28, .24, .13, .11, .1, .09, .085]);
  root.add(E.shadowed(new THREE.Mesh(bodyG, vcol())));
  const head = new THREE.Group(); head.position.set(0, .8, 2.15); root.add(head);
  part(E, wedge(.18, .3, .02, .03, 2.3, -.15), 0x3e352d, [0, 0, 0], [.1, 0, 0], [1, 1, 1], head);           // long beak
  part(E, wedge(.06, .9, .02, .1, .9), 0xa0482f, [0, .45, -.35], [-.5, 0, 0], [1, 1, 1], head);              // crest
  eyes(E, head, .09, .08, .12, .03);
  const wings = [-1, 1].map(s => {
    const inner = new THREE.Group(); inner.position.set(s * .2, .06, .35); root.add(inner);
    const outer = new THREE.Group(); outer.position.set(s * 1.9, 0, .25); inner.add(outer);
    const tri = (pts, c) => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pts.flat(), 3)); g.computeVertexNormals();
      const m = new THREE.Mesh(g, E.lam(c, { side: THREE.DoubleSide })); m.castShadow = true; return m; };
    inner.add(tri([[0, 0, .1], [s * 1.9, 0, .3], [s * 1.9, 0, -.25], [0, 0, -1.0], [0, 0, .1], [s * 1.9, 0, -.25]], mem));
    outer.add(tri([[0, 0, .05], [s * 3.1, 0, -.35], [0, 0, -.5]], mem));
    inner.add(staticTube(E, [[0, 0, .1], [s * 1.0, .05, .25], [s * 1.9, 0, .3]], [.09, .07, .06], col));
    outer.add(staticTube(E, [[0, 0, .05], [s * 1.6, 0, -.12], [s * 3.1, 0, -.35]], [.06, .04, .015], col));
    return { s, inner, outer };
  });
  const F = o.fly || { c: [0, 40, -80], r: 60, period: 26, dir: 1 };
  const posAt = t => {
    if (o.path) { const p = o.path; const fx = monotone(p.map(q => [q[0], q[1]])), fy = monotone(p.map(q => [q[0], q[2]])), fz = monotone(p.map(q => [q[0], q[3]])); return [fx(t), fy(t), fz(t)]; }
    const a = (t / F.period + hash(seed, 2)) * Math.PI * 2 * (F.dir ?? 1); return [F.c[0] + Math.sin(a) * F.r, F.c[1] + Math.sin(t * .4 + seed) * 2, F.c[2] + Math.cos(a) * F.r * (F.squash ?? 1)];
  };
  E.updates.push((t, Fz, tv) => {
    const ts = Math.min(tv, STOP + 30), p = posAt(ts), q2 = posAt(ts + .1), dx = q2[0] - p[0], dy = q2[1] - p[1], dz = q2[2] - p[2];
    root.position.set(...p); root.rotation.order = 'YXZ'; root.rotation.y = Math.atan2(dx, dz); root.rotation.x = -Math.atan2(dy, Math.hypot(dx, dz)) * .6;
    const turn = Math.atan2(Math.sin(Math.atan2(posAt(ts + .6)[0] - q2[0], posAt(ts + .6)[2] - q2[2]) - root.rotation.y), 1);
    root.rotation.z = -turn * 2.5;
    const flapOn = smooth(.6, 1, Math.sin(ts * .35 + seed * 2)), fl = Math.sin(ts * 2 * Math.PI * .7 + seed) * flapOn;
    for (const w of wings) { w.inner.rotation.z = w.s * (fl * .45 + .06); w.outer.rotation.z = w.s * (fl * .3 - .04); }
    head.rotation.y = Math.sin(ts * .3 + seed) * .25;
  });
  const obj = { kind: 'pterosaur', root, pos: posAt };
  (E.bigAnimals ??= []).push(obj);
  return obj;
}
SPECIES.pterosaur = {};

// ---------- herds and the scenario list ----------
export const isBig = kind => kind in SPECIES;
// one TL.animals entry; herd: { n, spread, depth, lag, vary, turn, seed } (or the small-animal names n / spread / lag)
export function bigAnimals(E, TL, a) {
  const H = a.herd || (a.n > 1 ? { n: a.n, spread: a.spread ?? 4, lag: a.lag ?? 1 } : null);
  if (!H) return animal(E, TL, a.kind, a);
  const R = rng(H.seed ?? 5);
  for (let i = 0; i < H.n; i++) {
    const dx = i ? (R() - .5) * 2 * H.spread : 0, dz = i ? (R() - .5) * 2 * H.spread * (H.depth ?? 1) : 0, dt = i ? R() * (H.lag ?? 1.5) : 0;
    const sc = (a.scale ?? 1) * (1 - (H.vary ?? .15) * (i ? R() : 0));
    animal(E, TL, a.kind, { ...a, herd: null, n: 1, seed: (a.seed ?? 1) + i * 17, scale: sc, steps: i === 0 && a.steps !== false, rot: (a.rot ?? 0) + (i ? (R() - .5) * (H.turn ?? .5) : 0),
      path: a.path ? a.path.map(([t, x, z]) => [t + dt, x + dx, z + dz]) : null, at: a.at ? [a.at[0] + dx, a.at[1] + dz] : null,
      roar: i === 0 ? a.roar : [], look: a.look?.map(([t, p]) => [t + R() * .8, p]),
      drink: (a.drink || []).map(([s, e]) => [s + R() * 3, e + R() * 2]), fly: a.fly && { ...a.fly, r: a.fly.r * (.8 + R() * .4), c: [a.fly.c[0] + dx, a.fly.c[1] + R() * 10, a.fly.c[2] + dz] } });
  }
}

// ---------- a puddle that ripples at every heavy footstep nearby ----------
export function puddle(E, x, z, r = 1.5, y) {
  const gy = y ?? (E.groundAt ? E.groundAt(x, z) : 0) + .03;
  const water = new THREE.Mesh(new THREE.CircleGeometry(r, 18), E.lam(0x3f4a4e, { transparent: true, opacity: .85 }));
  water.rotation.x = -Math.PI / 2; water.position.set(x, gy, z); water.scale.y = .7; E.scene.add(water);
  const rings = Array.from({ length: 4 }, () => { const m = new THREE.Mesh(new THREE.RingGeometry(.92, 1, 28), new THREE.MeshBasicMaterial({ color: 0xd8e2e6, transparent: true, opacity: 0 }));
    m.rotation.x = -Math.PI / 2; m.position.set(x, gy + .01, z); E.scene.add(m); return m; });
  E.updates.push(t => {
    const steps = E.EVENTS.filter(e => e.kind === 'stomp' && e.t <= t && t - e.t < 1.6);
    rings.forEach((m, k) => { let a = 0, s = .01;
      for (const e of steps) { const age = t - e.t - k * .18; if (age < 0) continue; const d = Math.hypot(e.x - x, e.z - z);
        const amp = e.e / (1 + d / 25); if (amp < .03) continue; a = Math.max(a, (1 - age / 1.4) * Math.min(1, amp)); s = r * (.15 + age * .7); }
      m.material.opacity = a * .6; m.scale.set(Math.min(s, r), Math.min(s, r) * .7, 1); });
  });
  return water;
}
