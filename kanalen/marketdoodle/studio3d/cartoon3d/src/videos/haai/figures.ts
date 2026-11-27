// Onze eigen figuren voor de haai-proef, getekend met de Pen van de cartoon-3d-short skill (inktrand, platte kleuren,
// zachte schaduwkant). De haai: zijaanzicht, grote benen, piepkleine armpjes, domme ogen. Ontwerpdoek 1100 x 1000,
// voetzolen op y = 975 (zelfde afspraak als toon.ts).
import { Pen, INK } from "../bridge/toon";

type P2 = [number, number];
const rad = (d: number) => (d * Math.PI) / 180;

export const SHARK = { skin: "#7f9cc0", skinDark: "#5f7ba0", belly: "#f4efe4", shoe: "#e8463a", sole: "#ffffff", lace: "#ffffff" };
export type SharkOpts = { phase: number; walk: number; arm: number; look: "dumb" | "happy" | "focus"; blink: number; squash?: number };

/** één been: heup -> knie -> enkel, dik en rond, met een grote sneaker */
const leg = (p: Pen, hip: P2, ph: number, A: number, far: boolean) => {
  const s = Math.sin(ph), c = Math.cos(ph);
  const fx = hip[0] + s * 125 * A, lift = Math.max(0, c) * 70 * A;
  const ank: P2 = [fx, 905 - lift];
  const knee: P2 = [(hip[0] + ank[0]) / 2 + 38 + 30 * A * Math.max(0, c), (hip[1] + ank[1]) / 2];
  const col = far ? SHARK.skinDark : SHARK.skin;
  p.line([hip, knee], col, 150, true);
  p.line([knee, ank], col, 112, true);
  p.line([hip, knee], col, 150, false);
  // sneaker: neus naar rechts (looprichting)
  const tilt = -0.18 * s * A;
  p.rot = [tilt, ank[0], ank[1] + 40];
  p.ell(ank[0] + 42, ank[1] + 38, 108, 44, far ? "#b8372e" : SHARK.shoe);
  p.poly([[ank[0] - 62, ank[1] + 56], [ank[0] + 148, ank[1] + 56], [ank[0] + 150, ank[1] + 76], [ank[0] - 64, ank[1] + 76]], SHARK.sole, 9);
  if (!far) { p.stroke([[ank[0] + 10, ank[1] + 6], [ank[0] + 46, ank[1] + 22]], 9, SHARK.lace); p.stroke([[ank[0] + 30, ank[1] - 2], [ank[0] + 66, ank[1] + 14]], 9, SHARK.lace); }
  p.rot = null;
};

