# Visual Explainer Engine (gestart 22 nov 2026)
Script + stem -> filmische uitlegvideo (Remotion 4 + React + Three.js + SVG). Losse map; de bestaande app in de hoofdmap is niet aangeraakt.
- Huisstijl: `src/theme.ts` (donker, cyaan/amber/rood/groen, Segoe UI). Basis-onderdelen: `src/scenes/Basis.tsx` (achtergrond, kop, kinetische tekst, label, fade).
- Scènesoorten (fase 2): `IsoWereld.tsx` (3D isometrisch diorama, lichten uit / rood + zakken), `GeldStroom.tsx` (knooppunten + stromende munten),
  `Infographic.tsx` (KoersLijn met top/nu, DagStaven, TijdLijn).
- Demo: `src/Demo.tsx` (Nvidia, 66 s; scèneplan per kernwoord uit woorden.json van Whisper).
- Renderen (Chrome van de pc, de meegeleverde headless shell geeft EFTYPE op Windows):
  `npx remotion render src/index.ts Demo out/demo-beeld.mp4 --gl=angle --browser-executable="C:/Program Files/Google/Chrome/Application/chrome.exe" --concurrency=3`
  66 s video = ± 2 min renderen. Daarna muziek mixen met ffmpeg.
- Volgende fases: 4 = beoordelen/verbeteren met de eigenaar; 5 = alle 10 scènesoorten + automatisch scèneplan + controles.
