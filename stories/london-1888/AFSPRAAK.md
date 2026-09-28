# London 1888: slaapdocumentaire

Afspraak voor dit project. Niets maken of betalen voordat de eigenaar zegt:
"begin". Daarna mag alles in één keer, zonder tussendoor te vragen.

## 1. Script
- Eén doorlopende slaapdocumentaire van ongeveer 2 uur (~16.000 woorden),
  in het Engels, over Londen in 1888 en het nooit opgeloste mysterie
  (Jack the Ripper).
- Opbouw: intro alleen aan het begin (de eigen intro, "Close your eyes if
  you'd like."), rustig slot alleen aan het eind. Geen hoofdstuktitels die
  worden voorgelezen. Delen 1-3 eindigen met een zachte overgang.
- Stijl: rustig, geruststellend, geen cliffhangers; `[pause]` en
  `[long-pause]` markers.
- Historisch correct; onzekerheid benoemen. Geen gruwelijke details, geen
  beschrijving van geweld. Slachtoffers respectvol: hun leven, niet hun dood.
- Vier delen van ~30 min:
  1. *De stad in de mist*: Londen 1888, Whitechapel, logementen, dokken,
     matchgirls-staking, gaslampen en mist, de politie (H Division).
     **Status: eerste versie klaar** (`deel1-de-stad-in-de-mist.txt`,
     ~2.000 woorden, ~15 min; nog aanvullen tot ~30 min).
  2. *De herfst van 1888*: de levens van Mary Ann Nichols, Annie Chapman,
     Elizabeth Stride, Catherine Eddowes en Mary Jane Kelly (naar Hallie
     Rubenhold), angst in de buurt, Whitechapel Vigilance Committee.
  3. *Brieven, kranten en speurders*: massakranten, "Dear Boss", "Saucy
     Jacky", "From Hell", Abberline en Warren, de Goulston Street-boodschap,
     onderzoek zonder moderne techniek.
  4. *Een zaak die nooit sloot*: verdachten (Druitt, Kosminski, Ostrog,
     Tumblety, latere theorieën), waarom niets bewezen is, het mysterie
     vandaag, heel rustig slot.

## 2. Audio
- `tools/xai_voiceover.py` met de standaardinstellingen: xAI, stem **Lux**,
  1.0x, pauzes 500/1000 ms, 300 ms na zinnen, natuurlijke pauze na komma's,
  randstilte weggeknipt, -16 LUFS.
- Sleutel via Claude Code credential: `--proxy-auth`.
- Resultaat: **één MP3 van ~2 uur** (spraakkwaliteit, ~115 MB).
  Verwachte kosten ~108.000 tekens, ~$0,45.

## 3. Afbeeldingen (Meta AI)
- Na de audio (dan zijn de tijden bekend): ~45-50 genummerde prompts met
  begin- en eindtijd en de bijbehorende zin uit het verhaal.
- **Vooral beelden van voorbeelden uit het verhaal** (markt in Petticoat
  Lane, logement, dokwerkers bij de poort, lantaarnopsteker, agent op zijn
  ronde, buurtwacht met lantaarns, krantenjongen, brief bij kaarslicht,
  inspecteur aan zijn bureau, enz.), aangevuld met een paar sfeerbeelden.
- Stijl zoals `stijl-voorbeeld.webp`. Vaste stijlzin achter elke prompt:
  `cinematic realistic photograph, Victorian London 1888, dusk, thick
  blue-grey fog, warm amber gaslight, wet cobblestones, soft glow, calm and
  quiet atmosphere, no people in focus, highly detailed, wide 16:9 landscape`
- Mensen op afstand of als silhouet. Geen geweld, geen slachtoffers, geen
  realistische nep-foto's van echte personen.
- Waar passend: tip voor een echt rechtenvrij historisch beeld (bijv.
  Charles Booth-kaart, Wikimedia Commons).

## 4. Video
- Eigenaar uploadt de afbeeldingen als `001.jpg`, `002.jpg`, ...
- MP4 16:9 met langzame zoom (Ken Burns) en zachte overgangen, op de tijden
  uit de tijdlijn. Als 1080p te groot is om te versturen: 720p of in delen.
