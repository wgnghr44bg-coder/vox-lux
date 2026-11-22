import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { FPS, kleur } from "./theme";
import { Achtergrond, Kop, Groot, Label, Fade } from "./scenes/Basis";
import { IsoWereld } from "./scenes/IsoWereld";
import { GeldStroom } from "./scenes/GeldStroom";
import { KoersLijn, DagStaven, TijdLijn } from "./scenes/Infographic";
import zinnen from "./data/zinnen.json";
import woorden from "./data/woorden.json";
import nvda from "./data/nvda.json";

// SCÈNEPLAN (demo, 22 nov 2026): per stukje tekst één beeld, op het kernwoord (woorden.json van Whisper).
const Z = zinnen as [number, number, string, string][];
const Wd = woorden as [number, string, number, number][];
const fr = (s: number) => Math.round(s * FPS);
const kw = (zin: number, woord: string, na = 0) => {
  const w = Wd.find((x) => x[0] === zin && x[1].toLowerCase().replace(/[^\w$%.]/g, "").startsWith(woord.toLowerCase()));
  return fr((w ? w[2] : Z[zin][0]) + na);
};
const data = nvda as [string, number][];
const laatste = data.slice(-128);

type Sc = { van: number; tot: number; el: (s: number) => React.ReactNode };
const s0 = 0, s1 = fr(Z[2][0] - 0.3), s2 = fr(Z[4][0] - 0.4), s3 = fr(Z[8][0] - 0.4), s4 = fr(Z[12][0] - 0.4), s5 = fr(Z[15][0] - 0.4);
export const demoDuur = fr(Z[Z.length - 1][1] + 1.8);

const scenes: Sc[] = [
  // 1 — LEVENDE INFOGRAPHIC: de klap van vrijdag
  { van: s0, tot: s1, el: (s) => (<>
      <Kop nr="NVIDIA · NOV 20" tekst="One day, one big fall" />
      <Groot tekst="−14%" van={kw(0, "14") - s} x={110} y={330} maat={230} kleur={kleur.rood} sub="in a single day" />
      <DagStaven data={data} n={7} start={kw(1, "seventh", -0.3) - s} per={5} x={840} y={360} w={960} h={380} />
      <Label tekst="7th drop in a row" van={kw(1, "row") - s} x={840} y={820} k={kleur.rood} />
  </>) },
  // 2 — ISOMETRISCHE WERELD: de campus; de lichten van de hoofdtoren gaan uit als de oprichter vertrekt
  { van: s1, tot: s2, el: (s) => (<>
      <IsoWereld lichtUitOp={kw(2, "walked") - s} />
      <Kop nr="THE COMPANY" tekst="The founder walks away" />
      <Label tekst="The man who built it left" van={kw(2, "walked") - s} x={1240} y={820} k={kleur.amber} />
      <Groot tekst="Here is what happened" van={kw(3, "here") - s} x={960} y={900} maat={54} kleur={kleur.tekst} uitlijn="center" />
  </>) },
  // 3 — LEVENDE INFOGRAPHIC (tijdlijn): 33 jaar Jensen Huang
  { van: s2, tot: s3, el: (s) => (<>
      <Kop nr="1993 – 2026" tekst="The man who built Nvidia" />
      <TijdLijn van={1993} tot={2026} start={0} x={180} y={620} w={1560} punten={[
        { jaar: 1993, tekst: "Founded in a Denny's booth", op: kw(4, "1993") - s },
        { jaar: 2026, tekst: "Nov 12: stepped down", op: kw(7, "november") - s, k: kleur.rood },
      ]} />
      <Groot tekst="33 years" van={kw(5, "33") - s} x={960} y={250} maat={140} kleur={kleur.amber} uitlijn="center" />
      <Label tekst="Black leather jacket" van={kw(6, "black") - s} x={420} y={780} k={kleur.cyaan} />
      <Label tekst="The chips behind the AI boom" van={kw(6, "chips") - s} x={900} y={780} k={kleur.nvidia} />
  </>) },
  // 4 — GELDSTROOM: big tech koopt chips; omzet stroomt naar Nvidia
  { van: s3, tot: s4, el: (s) => (<>
      <Kop nr="NOV 17 · Q3 RESULTS" tekst="Business has never been better" />
      <GeldStroom knoopStart={0} knopen={[
        { id: "nv", naam: "NVIDIA", x: 1300, y: 600, groot: true, sub: "chips", k: kleur.nvidia },
        { id: "a", naam: "Cloud", x: 430, y: 330, sub: "big tech" },
        { id: "b", naam: "AI labs", x: 340, y: 640, sub: "models" },
        { id: "c", naam: "Data centers", x: 560, y: 900, sub: "worldwide" },
      ]} stromen={[
        { van: "a", naar: "nv", start: kw(11, "big", -0.2) - s },
        { van: "b", naar: "nv", start: kw(9, "reported") - s, label: "$115.8B" },
        { van: "c", naar: "nv", start: kw(11, "data") - s },
      ]} />
      <Groot tekst="+103%" van={kw(10, "double", -0.1) - s} x={1560} y={280} maat={110} kleur={kleur.groen} sub="vs. a year ago" />
  </>) },
  // 5 — ISOMETRISCHE WERELD (rood): de verkoop
  { van: s4, tot: s5, el: (s) => (<>
      <IsoWereld rood zakOp={kw(13, "selling") - s} />
      <Kop nr="NOV 20" tekst="Then came the selling" />
      <Label tekst="Reuters: SEC looking at accounting" van={kw(12, "sec") - s} x={120} y={820} k={kleur.rood} />
      <Label tekst="7 days, 7 drops" van={kw(14, "7") - s} x={1300} y={820} k={kleur.rood} />
  </>) },
  // 6 — LEVENDE INFOGRAPHIC: de koers met top en nu, en de vraag
  { van: s5, tot: demoDuur, el: (s) => (<>
      <KoersLijn data={laatste} start={0} duur={40} x={160} y={300} w={1100} h={520} titel="NVIDIA · closing price, US dollars" />
      <Groot tekst="End of the boom?" van={kw(15, "end", -0.2) - s} x={1360} y={360} maat={58} kleur={kleur.rood} />
      <Groot tekst="Or a chance to buy?" van={kw(15, "chance", -0.2) - s} x={1360} y={460} maat={58} kleur={kleur.groen} />
  </>) },
];

export const Demo: React.FC = () => (
  <AbsoluteFill style={{ background: kleur.achter1 }}>
    <Achtergrond />
    {scenes.map((sc, i) => (
      <Sequence key={i} from={sc.van} durationInFrames={sc.tot - sc.van}>
        <Fade duur={sc.tot - sc.van}>{sc.el(sc.van)}</Fade>
      </Sequence>
    ))}
    <Audio src={staticFile("demo/stem.wav")} />
  </AbsoluteFill>
);
