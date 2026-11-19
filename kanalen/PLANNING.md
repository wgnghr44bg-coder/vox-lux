# Planning van alle kanalen (eigenaar 19 nov 2026)

Op de website staat het paneel **Planning alle kanalen**, met deze week en volgende week:
https://wgnghr44bg-coder.github.io/vox-lux/status/
De website wordt elk half uur bijgewerkt door `tools/dashboard_bijwerken.py`, dat `tools/kanalen_planning.py` gebruikt.

## Vaste ritmes

| Kanaal | Hoe vaak | Wanneer (NL) | Sleutel |
|---|---|---|---|
| **Sleep Archives** (@sleeparchiveshistory), **OP PAUZE** (taak bewaker uit) | (straks 1x per week) | za 21:00 | `YT_REFRESH_TOKEN` |
| **NOIRTRACES** (@noirtraces), **OP PAUZE** | (straks 1x per week) | vr 21:00 | `YT_KANAAL=altena` (`~/.yt-altena.json`) |
| **BlackswanVault** (@blackswanvault), **FOCUS** | 2 lange video's per week + Shorts; groot nieuws zo snel mogelijk | werkdag 15:00 (9:00 New York) | `YT_WHATIF_REFRESH_TOKEN` |

Alteraqon (@alteraqon) is gestopt.

## Waar de planning staat

- **Sleep Archives**: in `stories/<map>/planning.txt`, op de regel `datum`.
  - Alleen za (eigenaar 19 nov avond: "focus op swan, elke week 1 video voor sleep en noir"). Alle datums zijn omgezet.
  - `tools/routine_lokaal.py` en `tools/hype_wacht.py` gebruiken alleen za. `tools/keten_bewaker.py` wacht zolang `~/gpu-bezet.lock` bestaat (een keten van een ander kanaal gebruikt de videokaart).
- **NOIRTRACES en BlackswanVault**: in `kanalen/PLANNING-KANALEN.json`, met per video `kanaal`, `datum`, `tijd`, `titel`, `stand` en `youtube` (het video-id, zodra hij er staat).
  - Wat al op YouTube staat, haalt de website er zelf bij.
  - Gebruik voor `stand` een van: `onderwerp kiezen`, `script klaar`, `wordt gemaakt`, `gepland` of `online`.

## Inspelen op hype

- **Sleep Archives**
  - Feestdagen en jaardagen krijgen de laatste za-plek op of vóór de dag zelf.
  - De hype-wachter (elke dag om 08:30) laat zien welke slaapvideo's bij grote kanalen nu groeien. Zo'n onderwerp schuift naar voren.
- **NOIRTRACES**
  - Eerst de bekendste zaken (eigenaar 19 nov). De volgorde staat in `kanalen/PLANNING-KANALEN.json` onder `noir_volgorde`.
  - Komt een zaak in het nieuws (nieuwe docu, ontdekking, jaardag), dan schuift die naar de eerstvolgende vrijdag.
- **BlackswanVault**
  - Een kalender met bekende momenten (kwartaalcijfers van grote bedrijven, rentebesluiten, Black Friday, CES).
  - Een nieuwswacht: `tools/nieuwswacht.py` (Taakplanner "BlackswanVault nieuwswacht", 08:00 en 15:45). Hij leest koersen en de koppen van CNBC, MarketWatch, BBC en NYT, schrijft `stories/nieuws.json` (paneel op de website) en geeft bij GROOT een seintje in `stories/ROUTINE-LOG.md`.
  - Bij echt groot nieuws (crash, CEO weg, overname, schokkende cijfers): vraag de eigenaar en maak de video binnen 2 tot 3 dagen.
  - Is er geen groot nieuws, dan gaat er een reservevideo online (een tijdloos bedrijfsverhaal).

## Vaste regels

- Altijd eerst **privé** uploaden en via de API controleren dat de video op het goede kanaal staat (`snippet.channelTitle`).
- Openbaar zetten of een publicatietijd instellen mag alleen als de eigenaar het goedvindt.
- Controleer na elke wijziging van de status via de API of het AI-label (`containsSyntheticMedia`) nog aan staat.
- Na elke wijziging: `kanalen/PLANNING-KANALEN.json` en/of `planning.txt` bijwerken en opslaan via `tools/gitveilig.py` (`bewaar`).

## BlackswanVault: kwaliteit (eigenaar 19 nov avond, na de Nvidia-video)
- Geen schokkerige of onscherpe video's op de achtergrond. Gebruik een scherpe echte foto, of een goede AI-foto die past bij de tekst. Een echte video mag alleen als die er professioneel uitziet.
- Niets twee keer vertellen: hetzelfde bedrag of feit maar één keer uitspreken (in de Nvidia-video kwam de omzet van $115,8 miljard twee keer voor).
- Opsommingen rustig: elk item een eigen korte zin (eigen regel in script.txt), met 0,6 s pauze erna, en elk item apart in beeld (eigenaar 19 nov avond).
