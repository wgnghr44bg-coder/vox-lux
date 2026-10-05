// Channel name in the scene, once per video: a sign/billboard with "IfScape3D" ("3D" in amber).
// The place says where (E.brandSpot = { pos, ry, w, h, shot }); the POV camera glances at it once
// for ~1.6 s during the calm opening (TL.beats.brand overrides the moment) and then looks away.
import * as THREE from 'three';

export function createBrand(E, TL) {
  const S = E.brandSpot; if (!S || TL.brand === false) return;
  if (S.type === 'flag') return beachFlag(E, TL, S);
  const cv = document.createElement('canvas'); cv.width = 512; cv.height = 256;
  const x = cv.getContext('2d');
  const draw = () => {
    x.fillStyle = '#16181c'; x.fillRect(0, 0, 512, 256);
    x.strokeStyle = '#2c3036'; x.lineWidth = 10; x.strokeRect(5, 5, 502, 246);
    x.textAlign = 'center'; x.textBaseline = 'middle'; x.font = '600 92px PF, Georgia, serif';
    const a = x.measureText('IfScape').width, b = x.measureText('3D').width, x0 = 256 - (a + b) / 2;
    x.textAlign = 'left'; x.fillStyle = '#f3ede2'; x.fillText('IfScape', x0, 128); x.fillStyle = '#e9a85a'; x.fillText('3D', x0 + a, 128);
    tex.needsUpdate = true;
  };
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  draw(); document.fonts.ready.then(draw);
  // the channel logo (branding/logo.png) on a square sign; the drawn name stays as fallback
  // only the globe and the name (branding/logo-cut.png, transparent background), no board behind it
  if (S.logo !== false) (E.loading ||= []).push(new Promise(ok => new THREE.TextureLoader().load('../branding/logo-cut.png', t => {
    t.colorSpace = THREE.SRGBColorSpace; Object.assign(face.material, { map: t, transparent: true, alphaTest: .05 }); face.material.needsUpdate = true;
    // the logo sits on a light billboard panel (keeps its own aspect, centred on the panel)
    const k = Math.min(1, (S.h ?? 3) / (S.w ?? 6)) * .95; face.scale.set(k, (S.w ?? 6) / (S.h ?? 3) * k, 1);
    back.material = E.lam(S.panel ?? 0xf1ede4); ok(); }, undefined, ok)));
  const g = new THREE.Group(); g.position.set(...S.pos); g.rotation.y = S.ry ?? 0; E.scene.add(g);
  const w = S.w ?? 6, h = S.h ?? 3;
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 })); face.position.z = .14; g.add(face);
  const back = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(w + .3, h + .3, .15), E.lam(0x2a2d31))); g.add(back);
  const frame = new THREE.Mesh(new THREE.BoxGeometry(w + .5, h + .5, .1), E.lam(0x2a2d31)); frame.position.z = -.06; g.add(frame);
  if (S.arm) {        // steel arm from the top of the sign to the wall
    const top = new THREE.Vector3(0, h / 2 + .25, 0).applyMatrix4(g.matrixWorld.compose(g.position, g.quaternion, g.scale)), to = new THREE.Vector3(...S.arm);
    const len = top.distanceTo(to), arm = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(.12, .12, len), E.lam(0x2f3236)));
    arm.position.copy(top).add(to).multiplyScalar(.5); arm.lookAt(to); E.scene.add(arm);
    for (const dx of [-w / 3, w / 3]) { const hng = new THREE.Mesh(new THREE.BoxGeometry(.05, .3, .05), E.lam(0x2f3236)); hng.position.set(dx, h / 2 + .4, 0); g.add(hng); }
  }
  if (S.posts) for (const sx of [-w / 3, w / 3]) { const p = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(.15, S.posts, .15), E.lam(0x3a3d41))); p.position.set(sx, -h / 2 - S.posts / 2, -.05); g.add(p); }
  // one glance: the first time the named shot is on screen after the first lines, unless the scenario sets beats.brand
  let t = TL.beats.brand;
  if (t == null) { const s = TL.shots.find(([ts, name]) => name === S.shot && ts > 3) || TL.shots.find(([, name]) => name === S.shot); t = s ? Math.max(s[0], 3) + 1.2 : null; }
  if (t != null && t < TL.beats.climax - 6) (TL.looks ||= []).push([t, S.pos, 1.6, 9]);
}

// tall beach flag: pole + a light banner with the logo, waving gently (stronger in wind)
function beachFlag(E, TL, S) {
  const g = new THREE.Group(); g.position.set(...S.pos); g.rotation.y = S.ry ?? 0; E.scene.add(g);
  const H = S.height ?? 5.5, w = S.w ?? 1.8, h = S.h ?? 2.6;
  const pole = E.shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.04, .05, H, 6), E.lam(0xd9d6cc))); pole.position.y = H / 2; g.add(pole);
  const piv = new THREE.Group(); piv.position.set(0, H - .1, 0); g.add(piv);
  const banner = new THREE.Mesh(new THREE.PlaneGeometry(w, h, 6, 1), new THREE.MeshLambertMaterial({ color: S.panel ?? 0xf3efe6, side: THREE.DoubleSide }));
  banner.position.set(w / 2 + .05, -h / 2, 0); piv.add(banner);
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(w * .92, w * .92), new THREE.MeshBasicMaterial({ transparent: true, alphaTest: .05 }));
  logo.position.set(w / 2 + .05, -w * .55, .01); piv.add(logo);
  (E.loading ||= []).push(new Promise(ok => new THREE.TextureLoader().load('../branding/logo-cut.png', t => { t.colorSpace = THREE.SRGBColorSpace; logo.material.map = t; logo.material.needsUpdate = true; ok(); }, undefined, ok)));
  E.updates.push((t, F, tv) => { const a = .08 + (F.lateral ? F.lateral(t).a : 0) * .6; piv.rotation.y = Math.sin(tv * 2.1) * a; piv.rotation.z = Math.sin(tv * 1.3) * .02; });
  let tl = TL.beats.brand;
  if (tl == null) { const s = TL.shots.find(([ts, name]) => name === S.shot && ts > 3) || TL.shots.find(([, name]) => name === S.shot); tl = s ? Math.max(s[0], 3) + 1.2 : null; }
  if (tl != null && tl < TL.beats.climax - 6) (TL.looks ||= []).push([tl, [S.pos[0], S.pos[1] + H - h / 2, S.pos[2]], 1.6, 9]);
}
