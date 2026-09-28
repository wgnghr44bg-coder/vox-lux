# Pompeii: The Last Day — overdracht voor een nieuwe sessie

## Wat klaar is
- Script: `pompeii-the-last-day.txt` (1:47:20 audio, stem xAI Lux).
- Audio: `audio/pompeii-deel1..5.mp3` — achter elkaar = de volledige render.
  NIET opnieuw genereren: `tijdlijn.tsv` en `afbeeldingen-tijden.tsv` horen
  precies bij deze render.
- Afbeeldingen: 50 prompts voor Meta AI in `afbeeldingen-prompts.md` en
  `meta-ai-alles-in-een.txt`. Tijden per afbeelding: `afbeeldingen-tijden.tsv`
  (kolommen file, start, end in seconden, slug).
- YouTube-uploader: `tools/youtube_upload.py` (resumable, OAuth refresh token).

## Wat nog moet
1. **Afbeeldingen**: de eigenaar uploadt 50 afbeeldingen in de chat, op
   volgorde, met nummers erbij (bv. "001–010"). Hernoem ze naar
   `001.jpg` … `050.jpg` (schaal/crop naar 1920x1080).
2. **Video**: 1080p 16:9, langzame zoom (Ken Burns) per afbeelding, zachte
   overgang, afbeelding N van `start` tot `end` uit `afbeeldingen-tijden.tsv`,
   audio = deel1..5 aan elkaar. Geen achtergrondmuziek.
   Getest: zoompan 1080p25, libx264 crf 26 ≈ 2,4 MB/min video + AAC ≈ 0,7 MB/min;
   renderen ≈ 35 s per videominuut (4 cores).
3. **Levering**:
   - Voorkeur: **uploaden naar YouTube** met `tools/youtube_upload.py`
     (privé; de eigenaar kiest zelf thumbnail, AI-melding en zet openbaar).
     Titel: `Pompeii: The Last Day | Sleep Documentary`. Stel een rustige
     beschrijving + tags voor.
   - Terugval: video in delen < 30 MB (SendUserFile-limiet), knippen op
     afbeeldingsgrenzen; eigenaar plakt ze in CapCut aan elkaar.

## YouTube-toegang
- Omgevingsvariabelen: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
  (scope youtube.upload). Netwerk: `oauth2.googleapis.com`, `www.googleapis.com`.
- Google-app staat op **Testing**: de refresh token verloopt na 7 dagen.
  Nieuwe token: developers.google.com/oauthplayground → tandwiel → eigen
  credentials → scope `https://www.googleapis.com/auth/youtube.upload` →
  Authorize → Exchange → token in de omgeving vervangen, nieuwe sessie.
- Videos via een niet-geauditeerd API-project blijven privé; eigenaar publiceert.
- Test eerst alleen de token-verversing (geen upload) om te zien of het werkt.

## Afspraken met de eigenaar
- Communicatie in het Nederlands, eenvoudig, telefoon/laptop.
- Nooit sleutels in de chat laten plakken.
- Niets betaalds (xAI-audio) maken zonder akkoord.
