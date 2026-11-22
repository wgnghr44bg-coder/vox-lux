# Tekenstijl (whiteboard-video's) — stand 22 nov 2026, 02:15

Eigenaar 21-22 nov: getekende video's "zoals The Dividend Experiment / The Swedish Investor". Na ± 20 proeven zei de eigenaar
over de Nvidia-proef: **"zo is het perfect eigenlijk"**. Daarna een langere proef (± 2,6 min) gemaakt.

## Beste voorbeeld (hier op voortbouwen)
- `kanalen/blackswanvault/proef-teken/nvidia3/` — Nvidia, ± 2,6 min, 7 borden. Bouwen: `maak.py` (beeldplan per stukje tekst) →
  `volgorde.py` → `geluid.py` → `teken_anim.py` → mixen (zie onderaan). Script `script.txt`, beelden `prompts.txt` + `afbeeldingen/`,
  echte foto's (`*.jpg`, licentie + fotograaf staat in maak.py en in beeld), logo's `logos/` (Nvidia = echt logo met groen oog, `nvidia.png` liggend).
- Korte proef (1 min, goedgekeurd): `kanalen/blackswanvault/proef-teken/nvidia/` (`maak5.py`).
- Eigenaar wil het kanaal **Alteraqon** (alle oude video's verwijderd 21 nov) misschien ombouwen voor deze getekende video's;
  onderwerpen = hype zoals BlackswanVault (de wachters), taal waarschijnlijk Engels — NOG BEVESTIGEN met de eigenaar.

## Gereedschap (`kanalen/blackswan-nl/proef-teken/`)
- `teken_anim.py scene.json uit.mp4` — tekent alles: tekening (lijnen → kleur), handgeschreven tekst, echte foto die "getekend" binnenkomt
  (`foto`), logo, grafieken (`mooi.py`: lijn met top/laagste, staven, dagstaafjes), pijl, kop linksboven, borden (`borden` + `bord`), zoom (`zoom`).
- `woordtijden.py [en|nl]` (omnivoice-venv) — Whisper woordtijden → `woorden.json`; in maak.py `kw(zin, "woord")` = moment van dat woord.
- `volgorde.py scene.json` — nooit twee dingen tegelijk tekenen, vorige korter maken als de stem verder is, meldt **achterstand op de stem**
  (moet ± 0,0 s zijn) en **overlap** (moet "GEEN overlap" zijn); verlengt de video tot alles af is.
- `geluid.py scene.json teken.wav` — alleen een zachte 'plop' bij logo/grafiek (stiftgeluid standaard UIT).
- Stem: `stem.py` (zakelijk-23, **speed 0.9**, pauzes 0.7/1.2 s) + `check_stem.py` (Whisper, FOUT-lijst; getallen in cijfers zijn geen fout).

## Vaste regels van de eigenaar (allemaal 21-22 nov)
1. **Beeld klopt precies met wat er gezegd wordt**: tekst opdelen in stukjes, per stukje één passend beeld op het woord; past er niets goed bij,
   dan het woord/getal zelf groot schrijven (geen half passend plaatje — "bellen bij Friday" en "verrekijker bij watch" afgekeurd).
2. **Beeld loopt gelijk met de stem** (start 0,3 s vóór het woord, tekenen ± 1,2 s, tekst ± 0,6 s).
3. **Niet te snel, niet te druk**: opbouw zoals The Dividend Experiment: kop linksboven (blauwe hoofdletters + lijntje), "Not financial advice"
   rechtsboven, losse tekeningen over het bord, bord blijft staan tot het volgende hoofdstuk, stilstaande camera, GEEN zoom.
4. **Nooit over elkaar heen / nooit twee tegelijk** (volgorde.py). **GEEN zoom/beweging: getekende beelden staan stil als ze af zijn** (eigenaar 22 nov: "beelden hoeven niet te bewegen als ze getekend zijn") → `"zoom": 0`. Stilstand na het tekenen is dus goed; alleen lange stukken zonder nieuw beeld vermijden.
5. **Geen tekenende hand, geen stiftgeluid, geen vast poppetje in beeld** (F is wel ontworpen en bewaard: `kanalen/personage/personage.md`).
6. **Echte mensen alleen op echte foto's** met vrije licentie (Wikimedia), naam fotograaf + licentie klein onder de foto.
   Getekende/AI-mensen alleen als anonieme figuren. **Echte bedrijfslogo's** (Wikimedia) mogen.
7. AI-tekeningen (ComfyUI Z-Image, prompts in prompts.txt): whiteboard-stijl, wit, geen tekst/cijfers in het beeld (AI maakt nep-tekst:
   kranten met onzinwoorden, kalenders met verkeerde cijfers → niet gebruiken); kaders van "whiteboards" wegknippen.
8. Cijfers alleen uit nagekeken bronnen / slotkoersen; grafieken tonen top en laagste.

## Mixen (voorbeeld)
`ffmpeg -i beeld.mp4 -i stem.wav -stream_loop -1 -i <muziek.wav> -i teken.wav -filter_complex "[2:a]volume=0.07[m];[1:a]apad[v];[3:a]volume=0.55[k];[v][m][k]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -shortest uit.mp4` (**-shortest is nodig**: zonder loopt apad eindeloos door, 22 nov)
Daarna altijd: `ffmpeg -i uit.mp4 -vf freezedetect=n=0.0005:d=1.5 -f null -` en per zin een beeld bekijken (zie maak.py-controle).

## Let op
- Pc heeft weinig geheugen: Sleep-keten (Pearl Harbor) en ComfyUI tegelijk = vastlopen. **Sleep Archives staat STIL sinds 21 nov 23:15
  (taak "Sleep Archives bewaker" Disabled, `~/gpu-bezet.lock`) tot de eigenaar zegt "hervatten"** → dan lock weg + taak Enable + Start.
- Openstaand in de laatste proef: Nvidia-pijl op bord 1 iets naar rechts (`"pijl": [370, 170, 470, 300]`) en opnieuw renderen.

## Kanaal MARKET DOODLE (was Alteraqon; omgebouwd 22 nov 2026, eigenaar koos de naam "Market Doodle")
Token: `YT_REFRESH_TOKEN_ALTERAQON`. Alle oude What-if-video's verwijderd (21 nov). Gezet via API: Engelse beschrijving (`kanalen/alteraqon/beschrijving.txt`),
trefwoorden, taal en, banner `kanalen/alteraqon/banner.png` ("Market Doodle — Money news, drawn on a whiteboard"). Profielfoto `kanalen/alteraqon/profielfoto.png` ("MD" + rode koerslijn), naam "Market Doodle" en handle (bv. @marketdoodle)
zet de eigenaar zelf in Studio — GEDAAN 22 nov: snippet.title = "Market Doodle", handle @marketdoodle (0 video's). Upload altijd privé + kanaal controleren (snippet.channelTitle).

## Snelheid (GEDAAN 22 nov ochtend, eigenaar: "doodle is heel langzaam")
60 s video renderen: was 123 s, nu 19 s (± 6,5x sneller), beeld gelijk. Hoe: (1) per bord een cache-laag van alles wat al af is (klaar_tijd in
teken_anim.py), (2) grafiekkaartjes + schaduw één keer maken (mooi.py), snel verkleinen met reduce, (3) zoom met OpenCV (`pip install
opencv-python-headless`, valt terug op PIL als het er niet is), (4) opslaan met de videokaart (h264_nvenc; `--cpu` = oude libx264).
Een video van 6 min kost nu ± 2 min in plaats van ± 11 min.

## Hype-seintje (22 nov)
Market Doodle gebruikt dezelfde wachters als BlackswanVault (tools/nieuwswacht.py 08:00/15:45, tools/swan_yt_wacht.py 08:10/15:55).
Het telefoon-seintje "Hype: video maken?" (ntfy) noemt nu beide kanalen. Geen aparte wachter nodig.

## Let op Market Doodle video 1 (22 nov)
De al gemaakte video (kanalen/marketdoodle/video1) heeft nog de zoom. In maak.py en maak_short.py staat zoom nu op 0;
GEDAAN 22 nov 05:00: opnieuw gerenderd zonder zoom (lang + Short samen 171 s); oude versies in video1/oud-met-zoom/.
OPEN PUNT: "the biggest stock market debut ever" (scene d + kop "Reason 2: the biggest IPO ever"): SpaceX haalde in juni $86 mld
(CNBC: "a record $86 billion", incl. overtoewijzing; basis $75 mld) en Anthropic $81,34 mld -> eerst nakijken of "grootste ooit" klopt
(bron in bronnen.md regel 14), anders tekst/kop aanpassen ("one of the biggest").

## Planning Market Doodle (eigenaar 22 nov: "market doodle mag net zo snel")
Zelfde dag als BlackswanVault bij groot nieuws (niet een dag later): lange video ± 16:00 NL (10:00 New York) + Short ± 18:00 NL.
Op rustige dagen een tijdloze uitleg-video (bv. "What is a stock buyback?"). Uploaden altijd eerst privé, publiceren na OK eigenaar.
