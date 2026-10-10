// Small brick "planes": a low-poly airliner (parked, taxiing or grounded). Registers its paint as an ash/frost
// surface, so a covering force (eruption ash, cold) can grey it.   airliner(E, x, z, ry, { scale, color, stripe, y })
import * as THREE from 'three';

export function airliner(E, x, z, ry = 0, o = {}) {
  const { lam, shadowed } = E, g = new THREE.Group(), s = o.scale ?? 1; g.position.set(x, o.y ?? E.groundAt(x, z), z); g.rotation.y = ry; g.scale.setScalar(s); E.scene.add(g);
  const paint = lam(o.color ?? 0xe9ebec), stripe = lam(o.stripe ?? 0x2f5d8a), grey = lam(0xa9adb0), dark = lam(0x2a2e33);
  (E.ashRoofs ||= []).push(paint, grey); E.frost.push(paint);
  const Y = 4.2;                               // fuselage axis height (on its gear)
  const body = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(2, 2, 30, 12), paint)); body.rotation.x = Math.PI / 2; body.position.y = Y; g.add(body);
  const nose = shadowed(new THREE.Mesh(new THREE.SphereGeometry(2, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2), paint)); nose.rotation.x = -Math.PI / 2; nose.scale.y = 2; nose.position.set(0, Y, -15); g.add(nose);
  const tail = shadowed(new THREE.Mesh(new THREE.ConeGeometry(2, 9, 12), paint)); tail.rotation.x = Math.PI / 2; tail.position.set(0, Y + .5, 19.5); g.add(tail);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(2.02, 2.02, 30, 12, 1, true, Math.PI * .35, Math.PI * .3), stripe); band.rotation.x = Math.PI / 2; band.position.y = Y; g.add(band);
  for (const sx of [-1, 1]) {                  // window rows and cockpit
    const w = new THREE.Mesh(new THREE.BoxGeometry(.05, .35, 24), dark); w.position.set(sx * 2.01, Y + .6, 1); g.add(w);
    const ck = new THREE.Mesh(new THREE.BoxGeometry(.6, .4, .8), dark); ck.position.set(sx * .9, Y + 1.1, -16.6); ck.rotation.y = sx * .5; g.add(ck);
  }
  const wingShape = new THREE.Shape(); wingShape.moveTo(0, 0); wingShape.lineTo(17, 6); wingShape.lineTo(17, 8.5); wingShape.lineTo(0, 7); wingShape.closePath();
  const wg = new THREE.ExtrudeGeometry(wingShape, { depth: .45, bevelEnabled: false }); wg.rotateX(Math.PI / 2);
  for (const sx of [-1, 1]) {
    const w = shadowed(new THREE.Mesh(wg, grey)); w.scale.x = sx; w.position.set(sx * 1.2, Y - 1, -3); g.add(w);
    const eng = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(1.1, .9, 4.2, 10), grey)); eng.rotation.x = Math.PI / 2; eng.position.set(sx * 6.5, Y - 2.4, -1.5); g.add(eng);
    const intake = new THREE.Mesh(new THREE.CircleGeometry(.95, 10), dark); intake.position.set(sx * 6.5, Y - 2.4, -3.62); intake.rotation.y = Math.PI; g.add(intake);
    const st = shadowed(new THREE.Mesh(new THREE.BoxGeometry(6, .25, 2.6), paint)); st.position.set(sx * 3.6, Y + 1, 21); st.rotation.y = sx * -.3; g.add(st);
  }
  const fin = new THREE.Shape(); fin.moveTo(0, 0); fin.lineTo(4.5, 0); fin.lineTo(6.5, 7); fin.lineTo(4.5, 7); fin.closePath();
  const fg = new THREE.ExtrudeGeometry(fin, { depth: .35, bevelEnabled: false }); fg.rotateY(-Math.PI / 2);
  const f = shadowed(new THREE.Mesh(fg, stripe)); f.position.set(.17, Y + 1.5, 17); g.add(f);
  for (const [gx, gz] of [[0, -12], [-2.6, 1], [2.6, 1]]) {   // landing gear
    const leg = new THREE.Mesh(new THREE.BoxGeometry(.25, Y - 1.4, .25), grey); leg.position.set(gx, (Y - 1.4) / 2 + .6, gz); g.add(leg);
    const wh = new THREE.Mesh(new THREE.CylinderGeometry(.6, .6, .5, 10), dark); wh.rotation.z = Math.PI / 2; wh.position.set(gx, .6, gz); g.add(wh);
  }
  return g;
}
