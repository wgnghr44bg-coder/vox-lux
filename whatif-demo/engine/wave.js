// baksteen Golf + grootte (okt 2026): size comparisons with water. Made for "How tall was the biggest wave ever recorded?"
// on the boulevard (place 'boulevard', force 'calm'), but it only needs E.groundAt and a sea at y 0 along z < 0.
//   TL.wave = {
//     h: [[t, m], …]            height of a breaking wave standing just off the beach (cross-section scales with it)
//     front: z, x: [x0, x1]     where its lip is and how long it is along the shore
//     label: [t0, t1]           a height tag on its crest while it grows ("10 m")
//     runup: { h: [[t, m], …], at: [mx, mz], r: [rx, rz], peak, face: [fx, fz, c], label, labelAt }   a forested mountain beside the town; the water
//                               surges up its sea-facing slope to h (run-up) and strips the trees on the way
//     sizes: [{ kind: 'house'|'tower', x, z, w, d, h, label: [t0, t1] }]   things to compare with, with a height tag
//     tags: [{ text, pos: [x, y, z], at: [t0, t1] }]                       extra height tags
//     fogFar                    clear air for the big wide view (default 5200)
//   }
import * as THREE from 'three';
import { rng, hash, smooth, clamp, monotone } from './util.js';
import { house, tower } from './blocks.js';

function tag(E, text, color = '#ffffff') {
  const cv = document.createElement('canvas'); cv.width = 512; cv.height = 128; const x = cv.getContext('2d');
  x.font = '600 64px "Helvetica Neue", Arial, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.lineWidth = 10; x.strokeStyle = 'rgba(20,24,28,.75)'; x.strokeText(text, 256, 64); x.fillStyle = color; x.fillText(text, 256, 64);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false, sizeAttenuation: false, fog: false }));
  s.scale.set(.2, .05, 1); s.renderOrder = 10; E.scene.add(s); return s;
}
const show = (s, [a, b], t) => { const o = smooth(a, a + .8, t) * (1 - smooth(b - .8, b, t)); s.material.opacity = o; s.visible = o > .01; };

