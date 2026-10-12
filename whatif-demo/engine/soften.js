// Blender look (main.js, look=blender): people and animals get rounded, smooth shapes like a Blender render.
// Boxes become rounded boxes, cylinders/cones/spheres get more segments, ellipsoids get finer; smooth shading.
// Trees, houses and props stay flat low-poly. Runs once after the scene is built; geometry only, no new materials.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const cache = new Map();
function finer(geo) {
  const p = geo.parameters || {}, key = geo.type + JSON.stringify(p);
  if (cache.has(key)) return cache.get(key);
  let g = null;
  if (geo.type === 'BoxGeometry') { const r = Math.min(p.width, p.height, p.depth) * .45; g = new RoundedBoxGeometry(p.width, p.height, p.depth, 3, r); }
  else if (geo.type === 'CylinderGeometry') g = new THREE.CylinderGeometry(p.radiusTop, p.radiusBottom, p.height, Math.max(16, p.radialSegments), 1, p.openEnded);
  else if (geo.type === 'ConeGeometry') g = new THREE.ConeGeometry(p.radius, p.height, Math.max(16, p.radialSegments));
  else if (geo.type === 'SphereGeometry') g = new THREE.SphereGeometry(p.radius, 24, 16, p.phiStart, p.phiLength, p.thetaStart, p.thetaLength);
  else if (geo.type === 'IcosahedronGeometry') g = new THREE.IcosahedronGeometry(p.radius, Math.max(3, p.detail));
  cache.set(key, g); return g;
}

export function soften(E) {
  const roots = [...E.people.map(p => p.g), ...E.animals.map(a => a.g).filter(Boolean)];
  const mats = new Set();
  for (const root of roots) root.traverse(o => {
    if (!o.isMesh || o.isInstancedMesh) return;
    const g = finer(o.geometry); if (g) o.geometry = g;
    for (const m of [o.material].flat()) if (m && m.flatShading) mats.add(m);
  });
  for (const m of mats) { m.flatShading = false; m.needsUpdate = true; }
}