export const drawShark = (p: Pen, o: SharkOpts) => {
  const ph = o.phase * Math.PI * 2, A = o.walk;
  const bob = -Math.abs(Math.sin(ph)) * 16 * A + (o.squash ?? 0) * 30;
  const cy = 410 + bob;
  // ver been (achter het lijf)
  leg(p, [610, cy + 150], ph + Math.PI, A, true);
  // staart: twee lobben
  p.poly([[230, cy - 10], [70, cy - 210], [118, cy - 40], [96, cy + 150], [235, cy + 25]], SHARK.skinDark);
  // lijf
  const top: P2[] = [], bot: P2[] = [];
  for (let i = 0; i <= 40; i++) {
    const u = i / 40, x = 200 + u * 850;
    const h = 175 * Math.pow(Math.sin(Math.PI * Math.min(1, u * 1.08 + 0.02)), 0.62) + 18;
    top.push([x, cy - h * 1.0 + u * 22]);
    bot.push([x, cy + h * 0.95 + u * 10]);
  }
  const body: P2[] = [...top, ...bot.reverse()];
  // rugvin achter het lijf (onderkant valt weg achter het lijf)
  p.poly([[520, cy - 150], [650, cy - 345], [690, cy - 340], [745, cy - 160]], SHARK.skin);
  p.poly(body, SHARK.skin, 0);
  p.clip(body, () => {
    p.poly([[150, cy + 40], [600, cy + 70], [1100, cy + 20], [1100, 900], [150, 900]], SHARK.belly, 0);
    p.g.fillStyle = "rgba(40,50,90,0.16)"; p.g.fillRect(0, cy + 120, 1100, 400); // schaduw onderkant
    p.g.fillStyle = "rgba(255,255,255,0.18)"; p.g.beginPath(); p.g.ellipse(760, cy - 120, 260, 50, -0.05, 0, Math.PI * 2); p.g.fill(); // glans
  });
  p.poly(body, null);
  // kieuwen
  for (let i = 0; i < 3; i++) p.arc(770 - i * 34, cy + 10, 26, 70, 250, 110, 8);
  // bek: brede domme glimlach met tandjes
  const m0: P2 = [865, cy + 62], m1: P2 = [1030, cy + 30];
  const mouth: P2[] = [];
  for (let i = 0; i <= 16; i++) { const u = i / 16; mouth.push([m0[0] + (m1[0] - m0[0]) * u, m0[1] + (m1[1] - m0[1]) * u + Math.sin(Math.PI * u) * 46]); }
  p.poly([...mouth, [m1[0] - 10, m1[1] + 4], [m0[0] + 10, m0[1] - 2]], "#5a1e28", 9);
  for (let i = 1; i < 8; i++) {
    const u = i / 8, x = m0[0] + (m1[0] - m0[0]) * u, y = m0[1] + (m1[1] - m0[1]) * u;
    p.poly([[x - 11, y - 2], [x + 11, y - 2], [x, y + 22]], "#ffffff", 4);
  }
  // ogen: ver oog half achter de kop, dichtbij oog groot. "dumb" = scheel, pupillen elk een kant op
  const blink = o.blink;
  const eye = (x: number, y: number, r: number, px: number, py: number) => {
    if (blink > 0.5) { p.arc(x, y, r, r * 0.5, 10, 170, 9); return; }
    p.ell(x, y, r, r * 1.08, "#ffffff", 9);
    p.dot(x + px, y + py, r * 0.36);
    p.dot(x + px - r * 0.12, y + py - r * 0.14, r * 0.1, "#ffffff");
  };
  if (o.look === "dumb") { eye(985, cy - 78, 30, -14, 10); eye(915, cy - 70, 46, 18, -14); }
  else if (o.look === "focus") { eye(985, cy - 78, 30, 12, 4); eye(915, cy - 70, 46, 16, 4); }
  else { p.arc(985, cy - 74, 26, 18, 200, 340, 10); p.arc(915, cy - 66, 40, 26, 200, 340, 11); }
  // wenkbrauw
  p.stroke([[878, cy - 132], [948, cy - 140]], 12, INK);
  // piepkleine armpjes (twee stokjes met handje), zwaaien met arm 0..1
  for (const [ax, far] of [[812, true], [850, false]] as [number, boolean][]) {
    const a = rad(70 - 70 * o.arm * (far ? 0.6 : 1) + (far ? 12 : 0));
    const sh: P2 = [ax, cy + 118], hand: P2 = [ax + Math.cos(a) * 62, cy + 118 + Math.sin(a) * 62];
    p.line([sh, hand], far ? SHARK.skinDark : SHARK.skin, 22, true);
    p.ell(hand[0], hand[1], 15, 15, far ? SHARK.skinDark : SHARK.skin, 7);
  }
  // dichtbij been (voor het lijf)
  leg(p, [690, cy + 160], ph, A, false);
};

/** contactschaduw onder voeten: zacht ovaal, op een plat kaartje (multiply) */
export const drawBlob = (p: Pen) => {
  const g = p.g, gr = g.createRadialGradient(300, 100, 10, 300, 100, 290);
  gr.addColorStop(0, "rgba(60,50,80,0.55)"); gr.addColorStop(0.6, "rgba(60,50,80,0.3)"); gr.addColorStop(1, "rgba(60,50,80,0)");
  g.fillStyle = "#ffffff"; g.fillRect(0, 0, 600, 200);
  g.save(); g.scale(1, 1); g.fillStyle = gr; g.beginPath(); g.ellipse(300, 100, 290, 90, 0, 0, Math.PI * 2); g.fill(); g.restore();
};

/** splinters van de garagedeur (los effect) */
export const drawSplinters = (p: Pen, t: number) => {
  for (let i = 0; i < 9; i++) {
    const a = rad(-160 + i * 17 + (i % 3) * 5), d = 60 + 330 * (1 - (1 - t) ** 2) * (0.7 + 0.3 * ((i * 7) % 5) / 4);
    const x = 400 + Math.cos(a) * d, y = 400 + Math.sin(a) * d + 260 * t * t;
    p.rot = [a + t * 6 * (i % 2 ? 1 : -1), x, y];
    p.poly([[x - 34, y - 9], [x + 34, y - 6], [x + 30, y + 9], [x - 30, y + 7]], "#f3eee3", 6);
    p.rot = null;
  }
};
