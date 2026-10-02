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
   - de `yt-short`-dag uit planning.txt: "YouTube: upload Short <titel> (<tijd>)" met link
     naar https://claude.ai/artifact/G4rD4rSmPFCxjZiA5PueXQ (kaart "Voor YouTube"; de eigenaar
     uploadt die zelf, met de lange video als Gerelateerde video);
   - TikTok-dagen uit planning.txt (`short1..N`): "TikTok: post <onderwerp> Short <n>
     (<tijd>)" met link naar https://claude.ai/artifact/G4rD4rSmPFCxjZiA5PueXQ;
   - wat een mislukte run of een fout van de eigenaar vraagt (bv. token vernieuwen);
   - open verbeterpunten met hoog effect die de eigenaar zelf moet doen.
   Geen taken voor kleine dingen (ondertitels, community-posts e.d.).
   Verwijder taken die `klaar: true` zijn en ouder dan 7 dagen. Verander nooit
   `klaar` van een taak (dat doet de eigenaar met het vinkje).
5. Kosten. `cockpit/kosten` bevat de laatste echte stand van console.x.ai
   (`bijgewerkt`, `xai_saldo`, `xai_30d`, `xai_per_video`) en het Claude-abonnement
   (`claude_eur`, vast €22 per maand; Claude-gebruik NIET als kosten tonen). Zet alleen
   voor video's die NA `bijgewerkt` gemaakt zijn een document in collection `kosten`
   (doc_id `xai-<map>`; velden `soort` "xai", `datum` JJJJ-MM-DD, `wat`, `bedrag` in
   dollars, `geschat` true/false, `video` = map), met het totaal uit het blok "Kosten"
   van die video (planning.txt of VOLGENDE-STAPPEN.md, main en origin/claude/*). De
   pagina rekent zelf het resterende tegoed uit. Is dat geschatte tegoed lager dan
   3 × `xai_per_video`, maak dan een verbeterpunt (hoog) en een taak "xAI-tegoed
   aanvullen" en begin je laatste bericht met "⚠️". Een xAI-API voor het saldo is er
   niet; vraag de eigenaar in het advies af en toe om een nieuwe screenshot van
   console.x.ai als `bijgewerkt` ouder is dan 14 dagen.
6. Verbeterpunten in collection `verbeterpunten` — ALLEEN punten met hoog effect (de
   eigenaar wil geen kleine dingen; middel/laag niet tonen, ook niet als taak). Velden `impact` "hoog",
   `door` "jij"|"claude", `klaar`, `titel`, `tekst`): voeg nieuwe concrete punten toe die
   uit de cijfers volgen (max. 5 open tegelijk), en verwijder punten die al 14 dagen
   `klaar` zijn. Verander nooit `klaar` (dat doet de eigenaar).
7. Stijlcontrole van geplande lange video's (uit `youtube_schedule` in /tmp/dash.json):
   eindigt de titel niet op "| History for Sleep", staat er "Sleep Documentary" in, of
   ontbreekt `stories/<map>/thumbnail-v2.jpg` (main en origin/claude/*) voor dat
   onderwerp, maak dan een "actie"-advies en begin je laatste bericht met "⚠️" zodat de
   eigenaar het in de centrale sessie laat rechtzetten. Zelf niets op YouTube veranderen.
8. TikTok-controle: staan er in planning.txt `shortN`-regels (TikTok-datums) voor de
   komende 7 dagen waarvoor op https://claude.ai/artifact/G4rD4rSmPFCxjZiA5PueXQ (ArtifactData
   `list`, collection `tiktoks`) geen document met die datum en een `video_url` staat? Maak
   dan een "actie"-advies en begin je laatste bericht met "⚠️ TikToks ontbreken".
9. Geen bericht nodig als alles normaal is. Is er iets dringends (run mislukt, token
   verlopen, video niet gepland), begin je laatste bericht dan met "⚠️" en zeg wat er moet
   gebeuren.
