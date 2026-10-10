// AUTO BLOCK floating-cars: several cars floating and slowly drifting, bobbing and tilting on flood water that covers a city road.
// Use in scenario.js:  auto: [{ block: 'floating-cars', pos: [[-12,0,-82],[-3,0,-95],[8,0,-73],[18,0,-88],[-7,0,-108]], from:0, full:1, until:1e9 }]
//
// export default function build(E, TL, o, F) adds low-poly floating cars to E.scene.
// Cars bob/tilt/drift using F.field(t).waterY (full flood so waterY >= 0.6 above road).
const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const THREE = E.THREE;
  const R = rng(31);
  const positions = o.pos || [[-12,0,-82],[-3,0,-95],[8,0,-73],[18,0,-88],[-7,0,-108]];
  const cars = [];
  const carMat = E.lam(0x334455);
  const winMat = E.lam(0x88aadd);
  for (let i = 0; i < positions.length; i++) {
    const g = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(4.6,1.6,2.3), carMat);
    body.position.y = 0.8; g.add(body);
    const roof = new THREE.Mesh(new THREE.BoxGeometry(2.8,1.0,2.1), carMat);
    roof.position.set(0,1.85,0); g.add(roof);
    const winF = new THREE.Mesh(new THREE.BoxGeometry(1.2,0.8,2.15), winMat);
    winF.position.set(1.0,1.8,0); g.add(winF);
    const winR = new THREE.Mesh(new THREE.BoxGeometry(1.2,0.8,2.15), winMat);
    winR.position.set(-1.0,1.8,0); g.add(winR);
    E.shadowed(body); E.shadowed(roof);
    E.scene.add(g);
    cars.push({g, base: positions[i], phase: i*1.7 + R()*0.6, drift: 0.022 + R()*0.009});
  }
  return (t, tv) => {
    const wy = F.field(t).waterY || -10;
    for (let i = 0; i < cars.length; i++) {
      const c = cars[i];
      const bob = Math.sin(tv*0.75 + c.phase)*0.22;
      const tilt = Math.sin(tv*0.55 + c.phase*1.4)*0.11;
      const driftX = Math.sin(tv*0.13 + c.phase)*c.drift;
      c.g.position.set(c.base[0]+driftX, wy + bob + 0.4, c.base[2]);
      c.g.rotation.set(tilt*0.7, tilt*2.0, tilt);
    }
  };
}
