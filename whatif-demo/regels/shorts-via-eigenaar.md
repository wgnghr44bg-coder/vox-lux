# Shorts gaan via de eigenaar (eigenaar, 7 okt 2026)

Geldt alleen voor Shorts. Lange video's (16:9) uploadt en plant de routine zelf, zoals in AUTOMATISCH.md.

1. Maak de Short zoals altijd (stijl A/B volgens `stijl-afwisseling.md`), maar ZONDER ingebrande ondertitels:
   bouw niet met `--subs` en sla de ondertitel-controle over. De eigenaar zet de ondertitels zelf in TikTok.
   Wel `tools/check_video.py` (beeld/geluid) draaien: alleen bij "CONTROLE GOED" doorgeven.
2. NIET naar YouTube uploaden (ook niet privé). Dus niet `publish_whatif.py` voor de upload gebruiken;
   alleen de controle en de TikTok-tekst klaarzetten.
3. Geef de Short aan de eigenaar:
   - stuur het mp4-bestand in de sessie (SendUserFile, display "attach"), met de TikTok-tekst (`tiktok` uit upload.json) erbij;
   - en zet hem op de pagina "IfScape3D TikToks" zodra die bestaat (video, tekst + kopieerknop, downloadknop).
   - Zet in de melding: titel, stijl (A/B), en "klaar voor TikTok – stuur hem met ondertitels terug, dan zet ik hem op YouTube".
4. `onderwerpen.md`: status "klaar <datum>, bij eigenaar (TikTok)". De "live"-datum uit de planning vervalt voor Shorts:
   de Short gaat live op YouTube als de eigenaar hem terugstuurt.
5. Stuurt de eigenaar de ondertitelde Short terug: upload volgens `eigen-upload.md` (precies dat bestand, openbaar,
   playlist "What If"), titel/beschrijving/tags uit `upload.json`, en zet de stijl in de USAGE.md-log.
