# Overdracht (8 nov 2026, middag) – stem, muziek, opbouw en stand van de video's

Lees eerst CLAUDE.md, audio_engine/README.md, stories/OPBOUW.md en stories/PROMPT-ROUTINE-PC.md.
Praat Nederlands, simpel. Alles gratis/lokaal. Vraag de eigenaar altijd eerst als iets geld kost.

## Vast besloten door de eigenaar (7-8 nov 2026)
- **"B1-stem met achtergrondmuziek"** (kort B1) staat vast in **`audio_engine/B1.json`** (8 nov: één bron, tools/b1.py; een afwijkende stem.json wordt genegeerd met een WAARSCHUWING, behalve met "eigenaar_afwijking"):
  - **Stem**: `narrator-e` (audio_engine/voices/narrator-e, OmniVoice "male, elderly, moderate pitch, british accent",
    seed 27; ontworpen, niemand gekloond), speed 0.54, pauze 1.4, warme klank (EQ in "klank").
    **Niets aan de stem zelf veranderen** (eigenaar 8 nov: "anders is het meteen een robot"): geen rubberband/tempo,
    geen toonhoogte. Rustiger kan alleen met langere pauzes; een lagere OmniVoice-speed maakt deze stem niet trager.
    De rustigere versie (tempo 0.92) is beluisterd en afgewezen: "B1 zoals hij was".
  - **Muziek W3** "diep en donker-warm" (eigenaar 8 nov): "muziek" in B1.json (chord_len 6, fade 3, drone 1.3,
    strings 0.6, choir 0.2, atmosphere 0.3, reverb 0.55/6, lowpass 700, highpass 40), muziek_seed 1939,
    muziek_onder 11 (11 LUFS onder de stem). tools/engine_muziek.py leest dit via tools/b1.py.
- **Opbouw** volgens stories/OPBOUW.md: begin van ± 2 min zonder "Tonight"/"Hello" (opening in de jij-vorm, grote vraag,
  zachte abonneer-zin, reactievraag, settle in), 8-13 onderwerpen (TOPIC + BRIDGE) met feitjes, slot dat uitdooft.
  Script bouwen met tools/bouw_feiten.py (via bouw_script.py). Soort opening en titel afwisselen.
- **Titels**: vraag-titels zonder uren. **Thumbnails: nooit uren** (WW2 had nog "2+ Hours", vervangen door thumbnail-v4).
- Het tweede account schrijft scripts meteen in de nieuwe opbouw (stories/PROMPT-SCRIPT-VOORUIT.md).

## Gereedschap (verbeterd 7-8 nov)
- `tools/engine_stem.py <map>`: afgekapte zinnen (OmniVoice kapt in een groepje van 4 soms een zin af) worden
  automatisch los opnieuw ingesproken. `--hergebruik --opnieuw 8,46,60 --seed-extra 3000` spreekt de zinnen die
  check_stem_tekst meldt opnieuw in (beter dan herstel_zinnen.py als de goede zin niet in het gat past).
- Keten zoals bij WW2: engine_stem -> prep_engine.sh (tekstcontrole) -> zo nodig --opnieuw en opnieuw prep (max 3x)
  -> montage_engine.sh. Een video van ± 2u45 kost ± 12 uur (motion ± 5 uur, 16mm ± 1 uur). Draai lange ketens als los
  proces (Start-Process), niet als achtergrondtaak (die stopt na 2 uur).

## Stand van de video's
- **WW2 (nieuwe versie)**: https://youtu.be/ZZ5JMtF9kuI, **openbaar** sinds 8 nov (eigenaar: "Hij mag wel online"),
  2:42:37, B1 + W3, nieuwe opbouw, thumbnail-v4. Oude versie hVg9nrutQVI verwijderd. Bestanden op de pc opgeruimd.
- **Tombstone (wo 11 nov 21:00)**: keten loopt sinds 8 nov 11:10 (stem -> controles -> montage). Daarna: privé uploaden
  met publishAt 2026-11-11T20:00:00Z, titel "How Did Ordinary People Really Live in Tombstone? | History for Sleep",
  thumbnail-gekozen.jpg, playlist zoals in planning.txt, kanaal controleren, tools/wacht_verwerkt.py, dan pas de oude
  privéversie 4RjjJh-j5a0 verwijderen (OK van de eigenaar) en de grote bestanden opruimen.
