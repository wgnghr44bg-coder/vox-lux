# Shorts om en om in twee stijlen (eigenaar, 7 okt 2026, test)

De eigenaar wil weten welke stijl beter werkt (kijkduur, weergaven). Daarom wisselen de Shorts om en om:

| | Stijl A – POV (huidige regels) | Stijl B – gravity-stijl (zoals `topics/gravity-doubled`) |
|---|---|---|
| Opening | eerste zin "Imagine" + het onderwerp ("Imagine the Earth stopped spinning.") | eerst de plek en waarom het ertoe doet ("Imagine you are standing by a wide river… Every bridge … was made for one force."), daarna "Now imagine that …" |
| Titel in beeld | nee | ja: titelkaart bij de start (`title` + `titleOut` in scenario.js, zoals gravity-doubled) |
| Einde | geen eindkaart, beeld vloeit uit | eindkaart met de titel (`end: { title, lines }`, zoals gravity-doubled) |
| Verhaal | POV-beleving, "you" | meer uitleg met feiten en getallen ("At two g, you would weigh twice as much"), wel "you" |
| Beschrijving | begint met "POV: …" | begint met een feit of de vraag, geen "POV" |

Alles wat niet in deze tabel staat (ondertitels + controle, logo-moment, auto's, "wat de stem zegt moet je zien",
geen haak aan het begin, lengte, uploadtijden) blijft gelijk voor beide stijlen.

Werkwijze:
- Volgorde: kijk in de log van USAGE.md welke stijl de vorige Short had en kies de andere. Staat de stijl al in de
  planning (`[A]` / `[B]`), volg die.
- Zet de stijl in `upload.json` (`"stijl": "A-pov"` of `"stijl": "B-gravity"`) en in de USAGE.md-log (kolom Wat).
- Lange video's vallen buiten deze test.
- Weekcheck/maandaudit vergelijken per stijl: weergaven, gem. kijkduur en kijkpercentage (pas iets zeggen bij ≥ 3 Shorts
  per stijl met elk ≥ 100 weergaven).
