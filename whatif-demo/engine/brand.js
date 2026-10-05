// Channel name in the scene, once per video: a sign/billboard with "IfScape3D" ("3D" in amber).
// The place says where (E.brandSpot = { pos, ry, w, h, shot }); the POV camera glances at it once
// for ~1.6 s during the calm opening (TL.beats.brand overrides the moment) and then looks away.
import * as THREE from 'three';

export function createBrand(E, TL) {
  const S = E.brandSpot; if (!S || TL.brand === false) return;
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
  if (S.logo !== false) new THREE.TextureLoader().load('../branding/logo.png', t => { t.colorSpace = THREE.SRGBColorSpace; face.material.map = t; face.material.needsUpdate = true; face.scale.set(1, (S.w ?? 6) / (S.h ?? 3), 1); back.scale.set(1, ((S.w ?? 6) + .3) / ((S.h ?? 3) + .3), 1); face.position.y = back.position.y = ((S.w ?? 6) - (S.h ?? 3)) / 2; });
  const g = new THREE.Group(); g.position.set(...S.pos); g.rotation.y = S.ry ?? 0; E.scene.add(g);
  const w = S.w ?? 6, h = S.h ?? 3;
  const face = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex })); face.position.z = .08; g.add(face);
  const back = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(w + .3, h + .3, .15), E.lam(0x2a2d31))); g.add(back);
  if (S.posts) for (const sx of [-w / 3, w / 3]) { const p = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(.15, S.posts, .15), E.lam(0x3a3d41))); p.position.set(sx, -h / 2 - S.posts / 2, -.05); g.add(p); }
  // one glance: the first time the named shot is on screen after the first lines, unless the scenario sets beats.brand
  let t = TL.beats.brand;
  if (t == null) { const s = TL.shots.find(([ts, name]) => name === S.shot && ts > 3) || TL.shots.find(([, name]) => name === S.shot); t = s ? Math.max(s[0], 3) + 1.2 : null; }
  if (t != null && t < TL.beats.climax - 6) (TL.looks ||= []).push([t, S.pos, 1.6, 9]);
}
