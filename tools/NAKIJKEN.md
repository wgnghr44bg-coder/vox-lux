# Nakijkronde lange video (vast, vóór elke verzending naar de eigenaar)

Eigenaar 24 nov 2026: "wat kunnen we maken zodat dit voortaan automatisch wordt gezien en aangepast als het niet klopt, ik moet
nu elke keer zelf kijken". Drie lagen; pas als alle drie schoon zijn gaat de video naar de eigenaar.

## Laag 1 + 2: scènewachter (automatisch, in de renderer)
`tools/scenewachter.py` + `kanalen/marketdoodle/achtergronden.json`. Elk voorwerp meldt waar het op staat (`op=`):
vlak (stoep, aanrecht, tafel-rechts, vloer ...), `muur`, `hand:<naam>` / `bek` / `aan:<iets>` (met `punt=`) of `beeld`.
- Staat het niet op dat vlak -> de wachter zet het er zelf op (AANGEPAST).
- Staat het door een meubel -> schuift het opzij; lukt dat niet -> FOUT.
- Hangt iets niet op vrije muur, bedekt iets een gezicht, of is er geen `op=` -> FOUT.
Uitslag: `SCENEWACHTER.md` (na `--plaat` en na de render). **0 fouten vereist.** AANGEPAST-regels even nakijken op het blad.
Nieuwe achtergrond: `python tools/meet_achtergrond.py <png>` en vlakken/muur/meubels invullen in achtergronden.json
(zonder dat geeft de wachter een FOUT).

## Laag 2b: herkenwachter (blind herkennen, eigenaar 24 nov: "pas de controle aan, ik blijf niet elke keer zelf testen")
`python tools/herkenwachter.py <renderer-map>` knipt elk gemeld voorwerp los uit (zonder zoom/tekst), met rood kader en een
nummer, zonder naam -> `herkennen/blad-NN.jpg` + `sleutel.json`. Eén hulpje dat het verhaal NIET kent zegt per nummer wat
het is (mag sleutel.json niet lezen). Komt dat niet overeen met de bedoelde naam (bv. "telefoon" voor een stuk gamestoel),
dan is het onherkenbaar: opnieuw tekenen of weglaten. Elk zelfgetekend voorwerp moet zich melden met WACHT.plaats(),
anders wordt het niet getest.

## Laag 3: nakijkronde per overzichtsblad (Claude-hulpjes, gratis)
1. `python tools/rariteitenwachter.py <video.mp4>` -> `rariteiten/overzicht-NN.jpg` (12 beelden, elke 2 s, met de gesproken zin
   eronder) + `overzicht-NN.txt`.
2. Start **per blad één hulpje** (Agent, general-purpose), in groepjes van ±6 tegelijk, met de opdracht hieronder. Elk hulpje
   kijkt met frisse ogen naar alleen dat blad.
3. Verzamel de meldingen, herstel in de renderer, render opnieuw, en laat de hulpjes de bladen van de herstelde stukken
   opnieuw nakijken. Pas als er niets meer gemeld wordt: video naar de eigenaar.

### Opdracht voor elk hulpje (invullen: <blad>, <txt>)
```
Je bent een strenge beeldcontroleur voor een 2D-tekenfilm (simpele ronde poppetjes, platte achtergronden, ondertitels onderin,
grote koppen bovenin). Bekijk <blad> (Read) en lees <txt> (tijd + de zin die op dat moment gezegd wordt).
Beantwoord voor ELK van de 12 beelden deze vragen en meld alleen echte fouten:
1. WAAR STAAT HET OP? Zweeft er iets (auto, bord, apparaat, mat, dier, voorwerp) zonder dat het op de vloer/stoep/tafel/
   aanrecht staat, aan de muur hangt of door iemand wordt vastgehouden?
1b. LOGISCHE PLEK? Staat het waar het in het echt zou staan (huiswerk op een bureau, bord op tafel, router op het aanrecht,
   tv aan de muur of op een kast)? "Op de vloer gezet" omdat het anders zweefde is meestal FOUT.
2. DOOR IETS HEEN? Staat een voorwerp of persoon dóór een meubel (bank, stoel, kast, koelkast, tafel) of half erin?
3. ZIE JE WAT ER GEZEGD WORDT? Wordt een voorwerp of handeling uit de zin genoemd die je niet ziet (bv. "the TV is broken"
   maar er is geen tv; "Grandma ties the string" maar je ziet haar niets doen)? Klopt WIE het doet?
   Past het GEZICHT bij de zin (bv. "A little less happy" maar de jongen lacht -> fout; verdrietig/geschrokken/blij)?
4. KLOPT DE HANDELING? Touwtjes/kabels lopen naar de juiste plek (mond, klink, stopcontact); wie iets vasthoudt, heeft het in de hand.
5. RARE VORMEN? Losse vlekken, half weggepoetste stukken, vormen die nergens bij horen, iets over een gezicht, rare kleuren op
   een gezicht (clown-stippen), tranen/druppels op de verkeerde plek.
6. TEKST? Tekst die buiten zijn kader loopt, afgesneden is, onleesbaar klein is of verkeerd gespeld.
   Bedekt een kop/tekst iets belangrijks (een hoofd, het dier of voorwerp waar de zin over gaat)? Is het herkenbare deel
   (hoofd van een dier, gezicht) echt te zien?
7. AFGESNEDEN? Hoofden, personen of belangrijke voorwerpen die door de beeldrand worden afgesneden (een stapel vuilniszakken of
   een auto die het beeld in rijdt mag wel).
Normaal en GEEN fout: tekenfilmstijl, blosjes op de wangen, koppen bovenin die zweven (dat is tekst), ondertitels, naamlabels,
de camera die langzaam inzoomt, een gebaar van een poppetje.
Antwoord als lijst: "<tijd> – <wat> – <waar in beeld> – <hoe te herstellen>". Niets gevonden: "BLAD OK".
```
