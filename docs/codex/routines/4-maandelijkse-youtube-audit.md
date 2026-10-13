# Routine: Maandelijkse YouTube-audit (beide kanalen)
Vroeger bij Claude: elke 8e van de maand 17:52 (Europe/Amsterdam). Staat nu UIT.

```text
YOUTUBE-AUDIT (maandelijks) van mijn 2 kanalen: IfScape3D (What If / 3D / science) en Sleep Archives (history for sleep / dark history / relaxing documentaries). Ik wil weten wat goed gaat, wat niet, en wat ik concreet moet aanpassen.

BELANGRIJK
- ALLEEN LEZEN: upload, plan of wijzig niets op YouTube, commit of push niets, tot ik na het rapport uitdrukkelijk "ja" zeg op een voorstel.
- Koop niets en gebruik geen betaalde diensten (xAI e.d.) zonder mijn akkoord.
- Laat nooit tokens/keys zien en vraag mij er nooit om; ze staan al in de omgeving.
- Geen verzonnen cijfers. Ontbrekende data aangeven. Interpretaties labelen als "interpretatie". Bij elke conclusie: op hoeveel video's/weergaven die rust; < 100 weergaven = "te vroeg om te zeggen".
- BUDGET: lees eerst USAGE.md (git show origin/claude/whatif-machine:USAGE.md, anders die op main). Boven 85%: sla stap 4 over en houd het kort.

1. PROJECT: repo wgnghr44bg-coder/vox-lux, git fetch origin && git checkout main && git pull origin main. Lees indien relevant: stories/YOUTUBE-STANDAARD.md, stories/ONDERWERPEN.md, het logboek (git show origin/claude/youtube-log:stories/WIJZIGINGEN-LOG.md), en van origin/claude/whatif-machine: whatif-demo/AUTOMATISCH.md en whatif-demo/onderwerpen.md.
   Raad nooit aan een video opnieuw te uploaden. Het logboek is leidend voor wat al gedaan is.
2. KANAALDATA
   - Sleep Archives: python3 tools/dashboard_data.py > /tmp/sleep.json en python3 tools/youtube_reach.py --json > /tmp/sleep-reach.json
   - IfScape3D: dezelfde commando's met YT_REFRESH_TOKEN="$YT_WHATIF_REFRESH_TOKEN" ervoor (→ /tmp/3d.json, /tmp/3d-reach.json)
   Analyseer per kanaal: weergaven, kijktijd, abonnees, groei, vertoningen/CTR, gem. kijkduur en kijkpercentage, verkeersbronnen, Shorts vs lange video's, effect van de wijzigingen in het logboek.
3. VIDEO'S: rangschik per kanaal van best naar slechtst (>10: top 5 en onderste 5) met metrics en waarom (interpretatie). "Welk patroon hebben mijn beste video's gemeen?"
4. NICHE-CHECK (klein): alleen openbare cijfers via YouTube Data API (search.list + videos.list). Max. 5 video's per niche, met bron. Niet raden naar CTR van anderen. "Wat doen succesvolle video's beter dan mijn kanaal?"
5. VERBETERINGEN per kanaal: top 5 verbeteringen, 5 video-ideeën, 3 titelverbeteringen, 3 thumbnailverbeteringen.
6. MONETIZATION per kanaal: abonnees, kijkuren lange video's 12 mnd (watch_hours_12m), afstand tot 1.000 abonnees en 4.000 uur. IfScape3D ook Shorts-route (10 mln Shorts-weergaven in 90 dagen). Geen voorspellingen.
7. EINDRAPPORT (Nederlands, kort): # YOUTUBE AUDIT / ## IFSCAPE3D (status, goed, slecht, beste video, grootste probleem, grootste kans, top 3 acties) / ## SLEEP ARCHIVES / ## VERGELIJKING / ## NICHE / ## PRIORITEIT (5 acties). Sluit af met: "Als ik de komende 30 dagen maar 3 dingen mag veranderen, zijn dit de 3 dingen."
8. AANPASSEN (alleen na akkoord): genummerde lijst "Voorstellen om door te voeren" (wat, kanaal/video, kost geld ja/nee) en vraag "Welke nummers zal ik doorvoeren?". Uitvoeren zoals bij de wekelijkse check (videos.update alleen snippet, set_thumbnail, log op claude/youtube-log).
```
