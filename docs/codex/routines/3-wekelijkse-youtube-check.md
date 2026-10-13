# Routine: Wekelijkse YouTube-check (beide kanalen)
Vroeger bij Claude: maandag 17:52 (Europe/Amsterdam). Staat nu UIT.

```text
WEKELIJKSE KORTE YOUTUBE-CHECK voor Sleep Archives en IfScape3D. Zo zuinig mogelijk: geen web-zoekopdrachten, geen concurrentie-onderzoek, lees alleen wat hieronder staat.

REGELS
- Alleen lezen: upload, plan of wijzig niets op YouTube, commit/push niets, koop niets, tot ik uitdrukkelijk "ja" zeg op een voorstel.
- Laat nooit tokens/keys zien en vraag er nooit om (staan in de omgeving).
- Geen verzonnen cijfers; ontbrekende data noemen. < 100 weergaven = "te vroeg om te zeggen".

STAPPEN
1. Repo wgnghr44bg-coder/vox-lux: git fetch origin && git checkout main && git pull origin main
2. BUDGET: lees USAGE.md (nieuwste: git show origin/claude/whatif-machine:USAGE.md, anders die op main). Is het weekbudget voor meer dan 85% op, doe dan alleen stap 3–4 en geef alleen de getallen.
3. Data (lees de JSON met een klein python-scriptje, print alleen wat nodig is):
   python3 tools/dashboard_data.py > /tmp/sleep.json ; python3 tools/youtube_reach.py --json > /tmp/sleep-reach.json
   YT_REFRESH_TOKEN="$YT_WHATIF_REFRESH_TOKEN" python3 tools/dashboard_data.py > /tmp/3d.json ; YT_REFRESH_TOKEN="$YT_WHATIF_REFRESH_TOKEN" python3 tools/youtube_reach.py --json > /tmp/3d-reach.json
4. Per kanaal: laatste 7 dagen vs 7 dagen daarvoor (sleutel growth): weergaven, kijkminuten, abonnees. Nieuwe video's van deze week (weergaven, gem. kijkduur, vertoningen, klikfrequentie, grootste bron). Stand richting 1.000 abonnees / 4.000 uur (watch_hours_12m).
   IfScape3D STIJLTEST (sinds 7 okt 2026): Shorts wisselen om en om stijl A (POV) en B (gravity-stijl); welke Short welke stijl heeft staat in de log van USAGE.md op origin/claude/whatif-machine (gravity-doubled en sun-closer = B, earth-stopped en deep-freeze = A). Vergelijk per stijl: aantal, gem. weergaven, gem. kijkduur en kijkpercentage. Pas een conclusie bij ≥ 3 Shorts per stijl met elk ≥ 100 weergaven.
5. Logboek: git show origin/claude/youtube-log:stories/WIJZIGINGEN-LOG.md. Voor elke wijziging ≥ 7 dagen oud zonder effect: vergelijk vertoningen/klikfrequentie/weergaven per dag vóór en na.
6. Lees stories/YOUTUBE-STANDAARD.md alleen bij een titel- of thumbnailvoorstel.

ANTWOORD (Nederlands, max. ± 25 regels)
## Sleep Archives 🟢/🟡/🔴 – deze week vs vorige week (3 getallen) · beste en slechtste video · 1 opvallend ding
## IfScape3D 🟢/🟡/🔴 – zelfde, plus 1 regel stijltest A vs B
## Effect eerdere wijzigingen – per wijziging: beter/slechter/te vroeg
## Voorstellen (max. 3) – genummerd: wat, welk kanaal/video, waarom, kost geld ja/nee. Vraag: "Welke nummers zal ik doorvoeren?"
Niets bijzonders: "Alles normaal, geen actie nodig" met de getallen.

NA MIJN AKKOORD: volg stories/YOUTUBE-STANDAARD.md; nooit opnieuw uploaden of verwijderen. Titel: videos.update met alleen snippet (description/tags/categoryId ongewijzigd meenemen). Thumbnail: set_thumbnail uit tools/youtube_upload.py; 403 → stuur mij het bestand. Log elke wijziging in stories/WIJZIGINGEN-LOG.md op branch claude/youtube-log (git checkout -B claude/youtube-log origin/claude/youtube-log, commit, push). Andere repo-wijzigingen via een eigen branch + pull request naar main.
```
