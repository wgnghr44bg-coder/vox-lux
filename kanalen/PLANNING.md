# Planning van alle kanalen (eigenaar 19 nov 2026)

Op de website staat het paneel **Planning alle kanalen**, met deze week en volgende week:
https://wgnghr44bg-coder.github.io/vox-lux/status/
De website wordt elk half uur bijgewerkt door `tools/dashboard_bijwerken.py`, dat `tools/kanalen_planning.py` gebruikt.

## Vaste ritmes

| Kanaal | Hoe vaak | Wanneer (NL) | Sleutel |
|---|---|---|---|
| **Sleep Archives** (@sleeparchiveshistory) | 2x per week | wo en za 21:00 | `YT_REFRESH_TOKEN` |
| **NOIRTRACES** (@noirtraces) | 1x per week | vr 21:00 | `YT_KANAAL=altena` (`~/.yt-altena.json`) |
| **BlackswanVault** (@blackswanvault) | ongeveer 1x per week | werkdag 15:00 (9:00 New York) | `YT_WHATIF_REFRESH_TOKEN` |

Alteraqon (@alteraqon) is gestopt.

## Waar de planning staat

- **Sleep Archives**: in `stories/<map>/planning.txt`, op de regel `datum`.
  - Alleen wo en za. Sinds 19 nov 2026 zijn alle datums omgezet; de oude ma-plekken bestaan niet meer.
  - `tools/routine_lokaal.py`, `tools/keten_bewaker.py` en `tools/hype_wacht.py` gebruiken alleen wo en za.
- **NOIRTRACES en BlackswanVault**: in `kanalen/PLANNING-KANALEN.json`, met per video `kanaal`, `datum`, `tijd`, `titel`, `stand` en `youtube` (het video-id, zodra hij er staat).
  - Wat al op YouTube staat, haalt de website er zelf bij.
  - Gebruik voor `stand` een van: `onderwerp kiezen`, `script klaar`, `wordt gemaakt`, `gepland` of `online`.

## Inspelen op hype

- **Sleep Archives**
  - Feestdagen en jaardagen krijgen de laatste wo- of za-plek op of vóór de dag zelf.
  - De hype-wachter (elke dag om 08:30) laat zien welke slaapvideo's bij grote kanalen nu groeien. Zo'n onderwerp schuift naar voren.
- **NOIRTRACES**
  - Een vaste lijst met bekende zaken.
  - Komt een zaak in het nieuws (nieuwe docu, ontdekking, jaardag), dan schuift die naar de eerstvolgende vrijdag.
- **BlackswanVault**
  - Een kalender met bekende momenten (kwartaalcijfers van grote bedrijven, rentebesluiten, Black Friday, CES).
  - Een nieuwswacht die elke ochtend kijkt.
  - Bij echt groot nieuws (crash, CEO weg, overname, schokkende cijfers): vraag de eigenaar en maak de video binnen 2 tot 3 dagen.
  - Is er geen groot nieuws, dan gaat er een reservevideo online (een tijdloos bedrijfsverhaal).

## Vaste regels

- Altijd eerst **privé** uploaden en via de API controleren dat de video op het goede kanaal staat (`snippet.channelTitle`).
- Openbaar zetten of een publicatietijd instellen mag alleen als de eigenaar het goedvindt.
- Controleer na elke wijziging van de status via de API of het AI-label (`containsSyntheticMedia`) nog aan staat.
- Na elke wijziging: `kanalen/PLANNING-KANALEN.json` en/of `planning.txt` bijwerken en opslaan via `tools/gitveilig.py` (`bewaar`).