- **Egypte (za 14 nov 21:00)**: script klaar in de nieuwe opbouw (92 feitjes, 13 onderwerpen). Daarna zelfde keten,
  titel "What Did People Actually Do When Tutankhamun Was King? | History for Sleep", thumbnail-gekozen.jpg,
  oude privéversie ctC36HRFIac pas na verwerking verwijderen.
- **Gettysburg (wo 18 nov) en verder**: de routine volgt PROMPT-ROUTINE-PC.md (B1 + W3 + OPBOUW.md).

## Wat automatisch op de pc loopt (8 nov 2026, eigenaar: "ik wil alles automatisch en via pc")
- **Routine** (Taakplanner "Sleep Archives routine", zo/di/do 09:00): maakt de volgende video volgens PROMPT-ROUTINE-PC.md
  (ombouwen volgens PROMPT-SCRIPT-PC.md als dat nog niet gebeurd is, b1_check, B1 + W3, controles, upload).
- **Scriptgenerator** (Taakplanner "Sleep Archives scriptgenerator", elke dag 06:00, door de eigenaar aangezet):
  tools/script_generator.ps1 -> stories/PROMPT-SCRIPT-PC.md, één oud script per dag ombouwen, daarna nieuwe schrijven.
  Log: C:\Users\rane\sleep-archives-scripts-log.txt.
- **Keten Tombstone + Egypte** (gestart 8 nov 17:41, tools/keten_tombstone_egypte.ps1, log
  C:\Users\rane\keten-tombstone-egypte.log): Tombstone uploaden en de oude 4RjjJh-j5a0 vervangen
  (tools/vervang_video.py), dan Egypte maken (b1_check, afwisseling, stem, tekstcontrole, montage) en de oude
  ctC36HRFIac vervangen. Wacht als de routine bezig is. Uitslagen ook in stories/ROUTINE-LOG.md.

## Zonder Claude (eigenaar 8 nov 2026: "iets bouwen dat net zo goed is maar dan zonder Claude", "extra controle op verkeerde beelden") – IN TEST
- **Lokale modellen** (gratis, op de pc, via Ollama, C:\Users\rane\AppData\Local\Programs\Ollama): qwen3:14b (tekst) en
  qwen2.5vl:7b (beelden bekijken). Ollama start vanzelf bij het inloggen (http://127.0.0.1:11434).
- **Scriptgenerator lokaal**: python tools/scriptgen/generator.py [--map stories/<map>] [--test]. Volgt het recept van
  PROMPT-SCRIPT-PC.md: eerst oude scripts ombouwen, anders nieuw uit de "Nieuwe planning". Feiten **alleen** uit bronnen
  (Engelse Wikipedia + het oude script, bewaard in <map>/bronnen/), feitencheck per feitje, dezelfde harde controles
  (aantal feitjes/woorden, leesbaar, AFWISSELING GOED). Half werk krijgt status "in-wording" (de routine slaat dat over).
  Een script kost het lokale model een paar uur (draait 's nachts).
- **Dubbele beeldcontrole**: 	ools/beeldcheck.py stories/<map>. (1) Qwen2.5-VL beantwoordt vaste vragen (dingen die er
  toen niet waren, tekst, vervormd, past bij de beschrijving, eng); (2) een getrainde CLIP-detector
  (	ools/beeldcheck_train.py, gewichten tools/beeldcheck_clip.npz) die beelden herkent die lijken op eerder afgekeurde.
  Afgekeurd = opnieuw maken via ComfyUI, na 2 keer de beschrijving herschrijven, na 4 keer stoppen. Overzichtsvellen:
  <map>/beeldcheck-vel-N.jpg, uitslag <map>/beeldcheck.json. Gemeten: de CLIP-detector vangt ± 26% van de eerder
  afgekeurde beelden bij 5% onterecht; de meting van Qwen2.5-VL loopt (tools/beeldcheck_vlmtest.py). Nieuwe afgekeurde
  beelden in <map>/afgekeurd/ zetten en beeldcheck_train.py opnieuw draaien maakt hem beter.
- **Routine lokaal**: python tools/routine_lokaal.py [--plan]: kiest de plek, bouwt zo nodig om, beelden + beeldcontrole,
  thumbnail (gekozen thumbnail houden behalve met uren erop, anders 3 maken en de beste kiezen), b1_check, afwisseling,
  stem, tekstcontrole, montage, QC, upload (tools/vervang_video.py). Bij een fout niets online en status terug.
- **Nog niet omgezet**: de Taakplanner-taken draaien nog met Claude (routine.ps1 en tools/script_generator.ps1).
  Pas omzetten als de eigenaar het testscript (Gettysburg, --test) en de beeldcontrole goed vindt.