export function buildWave(E, TL, F, P) {
  const W = TL.wave, { scene, lam } = E;
  E.renderer.localClippingEnabled = true;
  const look = P.look; P.look = t => { const L = look(t); L.fogFar = W.fogFar ?? 5200; L.fogNear = 400; return L; };
  E.nearFn = p => p[1] > 120 ? 2 : .3;
  E.skyFollow = true;          // far out at sea: the sky sphere (r 4000) stays around the camera (main.js)

  // ---- the breaking wave: profile in (z landward, y up) for height 1, extruded along x ----
  if (W.h) {
    const hAt = monotone(W.h), [x0, x1] = W.x || [-420, 260], L = x1 - x0, zf = W.front ?? -8;
    const prof = [[-3.4, 0], [-2.2, .18], [-1.3, .5], [-.7, .8], [-.3, .97], [0, 1], [.25, .96], [.42, .84], [.4, .74], [.28, .7], [.2, .55], [.2, .3], [.3, 0]];
    const sh = new THREE.Shape(); prof.forEach(([u, v], i) => i ? sh.lineTo(u, v) : sh.moveTo(u, v)); sh.closePath();
    const g = new THREE.ExtrudeGeometry(sh, { depth: L, steps: 90, bevelEnabled: false, curveSegments: 1 });
    g.translate(0, 0, -L / 2); g.rotateY(-Math.PI / 2);        // shape x -> world z (landward), extrusion -> world x
    const pos = g.attributes.position, base = pos.array.slice(), col = new Float32Array(pos.count * 3);
    const deep = new THREE.Color(0x24606c), mid = new THREE.Color(0x3d8d96), foam = new THREE.Color(0xe9f1ef), c = new THREE.Color();
    for (let i = 0; i < pos.count; i++) { const y = pos.getY(i), z = pos.getZ(i);
      c.copy(deep).lerp(mid, smooth(.2, .75, y)); if (y > .86 || (z > .15 && y > .6)) c.lerp(foam, .8);
      c.toArray(col, i * 3); }
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const wave = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true }));
    wave.castShadow = true; wave.position.x = (x0 + x1) / 2; scene.add(wave);
    // tapered ends: the wave fades into the sea at both ends along x
    E.updates.push((t, _F, tv) => {
      const h = Math.max(.05, hAt(t)); wave.scale.set(1, h, h); wave.position.z = zf - .42 * h; wave.position.y = -.15 * Math.min(1, h);
      for (let i = 0; i < pos.count; i++) {
        const bx = base[i * 3], by = base[i * 3 + 1], bz = base[i * 3 + 2], u = (bx + L / 2) / L;
        const end = .03 + .97 * smooth(0, .12, u) * smooth(1, .88, u), ripple = Math.sin(bx * .045 + tv * .9) * .04 + Math.sin(bx * .11 - tv * 1.3) * .02;
        pos.setXYZ(i, bx, by * (end * (1 + ripple)), bz + Math.max(0, by - .5) * ripple * 1.5);
      }
      pos.needsUpdate = true; g.computeVertexNormals();
    });
    E.emitters.push((tv, add) => {       // spray blowing off the crest
      const h = hAt(tv); if (h < .5) return;
      for (let k = 0; k < 260; k++) {
        const u = (tv * .45 + hash(k, 1)) % 1, x = x0 + 40 + hash(k, 2) * (L - 80), y = h * (.92 + u * .2) + u * 3;
        add(x, y, zf - .1 * h - u * h * .25, h * (.06 + u * .12) + 1, Math.sin(u * Math.PI) * .35, .95, .97, .97, hash(k, 3) * 6);
      }
    });
    if (W.label) { const s = tag(E, ''), cv = s.material.map.image, cx = cv.getContext('2d'); let last = '';
      E.updates.push((t) => { const h = hAt(t), txt = `${h < 9.5 ? h.toFixed(0) : Math.round(h)} m`;
        if (txt !== last) { cx.clearRect(0, 0, 512, 128); cx.font = '600 64px "Helvetica Neue", Arial, sans-serif'; cx.textAlign = 'center'; cx.textBaseline = 'middle';
          cx.lineWidth = 10; cx.strokeStyle = 'rgba(20,24,28,.75)'; cx.strokeText(txt, 256, 64); cx.fillStyle = '#fff'; cx.fillText(txt, 256, 64); s.material.map.needsUpdate = true; last = txt; }
        s.position.set(W.labelX ?? 0, h * 1.12 + 1.5, zf - .3 * h); show(s, W.label, t); });
    }
  }

  // far land behind the town (seen from far out at sea): no edge of the world
  if (W.farLand !== false) { const y = E.groundAt ? E.groundAt(0, 690) : 0, fl = new THREE.Mesh(new THREE.PlaneGeometry(9000, 5000), lam(0x8f8d80));
    fl.rotation.x = -Math.PI / 2; fl.position.set(0, y - .05, 690 + 2500 - 2); scene.add(fl); }

  // ---- things to compare with ----
  for (const o of W.sizes || []) {
    const y = E.groundAt ? E.groundAt(o.x, o.z) : 0;
    let h;
    if (o.kind === 'house') h = house(E, { x: o.x, y, z: o.z, w: o.w ?? 9, d: o.d ?? 10, h: o.h - (o.roofH ?? 3.4), roofH: o.roofH ?? 3.4, ry: o.ry ?? 0, color: o.color ?? 0xe6dccb, roof: 0x8a4b3c, chimney: false }).h;
    else { h = tower(E, { x: o.x, y, z: o.z, w: o.w ?? 34, d: o.d ?? 30, h: o.h, color: o.color ?? 0x9fb2bd }).h;
      const crown = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry((o.w ?? 34) * .6, 6, (o.d ?? 30) * .6), lam(0x6f7d86))); crown.position.set(o.x, y + h + 3, o.z); scene.add(crown);
      const mast = new THREE.Mesh(new THREE.CylinderGeometry(.4, .6, 18, 5), lam(0xb9c0c4)); mast.position.set(o.x, y + h + 15, o.z); scene.add(mast); }
    if (o.label) { const s = tag(E, `${o.h} m`); s.position.set(o.x + (o.tagDx ?? 0), y + h + (o.tagDy ?? (o.kind === 'house' ? 3 : 34)), o.z); E.updates.push(t => show(s, o.label, t)); }
  }
  for (const o of W.tags || []) { const s = tag(E, o.text, o.color); s.position.set(...o.pos); E.updates.push(t => show(s, o.at, t)); }

  // ---- the mountain and the run-up ----
  if (W.runup) {
    const R0 = W.runup, hAt = monotone(R0.h), [mx, mz] = R0.at, [rx, rz] = R0.r, peak = R0.peak ?? 900, Rr = rng(77);
    const hf = (x, z) => { const q = 1 - ((x - mx) / rx) ** 2 - ((z - mz) / rz) ** 2; if (q <= 0) return -2;
      return peak * q ** .75 + (hash(Math.round(x / 40), Math.round(z / 40)) - .5) * 18 * q; };
    const N = 90, g = new THREE.PlaneGeometry(rx * 2, rz * 2, N, N); g.rotateX(-Math.PI / 2);
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i) + mx, z = p.getZ(i) + mz; p.setXYZ(i, x, hf(x, z), z); }
    g.computeVertexNormals();
    const col = new Float32Array(p.count * 3), c = new THREE.Color();
    for (let i = 0; i < p.count; i++) { const y = p.getY(i);
      c.set(0x5d6b4c).lerp(new THREE.Color(0x7a7266), smooth(peak * .55, peak * .8, y)).lerp(new THREE.Color(0xeef1f3), smooth(peak * .8, peak * .9, y));
      c.toArray(col, i * 3); }
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const mtn = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true })); mtn.receiveShadow = true; scene.add(mtn);
    // forest: cones on the lower slopes
    const trees = [], NT = 2600, tg = new THREE.ConeGeometry(4, 14, 5); tg.translate(0, 7, 0);
    for (let k = 0; trees.length < NT && k < NT * 6; k++) {
      const x = mx - rx + Rr() * rx * 2, z = mz - rz + Rr() * rz * 2, y = hf(x, z);
      if (y < 4 || y > peak * .62) continue; trees.push([x, y, z, .7 + Rr() * .7]);
    }
    const im = new THREE.InstancedMesh(tg, lam(0x2f4a33), trees.length); im.castShadow = true; scene.add(im);
    const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), S = new THREE.Vector3(), V = new THREE.Vector3();
    const [fx, fz, fc] = R0.face ?? [-1, 0, mx], onFace = (x, z) => fx * x + fz * z + fc >= 0;   // the water only climbs the face toward the town: fx*x + fz*z + fc >= 0
    let lastH = -1;
    const place = h => { trees.forEach(([x, y, z, s], i) => { const gone = onFace(x, z) && y < h; S.setScalar(gone ? 0 : s); M.compose(V.set(x, y, z), Q, S); im.setMatrixAt(i, M); }); im.instanceMatrix.needsUpdate = true; };
    place(0);
    // the water sheet: the same slope, a little above it, clipped at the run-up height
    const sheet = new THREE.Mesh(g.clone(), new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true, transparent: true, opacity: .97,
      clippingPlanes: [new THREE.Plane(new THREE.Vector3(0, -1, 0), 0), new THREE.Plane(new THREE.Vector3(fx, 0, fz), fc)] }));
    sheet.position.y = 2.5; scene.add(sheet);
    const sc = new Float32Array(p.count * 3); sheet.geometry.setAttribute('color', new THREE.BufferAttribute(sc, 3));
    E.updates.push((t) => {
      const h = hAt(t); sheet.material.clippingPlanes[0].constant = h; sheet.visible = h > 1;
      for (let i = 0; i < p.count; i++) { const y = p.getY(i), f = smooth(h - 45, h - 5, y); c.set(0x3f8e98).lerp(new THREE.Color(0xf2f6f5), f); c.toArray(sc, i * 3); }
      sheet.geometry.attributes.color.needsUpdate = true;
      if (Math.abs(h - lastH) > .5) { place(h); lastH = h; }
    });
    const edge = []; for (let i = 0; i < p.count; i++) if (onFace(p.getX(i), p.getZ(i)) && p.getY(i) > 3) edge.push([p.getX(i), p.getY(i), p.getZ(i)]);
    E.emitters.push((tv, add) => {        // spray and mist at the leading edge while it climbs
      const h = hAt(tv), dh = hAt(tv + .3) - h; if (h < 5) return;
      const k0 = clamp(dh * 3, .15, 1);
      let n = 0;
      for (let k = 0; k < edge.length && n < 900; k++) { const [x, y, z] = edge[k]; if (y > h || y < h - 60) continue;
        const u = (tv * .6 + hash(k, 4)) % 1; n++;
        add(x + fx * u * 10, y + 4 + u * 26, z, 14 + u * 30, Math.sin(u * Math.PI) * .5 * k0, .96, .97, .97, hash(k, 5) * 6); }
    });
    if (R0.label) { const s = tag(E, `${Math.round(hAt(1e9))} m`, '#ffffff'); const [lx, lz] = R0.labelAt;
      s.position.set(lx, hAt(1e9) + 30, lz); E.updates.push(t => show(s, R0.label, t));
      const line = new THREE.Mesh(new THREE.BoxGeometry(1, 1.6, 260), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, fog: false }));
      line.position.set(lx, hAt(1e9) + 2, lz); line.rotation.y = R0.lineRy ?? 0; scene.add(line); E.updates.push(t => { line.material.opacity = .7 * smooth(R0.label[0], R0.label[0] + 1, t); }); }
  }
}
