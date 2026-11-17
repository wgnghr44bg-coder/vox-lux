# Bodycam-kanaal (NL) – plan (eigenaar 17 nov 2026)

Kanaal met Amerikaanse incidenten en eigen ENGELSE voice-over (eerst NL bedacht; 17 nov Engels). Vaste vorm: 1 incident, 10-15 min, met verhaal
(voice-over, tijdlijn, uitleg). Eerst 5-10 video's maken, dan beoordelen. Sleep Archives staat hiervoor even stil.

## Bronnen (vrij te gebruiken)
1. **DVIDS** (dvidshub.net, zoek "body worn camera") – CBP-video's = federale overheid = public domain.
2. **CBP** – cbp.gov/newsroom/accountability-and-transparency/body-worn-camera-video-releases – public domain.
3. **Wikimedia Commons** – licentie per video checken (sjabloon onderaan de bestandspagina).

### LAPD op Commons (gecontroleerd 17 nov 2026 via de Commons-API)
Licentie **PD-CAGov-LAPD**: werk van LAPD-personeel in dienst is in de VS public domain (Californië verbiedt
copyright op public records; County of Santa Clara v. CFAC). **Let op:** geldt NIET voor beelden van derden in de
video (winkelcamera's, omstanders, nieuwszenders) – die stukken weglaten of apart nagaan.

| video op Commons | duur | licentie |
|---|---|---|
| Bodycam Footage Shows Police Shootout in Los Angeles, California (Trader Joe's Silver Lake, 2018) | 5:10 | PD-CAGov-LAPD |
| LAPD Cop Shoots Man Brandishing a Toy Airsoft Rifle Outside His Home (Luis Herrera, 17 sep 2022) | 10:39 | Public domain |
| Bodycam Footage Of Shooting That Left Suspect And Hostage Dead in Los Angeles (Van Nuys) | 2:42 | Public domain |
| 2 - OIS in Hollenbeck with gang suspect | 2:45 | Public domain |
| Suspect Sets Fire to Front of LAPD Central Community Police Station | 1:21 | PD-CCTV (in review) |

Nog na te kijken: North Hollywood ICD 7-27-2024 (NRF039-24), Southeast OIS 10-14-2020 (NRF046-20), NRF047-18,
Richard Mendoza (dashcam + 2 bodycams), Encino Home Invasion NR21315dm.

## Zoeken naar nieuwe video's
`python kanalen/bodycam/zoek_vrije_videos.py` (opties: `--zoek "police chase,pursuit"`, `--bronnen commons,cbp`,
`--aantal 30`) → `kanalen/bodycam/nieuwe-videos.md`, NIEUW = nog niet eerder gezien (`gezien.json`).
MAG = licentie in orde (maker is een overheid); LET OP = zelf nakijken (mediakanaal, uploader, BY-SA, niet gecontroleerd).
Gratis API-sleutels maken meer bronnen mogelijk: `DVIDS_API_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`.

## Niet gebruiken
- Illinois State Police, Anchorage PD (© auteursrecht), video's van andere YouTube-kanalen.
- Niet van YouTube downloaden; Commons-bestand of origineel bij het korps.

## Regels
- Altijd iets eigens: NL voice-over, uitleg, tijdlijn, kaart (anders "reused content", geen geld).
- Bronvermelding in de beschrijving, bv. "Beelden: LAPD – public domain (PD-CAGov-LAPD) – <Commons-link>".
- Screenshot van de licentie bewaren als bewijs (`kanalen/bodycam/<video>/licentie.png`).
- Gezichten van omstanders vervagen, geen vernederende beelden; heftigste moment inkorten of vervagen
  (YouTube-regels voor geweld: anders leeftijdsgrens / beperkte advertenties).
- Uitleg vooraan in de video, niet alleen beelden.

## Werkwijze per video (gratis, alles lokaal)
1. Incident kiezen, licentie checken + screenshot.
2. Feiten verzamelen (persbericht LAPD, nieuws) → Engels script, 10-15 min.
3. Stem: eigen stem via OmniVoice (Engels, speed 1.0): `maak_voiceover.py`.
4. Montage met ffmpeg: beelden + voice-over + tijdlijn/kaart, gezichten vervagen.
5. Bronvermelding + upload op een NIEUW kanaal (eigen refresh token).

## Overdracht / stand (17 nov 2026, avond) – voor elk Claude-account
Begin hier: lees dit bestand. Sleep Archives staat even stil voor bodycam (eigenaar 17 nov).
Taal: **Engelse voice-over** (eigenaar, 17 nov: eigen Engelse voice-over, eigen verhaal, context, eigen montage en
hoofdstukken; niet zomaar complete bodycamvideo's opnieuw uploaden — anders "reused content").
Stem: de eigen stem van de eigenaar (`eigen-stem`, OmniVoice), **speed 1.0**, klank uit B1.json, zonder muziek of haard.
Het stembestand staat alleen op de pc (`C:\Users\rane\vox-lux-stemmen\eigen-stem\ref.wav`): de stem maken kan dus alleen
op de pc, niet in de cloud.

### Video 1: `videos/traderjoes-2018/` (LAPD, Trader Joe's Silver Lake, 21 juli 2018)
- [x] Licentie: PD-CAGov-LAPD (zie bronvermelding.txt). Bron: Commons-bestand "Bodycam Footage Shows Police Shootout
      in Los Angeles, California.webm" (5:10, 102 MB).
- [x] `script.txt`: Engels, feiten nagekeken (Wikipedia, NPR, FOX 11 juni + okt 2026, ABC7); onbewezen zinnen eruit.
- [ ] Bronvideo downloaden naar `bron/bron.webm` (17 nov: Wikimedia gaf 429 "too many requests" voor het IP van de pc,
      na veel API-verzoeken. NIET omzeilen met een nep-browser; later opnieuw of de eigenaar downloadt in de browser).
- [ ] Beelden bekijken (frames + Whisper op het geluid), `[BEELD …]`-regels in script.txt afstemmen.
- [ ] Stem: `C:/Users/rane/omnivoice-venv/Scripts/python.exe kanalen/bodycam/maak_voiceover.py kanalen/bodycam/videos/traderjoes-2018`
      — alleen als de GPU vrij is (ComfyUI/Sleep Archives-keten gaat voor, 8 GB kaart).
- [ ] Montage (ffmpeg): stem op de juiste momenten, bodycam-geluid zachter onder de stem (ducking), heftigste moment
      inkorten, gezichten omstanders vervagen, kaart/tekstbeelden, hoofdstukken. Proef naar de eigenaar (telefoon).
- [ ] Nieuw YouTube-kanaal + eigen refresh token: pas bij uploaden, en alleen na akkoord van de eigenaar.
