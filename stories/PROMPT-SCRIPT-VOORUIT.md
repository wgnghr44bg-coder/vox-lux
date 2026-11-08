# Script vooruit schrijven (tweede Claude-account)

De eigenaar wil (1 nov 2026) dat een tweede Claude-account de scripts voor de komende video's alvast maakt. De
pc-routine (`stories/PROMPT-ROUTINE-PC.md`) vindt ze dan op main en maakt er beelden, stem en video van.

**Gebruik:** open Claude Code (web, claude.ai/code, of de desktop-app) met de repo `wgnghr44bg-coder/vox-lux` op
branch `main`, en geef deze opdracht:

> Lees stories/PROMPT-SCRIPT-VOORUIT.md en maak het eerstvolgende script.

## Wat je doet
**Volg precies `stories/PROMPT-SCRIPT-PC.md`** (eigenaar 8 nov 2026: het tweede account doet hetzelfde als de
scriptgenerator op de pc). Dus: eerst het eerstvolgende oude script **ombouwen** naar de nieuwe opbouw, en pas als alles
omgebouwd is een **nieuw** script schrijven; met dezelfde bestanden (src-feiten/begin.txt, deel*.txt, slot.txt,
stijl.txt, bouw_script.py, maak_motion.py, youtube-beschrijving.txt, planning.txt) en dezelfde controles
(AFWISSELING GOED). Zet in de status `tweede account`. Eén script per keer, alleen tekst, niets wat geld kost.

## Wat de routine ermee doet
De routine ziet `status script-klaar (nieuwe opbouw, ...)` en slaat het onderwerp kiezen en het script schrijven over.
Hij leest het script nog één keer na, draait `tools/b1_check.py`, maakt beelden, stem (B1), muziek (W3), montage en
controles, en uploadt op de datum uit `planning.txt`. Daarna zet hij de status op klaar met de YouTube-link.
