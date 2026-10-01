# Ochtendcheck: Sleep Archives Cockpit bijwerken

De eigenaar heeft één pagina waar alles op staat:
https://claude.ai/artifact/6cV4o63vPEeYF4JLe1PKFH ("Sleep Archives Cockpit").
De pagina leest haar gegevens uit de database van die artifact (ArtifactData-tool,
`url` = de pagina hierboven). Werk die elke ochtend bij. Niets uploaden of aanpassen op
YouTube; alleen kijken, uitrekenen en de cockpit vullen. Niets betaalds.

1. `git fetch origin` en `python3 tools/dashboard_data.py > /tmp/dash.json`
   (YouTube-cijfers, geplande video's, planning.txt van main en origin/claude/*).
   Werkt de YouTube-token niet: zet dat als eerste taak en als "actie"-advies.
2. Kijk welke video er nu gemaakt wordt: de nieuwste sessie van de routine
   "Sleep Archives video" (list_triggers → last_run.session_id → get_session en
   list_events met kinds ["assistant"]) en de commits op die branch. Vat samen in
   `in_de_maak`: `onderwerp`, `stap` (precies één van: Script, Stem, Afbeeldingen, Video,
   Effecten, Upload, Shorts, Klaar), `toelichting` (1 zin), `live` (bv. "wo 7 okt 21:00"),
   `volgende` (wanneer de volgende video-run start + onderwerp). Loopt er niets: alleen
   `volgende`. Mislukt een run: zeg dat in `toelichting` en maak er een taak van.
3. Schrijf in `/tmp/dash.json` erbij (Nederlands, eenvoudig, korte zinnen):
   - `samenvatting`: één of twee zinnen hoe het kanaal ervoor staat.
   - `advies`: 3-6 punten `{niveau: "goed"|"let-op"|"actie", titel, tekst}` op basis van
     de cijfers (weergaven en kijktijd vs. vorige periode, beste/slechtste video's,
     verkeersbronnen, hoe de nieuwe Shorts-stijl het doet, afwisseling van onderwerpen
     in het schema, groei richting 1.000 abonnees / 4.000 kijkuren). Alleen dingen die
     echt in de cijfers staan; geen verzonnen getallen.
   Schrijf het weg met ArtifactData `set`, collection `cockpit`, doc_id `stand`,
   `file_path` /tmp/dash.json (lees eerst met `get` voor `if_version`).
4. Taken in collection `taken` (doc_id `JJJJ-MM-DD-<kort>`, velden `datum`,
   `volgorde`, `tekst`, `uitleg`, `link` (optioneel), `klaar: false`). Lees eerst de
   bestaande taken (`list`). Maak alleen taken die de eigenaar zelf moet doen, voor
   vandaag en de komende 7 dagen, en alleen als ze er nog niet staan:
   - de dag dat een lange video live gaat: "Na <tijd>: <Short(s)> koppelen aan <video>"
     (Gerelateerde video in Studio) voor elke YouTube-Short van dat onderwerp;
   - TikTok-dagen uit planning.txt (`short1..N`): "TikTok: post <onderwerp> Short <n>
     (<tijd>)" met link naar https://claude.ai/artifact/G4rD4rSmPFCxjZiA5PueXQ;
   - wat een mislukte run of een fout van de eigenaar vraagt (bv. token vernieuwen).
   Verwijder taken die `klaar: true` zijn en ouder dan 7 dagen. Verander nooit
   `klaar` van een taak (dat doet de eigenaar met het vinkje).
5. Kosten in collection `kosten` (doc_id `xai-<map>` of `claude-<session-id>`; velden
   `soort` "xai"|"claude", `datum` JJJJ-MM-DD, `wat`, `bedrag` in dollars, `geschat`
   true/false, bij xAI ook `video` = map). Bestaat het document al, werk het bij
   (`update` met `if_version`).
   - xAI: per video het blok "Kosten" uit `stories/<map>/planning.txt` of
     `VOLGENDE-STAPPEN.md` (main en origin/claude/*). Neem het totaal; staat er "±" of
     "≈", zet `geschat: true`. Een xAI-API voor het echte saldo is er niet; het exacte
     bedrag staat op console.x.ai → Usage.
   - Claude: `list_sessions` (mine, limit 100) en de laatste runs van de routines
     (`list_triggers` → `last_run.session_id` → `get_session`): per sessie over
     vox-lux `usage.cost_usd` (afgerond op 2 decimalen) en de titel. Dit is de waarde in
     API-prijzen; met het abonnement betaalt de eigenaar dit niet apart. Zie je in
     `rate_limit_info` dat `isUsingOverage` true is, maak dan een "actie"-advies.
     Zijn deze tools er niet, sla dit over.
6. Verbeterpunten in collection `verbeterpunten` (velden `impact` hoog|middel|laag,
   `door` "jij"|"claude", `klaar`, `titel`, `tekst`): voeg nieuwe concrete punten toe die
   uit de cijfers volgen (max. 8 open tegelijk), en verwijder punten die al 14 dagen
   `klaar` zijn. Verander nooit `klaar` (dat doet de eigenaar).
7. Geen bericht nodig als alles normaal is. Is er iets dringends (run mislukt, token
   verlopen, video niet gepland), begin je laatste bericht dan met "⚠️" en zeg wat er moet
   gebeuren.
