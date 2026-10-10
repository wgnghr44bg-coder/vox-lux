# Auto-bouwstenen (engine/auto/)

Bouwstenen die voor een verhaal nodig waren en daarna voor elke video beschikbaar blijven.
Gebruik in `scenario.js`: `auto: [{ block: '<naam>', ...opties }]` (opties: zie de eerste regels van het bestand).
Hoe je er een maakt: zie het commentaar bovenin `rain.js`. `make_topic.py` voegt nieuwe blokken hier vanzelf toe.

| block | wat het laat zien | gebruik |
|---|---|---|
| `rain` | regen: vallende druppelstrepen rond de camera, van motregen tot stortbui | `{ block: 'rain', from: 4, full: 20, until: 1e9, strength: 1 }` |
| `floating-cars` | auto's die drijven, langzaam wegdrijven, deinen en kantelen op overstromingswater (gemaakt door Grok, 2026-10-10) | `{ block: 'floating-cars', pos: [[-12, 0, -82], [-3, 0, -95], [8, 0, -73]], from: 0, full: 1, until: 1e9 }` |
