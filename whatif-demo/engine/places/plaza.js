// CITY PLAZA (style: calm toy city, muted colours): a big paved square with a fountain and many people, a road
// with a bus and zebra crossings, a market hall ("CENTRAL MARKET") with columns, a clock tower, brown and tan
// office blocks with blue window grids all around, soft white clouds. Seen from a balcony (railing in front).
//   can cover:  square, roofs (eruption ash cover, cold frost)
// Beats: lookUp (people stop and stare at the sky), shelter (they walk off), carsStop
import * as THREE from 'three';
import { rng, colorKeys } from '../util.js';
import { person, car, lamp, roundTree } from '../props.js';
import { crowd } from '../crowd.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats;
  E.groundAt = () => 0; E.waterBase = -50; E.dustColor = [.72, .68, .58];
  E.ashGround = []; E.ashRoofs ||= [];
  const flat = (w, d, x, z, col, y = .02) => { const m = lam(col, { flatShading: false }); const g = new THREE.Mesh(new THREE.PlaneGeometry(w, d), m); g.rotation.x = -Math.PI / 2; g.position.set(x, y, z); g.receiveShadow = true; scene.add(g); E.ashGround.push(m); return g; };
  const box = (w, h, d, x, y, z, m) => { const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m)); b.position.set(x, y, z); scene.add(b); return b; };

  // facades: plain wall colour with a grid of light-blue windows (the look of the reference), one bay = 3.2 m, one storey = 3.4 m
  const texCache = {};
  const facade = (wall, glass = '#5f8fb8') => {
    const key = wall + glass; if (texCache[key]) return texCache[key];
    const cv = document.createElement('canvas'); cv.width = cv.height = 64; const x = cv.getContext('2d');
    const c = new THREE.Color(wall), hex = k => '#' + c.clone().multiplyScalar(k).getHexString();
    x.fillStyle = hex(1); x.fillRect(0, 0, 64, 64);
    x.fillStyle = hex(.86); x.fillRect(0, 56, 64, 8);                       // floor band
    x.fillStyle = glass; x.fillRect(14, 12, 36, 36);
    x.fillStyle = '#8fb6d6'; x.fillRect(14, 12, 36, 7);                     // sky reflected in the top of the glass
    x.fillStyle = hex(.92); x.fillRect(31, 12, 2, 36);
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4;
    const side = lam(0xffffff, { map: t }), top = lam(c.clone().multiplyScalar(.7)); E.frost.push(side, top); E.ashRoofs.push(top);
    return (texCache[key] = [side, side, top, top, side, side]);
  };
  const building = (x, z, w, d, h, wall, glass) => { const b = shadowed(new THREE.Mesh(E.facadeBox(w, h, d, 3.2, 3.4), facade(wall, glass))); b.position.set(x, h / 2, z); scene.add(b);
    const rim = box(w + .6, .6, d + .6, x, h + .3, z, lam(new THREE.Color(wall).multiplyScalar(.75))); E.ashRoofs.push(rim.material);
    if (w * d > 300) box(4, 2, 3, x + w * .2, h + 1.6, z, lam(0x9a9890));      // a roof box (lift house)
    return b; };

  // ground: the square (light sand paving), the road along x, the upper terrace in front of the market
  flat(3000, 3000, 0, 0, 0xb9b09a, 0);
  flat(150, 130, 0, 20, 0xd3c9b3, .02);                                       // the square
  { const m = lam(0xc9bda2, { flatShading: false });                          // paving joints: faint lines
    for (let x = -70; x <= 70; x += 6) { const l = new THREE.Mesh(new THREE.PlaneGeometry(.12, 130), m); l.rotation.x = -Math.PI / 2; l.position.set(x, .03, 20); scene.add(l); } }
  flat(400, 14, 0, -12, 0x575c62, .04);                                       // road
  flat(400, .5, 0, -12, 0xd8d2bc, .05);                                       // centre line
  for (const zx of [-20, 22]) for (let k = 0; k < 7; k++) flat(1, 9, zx + k * 2, -12, 0xece7d8, .06).rotation.z = 0;   // zebra crossings
  for (const zx of [-20, 22]) for (let k = 0; k < 7; k++) { const s = flat(6, .9, zx, -16.5 + k * 1.5, 0xece7d8, .065); }
  flat(400, 2, 0, -4.2, 0xbfb6a0, .08); flat(400, 2, 0, -19.8, 0xbfb6a0, .08);   // kerbs
  flat(120, 40, 0, -40, 0xcfc3a6, .03);                                       // terrace in front of the market

  // market hall: long low hall with a portico of columns and the name on the frieze
  { const hall = box(84, 9, 22, 0, 4.5, -68, lam(0x8ea2b6)); E.ashRoofs.push(hall.material);
    box(88, 1.6, 26, 0, 9.8, -66, lam(0x7d8792));                            // flat roof slab
    box(88, 2.4, 1.2, 0, 8.2, -55.2, lam(0x9aa6b2));                         // frieze
    for (let x = -42; x <= 42; x += 7) box(1.1, 7, 1.1, x, 3.5, -55.2, lam(0xa8b2bc));   // columns
    const cv = document.createElement('canvas'); cv.width = 512; cv.height = 32; const c = cv.getContext('2d');
    c.fillStyle = '#9aa6b2'; c.fillRect(0, 0, 512, 32); c.fillStyle = '#d9dee4'; c.font = 'bold 22px Georgia, serif'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.letterSpacing = '6px'; c.fillText('CENTRAL MARKET', 256, 17);
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(40, 2.4), new THREE.MeshLambertMaterial({ map: t })); sign.position.set(0, 8.2, -54.55); scene.add(sign);
    // market stalls with awnings at both ends
    for (const sx of [-1, 1]) for (let k = 0; k < 3; k++) { const x = sx * (34 + k * 4.5);
      box(3.6, 1, 2, x, .5, -47, lam(0x7a5a3a)); box(4, .25, 2.8, x, 2.6, -47, lam([0xc9b27a, 0x9a6a4a, 0xb8a070][k]));
      for (const px of [-1.7, 1.7]) box(.12, 2.6, .12, x + px, 1.3, -46, lam(0x5a4a3a)); }
  }
  // clock tower (left behind the hall): shaft, clock faces, a pyramid roof
  { const tx = -26, tz = -88, h = 46;
    const shaft = shadowed(new THREE.Mesh(E.facadeBox(13, h, 13, 3.2, 3.4), facade(0xb08a5a))); shaft.position.set(tx, h / 2, tz); scene.add(shaft);
    box(14.5, 1.2, 14.5, tx, h + .6, tz, lam(0x6d6458));
    const roof = shadowed(new THREE.Mesh(new THREE.ConeGeometry(10.5, 9, 4), lam(0x3c4650))); roof.rotation.y = Math.PI / 4; roof.position.set(tx, h + 5.7, tz); scene.add(roof); E.ashRoofs.push(roof.material);
    const cv = document.createElement('canvas'); cv.width = cv.height = 128; const c = cv.getContext('2d');
    c.fillStyle = '#e9e4d6'; c.beginPath(); c.arc(64, 64, 60, 0, 7); c.fill(); c.lineWidth = 6; c.strokeStyle = '#3a3a3a'; c.stroke();
    c.lineWidth = 3; for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; c.beginPath(); c.moveTo(64 + Math.sin(a) * 50, 64 - Math.cos(a) * 50); c.lineTo(64 + Math.sin(a) * 56, 64 - Math.cos(a) * 56); c.stroke(); }
    c.lineWidth = 5; c.beginPath(); c.moveTo(64, 64); c.lineTo(64 + 26, 64 + 8); c.stroke(); c.lineWidth = 3; c.beginPath(); c.moveTo(64, 64); c.lineTo(64 - 6, 64 - 44); c.stroke();
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    const face = new THREE.Mesh(new THREE.CircleGeometry(4.2, 32), new THREE.MeshLambertMaterial({ map: t })); face.position.set(tx, h - 6, tz + 6.55); scene.add(face);
    const f2 = face.clone(); f2.rotation.y = Math.PI / 2; f2.position.set(tx + 6.55, h - 6, tz); scene.add(f2);
  }
  // office blocks around the square and behind the hall (tan, brown, grey-blue; blue window grids)
  const walls = [0x9c8268, 0x7e6652, 0xb3a184, 0x7f8b96, 0x8f7660, 0xa8957c];
  const R = rng(17), pick = () => walls[Math.floor(R() * walls.length)];
  // left and right of the square (the camera looks between them)
  [[-58, -34, 26, 30, 30], [-62, 8, 28, 26, 22], [-60, 44, 26, 30, 26], [58, -34, 26, 30, 33], [62, 8, 28, 26, 24], [60, 44, 26, 30, 28]].forEach(([x, z, w, d, h]) => building(x, z, w, d, h, pick()));
  // the skyline behind the hall
  for (let i = 0; i < 9; i++) { const x = -70 + i * 17 + (R() - .5) * 4; if (Math.abs(x + 26) < 9) continue; building(x, -100 - R() * 25, 14 + R() * 6, 16 + R() * 6, 22 + R() * 26, pick()); }
  for (let i = 0; i < 14; i++) building(-160 + i * 24, -170 - R() * 40, 18, 18, 30 + R() * 30, pick(), '#7aa0c2');

  // fountain on the square: a dark basin, a pedestal, arcs of water
  { const fx = -14, fz = 18;
    const rim = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(7, 7.3, .9, 40), lam(0x3c4a5a))); rim.position.set(fx, .45, fz); scene.add(rim);
    const water = new THREE.Mesh(new THREE.CircleGeometry(6.5, 40), new THREE.MeshLambertMaterial({ color: 0x5f86a8 })); water.rotation.x = -Math.PI / 2; water.position.set(fx, .8, fz); scene.add(water);
    box(1.4, 2.4, 1.4, fx, 1.2, fz, lam(0x6d7a86)); const bowl = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(1.8, .6, .5, 20), lam(0x6d7a86))); bowl.position.set(fx, 2.6, fz); scene.add(bowl);
    const wm = new THREE.MeshBasicMaterial({ color: 0xcfe2f0, transparent: true, opacity: .55 });
    for (let k = 0; k < 10; k++) { const a = k / 10 * Math.PI * 2, pts = [];
      for (let i = 0; i <= 16; i++) { const u = i / 16; pts.push(new THREE.Vector3(fx + Math.cos(a) * 5.6 * u, 2.8 + 3.2 * u - 5 * u * u, fz + Math.sin(a) * 5.6 * u)); }
      scene.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 16, .06, 4), wm)); }
  }
  // lamps and a few trees along the road
  for (let x = -60; x <= 60; x += 20) lamp(E, x, -3.4, 1, { y: 0 });
  // traffic: a long blue bus and some cars on the road
  { const bus = new THREE.Group(); bus.position.set(-6, 0, -9.6); scene.add(bus);
    const body = shadowed(new THREE.Mesh(new THREE.BoxGeometry(24, 3, 2.6), lam(0x3f7fa0))); body.position.y = 1.9; bus.add(body);
    const stripe = new THREE.Mesh(new THREE.BoxGeometry(24.05, .35, 2.65), lam(0xd9b45a)); stripe.position.y = .6; bus.add(stripe);
    const win = new THREE.Mesh(new THREE.BoxGeometry(23, 1, 2.62), lam(0x2a3c48)); win.position.y = 2.4; bus.add(win);
    const joint = new THREE.Mesh(new THREE.BoxGeometry(.5, 2.9, 2.5), lam(0x2a2a2a)); joint.position.y = 1.9; bus.add(joint);
    for (const wx of [-9, -3, 3, 9]) for (const wz of [-1.3, 1.3]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(.5, .5, .3, 12), lam(0x1d1d1d)); w.rotation.x = Math.PI / 2; w.position.set(wx, .5, wz); bus.add(w); }
    const stop = B.carsStop ?? 1e9;
    E.updates.push(t => { const tt = Math.min(t, stop); bus.position.x = -6 + tt * 2.2 - Math.max(0, Math.min(t, stop) - stop); });
  }
  [[2.8, 1, 0], [-2.8, -1, 1], [2.8, 1, 2], [-2.8, -1, 3]].forEach(([dz, dir, k]) => car(E, 960 + k, { x0: -140 + k * 70, z0: -12 + dz, dir, v: 9, axis: 'x', a: -200, b: 200, brakeT: (B.carsStop ?? 1e9) + k * .5, F, strength: {} }));

  // many small people on the square and the terrace (walking, standing)
  crowd(E, TL, { n: 26, axis: 'x', lane: [2, 60], range: [-60, 60], door: () => 70, seed: 41 });
  crowd(E, TL, { n: 14, axis: 'x', lane: [-50, -24], range: [-45, 45], door: () => -56, seed: 43 });
  { const R2 = rng(5);
    for (let i = 0; i < 18; i++) { const x = -50 + R2() * 100, z = 4 + R2() * 50, rot = R2() * 6.28, look = (B.lookUp ?? 1e9) + R2() * 1.4;
      person(E, 7000 + i, { y: 0, path: t => ({ x, z, rot, moving: 0, speed: 0, headUp: Math.min(1, Math.max(0, (t - look) / 1.2)) * .75 }) }); } }

  // balcony railing in front of the camera (on a building at z = +78)
  { const m = lam(0x2f4a58), rx = 0, rz = 78, ry = 15.5;
    box(60, .35, .35, rx, ry, rz, m); box(60, .2, .2, rx, ry - .55, rz, m);
    for (let x = -24; x <= 24; x += 4.6) box(.32, 1.6, .32, rx + x, ry - .8, rz, m);
  }

  // soft white clouds (sprites: use post { ao: false } with this place, the AO pass turns them black): big flat sprites with a blurred round texture, high over the city
  { const cv = document.createElement('canvas'); cv.width = cv.height = 128; const c = cv.getContext('2d');
    const g = c.createRadialGradient(64, 64, 8, 64, 64, 62); g.addColorStop(0, 'rgba(255,255,255,.95)'); g.addColorStop(.55, 'rgba(250,250,252,.6)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    c.fillStyle = g; c.fillRect(0, 0, 128, 128);
    const t = new THREE.CanvasTexture(cv); const R3 = rng(23);
    for (let k = 0; k < 9; k++) {   // one cloud bank = several puffs side by side
      const cx = -1500 + k * 380 + (R3() - .5) * 200, cz = -1700 - R3() * 600, cy = 520 + R3() * 380;
      for (let p = 0; p < 6; p++) { const s = 150 + R3() * 170, m = new THREE.SpriteMaterial({ map: t, color: new THREE.Color().setHSL(.6, .1, .9 + R3() * .08), transparent: true, depthWrite: false, fog: false, opacity: .7 });
        const sp = new THREE.Sprite(m); sp.scale.set(s * 1.8, s * .7, 1); sp.position.set(cx + (R3() - .5) * 260, cy + (R3() - .5) * 50, cz + (R3() - .5) * 100); scene.add(sp); } }
  }

  E.brandSpot = { pos: [0, 4, -54.4], ry: 0, w: 6, h: 2.4, posts: 0, shot: 'square' };
  const sky = colorKeys(THREE, [[0, 0x4f88bf, 0xd8d6cc]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [-160, 200, 140]));
  return {
    ambience: 'stad',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 160, fogFar: 1600, hemi: 1.55, hemiColor: new THREE.Color(0xe9ecee), groundColor: new THREE.Color(0x8a8270),
      sun: 2.1, sunColor: new THREE.Color(0xfff0d8), sunDisc: new THREE.Color(0x998877) }),
    shots: {
      balcony: { pos: [0, 16.4, 79.2], look: [-2, 9, -40], drift: [.3, 0, 0], fov: 52 },               // from the balcony over the square to the hall and the tower (railing in front)
      square: { pos: [18, 1.7, 40], look: [-10, 4, -30], drift: [-.4, 0, 0], fov: 58 },              // on the square between the people
      fountain: { pos: [-2, 3, 32], look: [-14, 1.5, 18], drift: [.3, 0, 0], fov: 50 },
      road: { pos: [34, 1.8, -2], look: [-20, 2, -12], drift: [0, 0, 0], fov: 54 },                   // at the kerb, the bus passes
      tower: { pos: [-10, 1.7, -36], look: [-26, 40, -88], drift: [0, 0, 0], fov: 60 },
      'pov-up': { pos: [6, 1.6, 20], look: [10, 60, -40], drift: [0, 0, 0], fov: 70 },
      high: { pos: [40, 70, 120], look: [-6, 0, -30], drift: [-1, 0, 0], fov: 50 },
    },
  };
}
