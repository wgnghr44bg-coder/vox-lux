// Visual Explainer Engine — vaste huisstijl (donker, filmisch, rustig). Alles leest hieruit, zodat elke video herkenbaar is.
export const FPS = 30;
export const W = 1920;
export const H = 1080;

export const kleur = {
  achter1: "#070B16", // achtergrond boven
  achter2: "#0E1A2E", // achtergrond onder
  raster: "rgba(120,160,220,0.07)",
  tekst: "#EAF0FA",
  zacht: "#8A9BB8",
  cyaan: "#3DD6F5",
  amber: "#F5B13D",
  rood: "#FF5A5F",
  groen: "#3DDC97",
  nvidia: "#76B900",
  paneel: "rgba(18,30,52,0.72)",
  rand: "rgba(120,170,240,0.22)",
};

export const font = {
  kop: "'Segoe UI Semibold', 'Segoe UI', Arial, sans-serif",
  zwaar: "'Segoe UI Black', 'Segoe UI', Arial, sans-serif",
  tekst: "'Segoe UI', Arial, sans-serif",
  cijfer: "'Bahnschrift', 'Segoe UI', Arial, sans-serif",
};

// zachte, filmische versnelling (ease-out cubic)
export const zacht = (x: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 3);
export const inUit = (x: number) => {
  const t = Math.min(1, Math.max(0, x));
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
};
