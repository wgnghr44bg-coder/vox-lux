# Sleep Archives – automatische routine op de pc

De eigenaar wil dat alles automatisch gebeurt (27 okt 2026): **2 video's per week, woensdag en
zaterdag 21:00 NL-tijd**, volgens het Titanic-recept (stories/ONDERWERPEN.md). Deze prompt draait
op de pc van de eigenaar (Windows Taakplanner start `claude -p` op **zondag en donderdag 09:00**),
want ComfyUI, de stem en het videobestand staan alleen daar. Niemand kijkt mee: vraag niets,
werk alles af.

1. `git checkout main && git pull`. Start ComfyUI als `http://127.0.0.1:8188` niet antwoordt en
   wacht tot hij klaar is.
2. **Onderwerp** volgens stap 0 van het Titanic-recept in stories/ONDERWERPEN.md: nooit een
   onderwerp dat al op Sleep Archives staat (`python tools/sleep_trends.py --check ...` toont
   "AL GEMAAKT") of al in een stories/*/planning.txt op main of origin/claude/* staat; kies van de
   rest het onderwerp met de meeste kans (meeste views van bestaande slaapvideo's, of nu hard
   groeiend bij een groot kanaal volgens `python tools/sleep_trends.py`). Is er geen duidelijke
   winnaar, neem dan het eerste vrije onderwerp uit "Eerst deze".
3. **Datum**: de eerste vrije woensdag of zaterdag 21:00, minstens 2 dagen na vandaag. Zet
   `stories/<map>/planning.txt` meteen op main (commit + push), zodat een volgende run hem ziet.
4. **Maken** volgens stories/PROMPT-NIEUWE-VIDEO.md en stories/YOUTUBE-STANDAARD.md, met deze
   afwijkingen:
   - Script met de opbouw van stories/titanic (OPZET.md daar), ± 2 uur video.
   - Beelden via comfy (`tools/comfy/comfy_batch.py`, tools/comfy/README.md) en stem met
     Chatterbox als bm_george, rustig (`tools/comfy/make_voice_local.py`). **Nooit xAI of iets
     anders dat geld kost.**
   - Pc-paden (test 27 okt 2026): de stem altijd met
     `C:\Users\rane\chatterbox-venv\Scripts\python.exe tools/comfy/make_voice_local.py <map>`
     (het gewone `python` heeft geen chatterbox). De beelden-workflow is `tools/comfy/zimage_api.json`
     (staat alleen op de pc, niet in git; ontbreekt hij, kijk dan in de hoofdmap van de repo).
   - Titel: bekende naam + maand en jaar + ` | History for Sleep`; thumbnail in de stijl van
     stories/titanic/thumbnail.jpg.
   - **Geen ondertitels** (eigenaar, 28 okt 2026): niet in beeld en niet als ondertitelbestand op YouTube.
   - Kwaliteitscontrole zoals in de prompt (`tools/qc_video.py`); fouten zelf herstellen.
5. **Uploaden**: privé met publishAt op de geplande tijd naar **Sleep Archives**
   (`YT_REFRESH_TOKEN`, `tools/youtube_upload.py`), met titel, beschrijving, tags, thumbnail en
   afspeellijst. Controleer via de API dat `snippet.channelTitle` "Sleep Archives" is; anders
   meteen verwijderen en stoppen.
6. Zet de link en de kosten (€0) in planning.txt, commit en push naar main.
7. Lukt iets niet (ComfyUI start niet, sleutel ontbreekt, schijf vol), verwijder dan je
   planning.txt van main zodat de volgende run de datum weer kan pakken, en schrijf in
   `stories/ROUTINE-LOG.md` (op main) in simpel Nederlands wat er misging en wat de eigenaar moet doen.
