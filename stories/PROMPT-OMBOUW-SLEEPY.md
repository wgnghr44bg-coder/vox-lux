# Scripts ombouwen naar de opbouw van Sleepy History (eigenaar 12 nov 2026)

Start: "Lees stories/PROMPT-OMBOUW-SLEEPY.md en voer het uit voor <map>". Werk af zonder te vragen.
**Alleen tekst**: geen beelden, geen stem, geen video, niets wat geld kost. Eén map per keer, alleen jouw map aanraken.

## Verdeling (zodat niemand elkaars werk overschrijft)
- **Tweede account**: `thanksgiving-1621` (wo 25 nov), `pearl-harbor-1941` (za 28 nov), `boeren-winter-1300` (wo 2 dec).
- Hoofdsessie op de pc: babylon (klaar), crisis-1933, gettysburg-1863, dallas-1963, egypte-toetanchamon en de rest.

## 0. Begin
`git checkout main && git pull`. Lees CLAUDE.md en **stories/OPBOUW.md** (bovenaan: "Nieuwe opbouw sinds 12 nov 2026").
Voorbeeld van een omgebouwd script: `stories/babylon-600-vc/src-feiten/` (commit 11d9f96a).

## 1. Wat er moet gebeuren in `stories/<map>/src-feiten/`
De oude "nieuwe toon" van 11 nov is vervallen. Het script moet klinken als een **kalme gids**, zoals de Sleepy History
Channel ("What Was Medicine Like in Ancient Times?"). Neem hun opbouw en manier van vertellen over, **nooit hun zinnen**.

**Blokken (deel1-3.txt)**: elk blok `IMG / HEAD / BODY`.
- **IMG- en TOPIC-regels blijven precies gelijk** (de beelden bestaan al of worden daarop gemaakt). TOPIC = thema.
- **BRIDGE-regels weg** (geen overgangszinnen meer).
- **HEAD**: één feit als gewone uitspraak, verleden tijd ("Farm wives often earned the only steady cash from eggs.").
- **BODY** (± 170-230 woorden), vaste volgorde: openingszin die het feit in andere woorden herhaalt -> uitleg -> iets
  concreets of een bewijs (vondst, brief, dagboek, cijfer, "historians", "archaeologists") -> nuance ("Yet…",
  "Even so…") -> rustige slotgedachte (wat het zegt over de mensen van toen, vaak de brug naar nu).
- **Elk blok staat op zichzelf**: geen "later", "remember this", "as we saw", geen verzonnen hoofdpersonen of
  familie die door het hele script loopt (echte historische personen mogen wel).
- **Geen jij-vorm** ("you'd", "imagine you", "picture yourself"), **geen vragen aan de luisteraar**, **geen "I"**,
  geen "you might think". Verleden tijd, korte gewone zinnen (gem. 10-14 woorden), elk feit één keer per blok.
- Alleen feiten die kloppen; bij twijfel weglaten of "according to…" zeggen.

**begin.txt (80-160 woorden, eigenaar: kort)**: 4-6 zinnen over het onderwerp, één zin abonneren (anders verwoord
dan in andere video's), 2-3 heel korte ontspanzinnen, "Let's begin." Geen "Tonight/Hello/Welcome" aan het begin.
**slot.txt (80-170 woorden)**: 2-3 zinnen terugblik, het beeld dooft uit, "no need to remember", één zin met
"another ... story/journey/video ... on the screen", kort abonneren, ademen, als laatste "Sleep well, and good night."

Hulp: `python tools/ombouw_blokken.py lijst stories/<map>` toont blokken met jij-vorm/vragen/verwijzingen.
`python tools/ombouw_blokken.py vervang stories/<map> nieuw.json` zet nieuwe tekst per IMG-slug
(`{"<slug>": {"head": "...", "body": "..."}}`) en haalt alle BRIDGE-regels weg. In de meeste scripts moet vrijwel
elk blok herschreven worden.

## 2. Controles (allemaal verplicht)
```
python tools/script_leesbaar.py stories/<map>          # moet MAKKELIJK of GOED en "TOON GOED" geven
python tools/check_afwisseling.py stories/<map>        # AFWISSELING GOED (anders begin/slot anders verwoorden)
python tools/script_check.py stories/<map> --zonder-model   # SCRIPT GOED
python stories/<map>/bouw_script.py                    # bouwt script-cues.txt opnieuw
```
`prompts.txt` niet meecommitten als alleen de stijlregel verschuift (`git checkout -- stories/<map>/prompts.txt`).

## 3. Afronden
In planning.txt de regel `status` laten staan, maar achter "nieuwe opbouw" toevoegen: `, opbouw Sleepy 12 nov`.
Commit alleen `stories/<map>/` met als boodschap `<map>: omgebouwd naar opbouw Sleepy History (SCRIPT GOED, TOON GOED)`,
dan `git pull --rebase && git push`. Eén regel in stories/ROUTINE-LOG.md. Dan de volgende map.
