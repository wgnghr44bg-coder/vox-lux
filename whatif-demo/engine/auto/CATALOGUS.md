# Auto-bouwstenen (engine/auto/)

Bouwstenen die voor een verhaal nodig waren en daarna voor elke video beschikbaar blijven.
Gebruik in `scenario.js`: `auto: [{ block: '<naam>', ...opties }]` (opties: zie de eerste regels van het bestand).
Hoe je er een maakt: zie het commentaar bovenin `rain.js`. `make_topic.py` voegt nieuwe blokken hier vanzelf toe.

| block | wat het laat zien | gebruik |
|---|---|---|
| `rain` | regen: vallende druppelstrepen rond de camera, van motregen tot stortbui | `{ block: 'rain', from: 4, full: 20, until: 1e9, strength: 1 }` |
| `floating-cars` | auto's die drijven, langzaam wegdrijven, deinen en kantelen op overstromingswater (gemaakt door Grok, 2026-10-10) | `{ block: 'floating-cars', pos: [[-12, 0, -82], [-3, 0, -95], [8, 0, -73]], from: 0, full: 1, until: 1e9 }` |
| `aurora` | noorderlicht: groene gordijnen met paarse toppen die over de nachtlucht golven; `night: true` maakt het eerst nacht; strength 1.5 = zware zonnestorm (tot boven je hoofd, rood) | `{ block: 'aurora', from: 8, full: 20, strength: 1, az: 0, night: true }` |
| `storm-clouds` | laag, donker, voortrollend wolkendek dat de plek donker en grauw maakt (orkaan, eindeloze regen, onweer; samen met `rain` en `TL.lightning`); strength 1.5 = orkaan | `{ block: 'storm-clouds', from: 2, full: 15, strength: 1, height: 220, wind: [8, -3] }` |
| `tsunami-wave` | vloedgolf: een muur van water met witte kam en schuim die van zee komt, groeit bij de kust en breekt (camera schudt); combineer met water/tide om het land daarna te laten onderlopen | `{ block: 'tsunami-wave', at: 20, arrive: 14, from: [0, -1800], to: [0, 40], height: [12, 35], width: 2600, run: 60 }` |
| `sinkhole` | zinkgat: een rond gat opent in straat of plein, de rand breekt af en valt erin, stof stijgt op, auto's en mensen erboven vallen erin; binnenin aardlagen die in het donker verdwijnen | `{ block: 'sinkhole', pos: [0, 0, -60], at: 12, open: 8, r: 18, depth: 45 }` |
| `second-sun` | tweede zon: felle schijf met gloed die verschijnt of opkomt, met eigen warm licht; lucht wordt lichter en warmer (twee zonnen, een ster die langskomt) | `{ block: 'second-sun', from: 6, full: 14, az: 1.1, el: .35, size: 1, color: 0xffc27a }` |
| `crowd-jump` | iedereen springt tegelijk: alle mensen in de plek zakken door de knieën en springen (± 0,5 m, echte natuurkunde), eventueel een paar keer; met `extra` komt er een menigte bij | `{ block: 'crowd-jump', at: 24, height: .5, count: 1, gap: 2, pos: [0, 0, 10], extra: 60, r: 22 }` |
