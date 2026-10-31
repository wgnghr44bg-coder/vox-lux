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
   **Planning bijsturen op hype (eigenaar, 28 okt 2026)**: neem standaard het onderwerp dat in de
   "Nieuwe planning" in ONDERWERPEN.md op die datum staat. Draai eerst `python tools/sleep_trends.py --days 30`:
   groeit er nu een **wereldberoemd** onderwerp hard bij een groot kanaal (≥ 10.000 views per dag) dat
   nog niet bij ons staat, maak dat dan in plaats van het geplande, en schuif het geplande en de rest
   één plek op in de lijst (commit + push). **Nooit** vervangen of verschuiven: een onderwerp met een
   vaste datum (jubileum, feestdag, filmpremière, bv. Kennedy 21 nov, Pearl Harbor 28 nov, kerst);
   schuif dan de flexibele onderwerpen eromheen. Zet in ROUTINE-LOG.md welke hype je zag en wat je koos.
3. **Datum**: de eerste vrije woensdag of zaterdag 21:00, minstens 2 dagen na vandaag. Zet
   `stories/<map>/planning.txt` meteen op main (commit + push), zodat een volgende run hem ziet.
4. **Maken** volgens stories/PROMPT-NIEUWE-VIDEO.md en stories/YOUTUBE-STANDAARD.md, met deze
   afwijkingen:
   - Script met de opbouw van stories/titanic (OPZET.md daar), ± 2 uur video.
   - Beelden via comfy (`tools/comfy/comfy_batch.py`, tools/comfy/README.md). **Nooit xAI of iets
     anders dat geld kost.**
   - **Stem: Slaap 3** (eigenaar, 31 okt 2026; vervangt George): eigen ontworpen OmniVoice-stem, oudere
     Britse man, heel laag, langzaam met lange pauzes. Altijd met
     `C:\Users\rane\omnivoice-venv\Scripts\python.exe tools/comfy/make_voice_omni.py <map>`
     (de standaardinstellingen zijn goed; het gewone `python` heeft geen omnivoice). Na
     `tools/add_pauses.py --niet-zwaarder <map>` altijd `python tools/zachte_stem.py <map>` en monteer met
     `make_video.py ... --muziek-db -24.6` (ook bij check_video/qc). Meet daarna het volume
     (ffmpeg `ebur128`) en zet hem als laatste stap op -14 LUFS met `python tools/eind_volume.py <video>.mp4 <video>-14.mp4`
     (eigenaar, 31 okt 2026: "net zo hard als de meeste sleep history video's"); upload die versie. Door de lange
     pauzes wordt de video langer: ± 15.000 woorden script geeft ± 2 uur.
   - Pc-paden (test 27 okt 2026): De beelden-workflow is `tools/comfy/zimage_api.json`
     (staat alleen op de pc, niet in git; ontbreekt hij, kijk dan in de hoofdmap van de repo).
   - Titel: bekende naam + maand en jaar + ` | History for Sleep`.
   - Thumbnail: ontwerp v2 (`tools/make_thumbnail.py`, YOUTUBE-STANDAARD.md) zoals
     `stories/titanic/thumbnail-v2.jpg`: **mensen van dat moment** dichtbij in warm licht (rechts of
     in het midden), het onderwerp eromheen; nooit alleen een schip of gebouw. Geen goed beeld met
     mensen in de video? Maak er één extra via comfy (gratis). Bekijk het resultaat zelf.
   - **Abonneer-zin** na de eerste 2-4 zinnen (± 30-60 s), kort en rustig, per video iets anders
     verwoord (PROMPT-NIEUWE-VIDEO.md stap 2); het einde vraagt zoals altijd nog één keer.
   - **Avondeffect v2** (eigenaar, 30 okt 2026): `tools/make_video.py` maakt het beeld standaard iets donkerder
     met zachte donkere randen, kleuren gewoon (geen gele lucht). Niet uitzetten; de thumbnail blijft helder.
     Vraag in de beeldprompts liefst om avondlicht (kampvuur, lamp, schemering).
   - **Geen ondertitels** (eigenaar, 28 okt 2026): niet in beeld en niet als ondertitelbestand op YouTube.
   - Kwaliteitscontrole zoals in de prompt (`tools/qc_video.py`); fouten zelf herstellen.
5. **Uploaden**: privé met publishAt op de geplande tijd naar **Sleep Archives**
   (`YT_REFRESH_TOKEN`, `tools/youtube_upload.py`), met titel, beschrijving, tags en thumbnail.
   Zet hem meteen in de afspeellijsten: `python tools/youtube_playlist.py --soort <soort> <id>`
   (zet hem ook in "Full Documentaries"); hooguit 2 soorten, bv. reizen `reis`, rampen `ramp`,
   oorlog `oorlog`. **Nooit nieuwe afspeellijsten maken** (eigenaar). Controleer dat hij erin staat. Controleer via de API dat `snippet.channelTitle` "Sleep Archives" is; anders
   meteen verwijderen en stoppen.
6. Zet de link en de kosten (€0) in planning.txt, commit en push naar main.
   **Opruimen** (eigenaar, 31 okt 2026: "doe dit zo elke keer"): staat de video gecontroleerd op YouTube
   (juiste kanaal, thumbnail, afspeellijsten), verwijder dan de grote bestanden van die video op de pc:
   alle `*.mp4` en `*.wav` in `stories/<map>/video/` (ook `clips/`). Beelden, script, stem-mp3 en tekstbestanden blijven.
   Vervang je een oude video op YouTube door een nieuwe, verwijder dan ook het oude bestand. Nooit iets anders
   (games, eigen opnames) aanraken.
7. Lukt iets niet (ComfyUI start niet, sleutel ontbreekt, schijf vol), verwijder dan je
   planning.txt van main zodat de volgende run de datum weer kan pakken, en schrijf in
   `stories/ROUTINE-LOG.md` (op main) in simpel Nederlands wat er misging en wat de eigenaar moet doen.
