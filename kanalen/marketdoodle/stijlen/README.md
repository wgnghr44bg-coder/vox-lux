# Market Doodle: twee vaste stijlen (eigenaar 28 nov 2026)

De eigenaar vroeg: "kun je zowel de 3D style die online staat opslaan als 3D en deze opslaan als 2D".
Zegt de eigenaar **"3D"**, gebruik dan de 3D-stijl. Zegt hij **"2D"** (of niets), gebruik dan de 2D-stijl, die is de standaard.

Voor beide stijlen gelden dezelfde vaste regels:
- Shortregels: "What if" in de eerste seconde, 35-45 s, loop.
- Alle controles moeten 0 fouten geven.
- Verhaal: snelle grappen zoals de GTA-short, niet steeds "Day 1 / Day 2".

## 3D: de haai die online staat
Online: YouTube https://youtu.be/VQ2RD_kv_ZQ ("What If You Built A Shark That Can Walk?") en TikTok.
Voorbeeldvideo: `D:/marketdoodle-stijlen/3d-voorbeeld-haai.mp4`.

**Hoe het eruitziet:**
- Platte "bean-head" cartoonfiguren als kaartjes, met inktranden.
- Een geschilderde 3D-wereld met zwarte inktlijnen, felle lucht en wazige achtergronden.
- Een zwevende camera die meebeweegt.
- Lipsync per klank.

**Bron:**
- `stijlen/3d/bron/`: momentopname van git-commit `628eb8c4` (haai-map + `bridge/toon.ts`).
- Het project zelf staat in `studio3d/cartoon3d`. Het draait op Remotion + three.js, met de bouwstenen in `src/videos/bridge`, uit de skill cartoon-3d-short.

**Renderen:**
- Gebruik Edge.
- Draai met `--concurrency=1` en `--timeout=180000` (Kenney-modellen laden langzaam).

**Controles:**
- `scripts/wachter3d*.ts` + `scripts/controle3d*.py`.
- Moeten 0 fouten geven.

**Let op:**
- Camera niet te dichtbij. De eigenaar vond de ingezoomde robotbutler "niet leuk om naar te kijken".
- Kies medium-wijde shots met een vlakke camerahoek.

## 2D: de oude pop_short-stijl (standaard)
Voorbeeldvideo: `D:/marketdoodle-stijlen/2d-voorbeeld-haai.mp4`.
Bewezen: ± 1.200-1.500 weergaven per short.

**Hoe het eruitziet:**
- De vaste poppetjes uit `proef-pop-short/pop_short.py` (you, dad, mom, sis, ...), met gebaren en naamlabels.
- Lipsync en gele ondertitels.
- Een vlakke cartoonachtergrond van ComfyUI (gratis, prompts in `prompts.txt`).
- Losse plaatjes op witte achtergrond (`sprites/`).
- Plaatskaarten en grote koppen (bijvoorbeeld "TAXES +300%").

**Sjabloon:**
- `short-helden/maak_short.py`, met als bovenkant/onderkant het generieke deel van `short-haai/maak_short.py`.
- Werkwijze:
  - `script.txt` → `stem.py` → `woordtijden.py` → `tools/stemtempo.py` → `tools/tempowachter.py`.
  - Daarna ComfyUI (`tools/comfy/comfy_batch.py ... --short`).
  - Maat van nieuwe achtergronden in `achtergronden.json` zetten.
  - Tot slot `maak_short.py --plaat` / `--tekst` / volledig.

**Controles (in maak_short.py):**
- shortregels
- tekstwachter
- scènewachter
- LAYOUT
- geluidcheck
- tempowachter
- luidheid
- TEKSTCONTROLE.jpg zelf nalopen.
