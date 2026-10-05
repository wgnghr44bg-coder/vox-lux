// Lifebuoy with the channel name ("IfScape3D", "3D" in amber) on orange/white segments.
// lifebuoy(E, { pos, ry }) -> THREE.Group lying flat on the water (float it with the water level).
import * as THREE from 'three';

export function lifebuoy(E, o = {}) {
  const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 128;
  const x = cv.getContext('2d');
  const draw = () => {
    for (let i = 0; i < 4; i++) { x.fillStyle = i % 2 ? '#f4f1ea' : '#e8642c'; x.fillRect(i * 256, 0, 256, 128); }
    // the top of the tube is v = .25 (canvas y ≈ 96); flip vertically so the name reads upright from outside the ring
    x.save(); x.translate(0, 192); x.scale(1, -1);
    x.font = '600 50px PF, Georgia, serif'; x.textBaseline = 'middle';
    for (const c of [128, 640]) {   // the name on both orange segments
      const a = x.measureText('IfScape').width, b = x.measureText('3D').width, x0 = c - (a + b) / 2;
      x.fillStyle = '#fbf6ec'; x.fillText('IfScape', x0, 96); x.fillStyle = '#ffd59a'; x.fillText('3D', x0 + a, 96);
    }
    x.restore();
    tex.needsUpdate = true;
  };
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  draw(); document.fonts.ready.then(draw);
  const g = new THREE.Group();
  const ring = E.shadowed(new THREE.Mesh(new THREE.TorusGeometry(.62, .2, 12, 40), new THREE.MeshLambertMaterial({ map: tex })));
  ring.rotation.x = -Math.PI / 2; g.add(ring);
  const rope = new THREE.Mesh(new THREE.TorusGeometry(.84, .025, 4, 40), E.lam(0xd9d2c0)); rope.rotation.x = -Math.PI / 2; g.add(rope);
  if (o.pos) g.position.set(...o.pos); g.rotation.y = o.ry ?? 0; E.scene.add(g);
  return g;
}
