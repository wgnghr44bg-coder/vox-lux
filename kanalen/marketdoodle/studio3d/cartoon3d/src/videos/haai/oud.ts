// De oude Market Doodle-figuren (plaatjes uit maak_oude_figuren.py) als textures, één keer vooraf geladen.
import * as THREE from "three";
import { staticFile } from "remotion";
import { NAMEN } from "./oudmaat";

export const OUD = new Map<string, THREE.Texture>();
let p: Promise<void> | null = null;
export const laadOud = () => {
  if (!p) {
    const loader = new THREE.TextureLoader();
    p = Promise.all(NAMEN.map((n) => loader.loadAsync(staticFile(`oud/${n}.png`)).then((t) => {
      t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; OUD.set(n, t);
    }))).then(() => undefined);
  }
  return p;
};
export const oud = (n: string) => {
  const t = OUD.get(n);
  if (!t) throw new Error("oud plaatje ontbreekt: " + n);
  return t;
};
