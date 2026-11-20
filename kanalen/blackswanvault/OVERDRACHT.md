# BlackswanVault: overdracht (stand vr 20 nov 2026, 17:30)

Vaste regels: `README.md` (getallen in cijfers, rustige beeldwissels, clip moet passen, uitspraak controleren, grafieklabels pas als de lijn er is, thumbnailstijl, stem blijft zakelijk-23). Planning: `../PLANNING-KANALEN.json`.

## Gepland op YouTube (privé, gaan vanzelf openbaar; kanaal gecontroleerd)
| dag | tijd | wat | id |
|---|---|---|---|
| za 21 nov | 15:00 | Why Is Take-Two's Stock Falling After GTA 6? (video3) | GEktvTAsVIw |
| za 21 nov | 17:00 | Short: GTA 6 Broke Records. So Why Did the Stock Fall? | HWcKzzN7PzI |
| zo 22 nov | 15:00 | Microsoft, JPMorgan and the FAA All Went Down. It Wasn't Hackers (video5) | nMqDK9HAAcA |
| zo 22 nov | 17:00 | Short: Microsoft, JPMorgan and the FAA All Went Down in One Week | l3tU0GKVldM |

## Maandag 23 nov: markt-video (video4) — NOG NIET geüpload
- Titel: "The Nasdaq Just Fell 10%. Here's What Investors Are Afraid Of". Thumbnail: `video4/thumbnail-definitief.jpg` (NASDAQ / -13% / WHY?).
- Ma-ochtend: koersen ophalen (data/*.json, Yahoo), `{SLOT}` in `video4/script.txt` vervangen door 2-3 zinnen over de laatste stand (GEEN voorspelling), `stem.sh` + `mix.py` + `maak.sh`, controleren, eindversie naar eigenaar.
- Pas na akkoord eigenaar: privé uploaden met publishAt ma 15:00 (14:00Z), kanaal checken.
- Short: `shorts/markt-short-1.mp4` (zin 0-18), beschrijving `shorts/markt-short-1-beschrijving.txt` ({LINK} invullen), ma 17:00. Eigenaar zei "Ja" op 15:00/17:00.
- Beschrijving lange video nog schrijven (3 zinnen, hoofdstukken met cijfers, "Not financial advice.", 3 hashtags).

## Dinsdag 24 nov: nieuw onderwerp (lange video + Short) — wacht op "ja" van eigenaar
- Voorstel: OpenAI-agents braken uit hun test en hackten Hugging Face; Californië klaagt OpenAI aan (17 nov; "meer dan 80 keer controle verloren" = beschuldiging). Zakelijke invalshoek (beleggers SoftBank/Microsoft, Anthropic ook). Titelidee: "OpenAI's AI Escaped and Hacked a Company. Now California Is Suing"; thumbnail OPENAI / 80+ TIMES / OUT OF CONTROL?
- Werkwijze zoals video5: eerst bronnen lezen (`bronnen.md`), script (≥ 8 min, antwoord vooraan), proef 1 min naar eigenaar, dan geheel.
- Ook di 24 nov: kijkersbehoud vergelijken (Nvidia vs GTA nieuwe volgorde).

## Gereedschap (video5 is het nieuwste voorbeeld)
- `video5/`: stem.sh (stem + Whisper), mix.py, maak.sh, render5-basis.py + render5-shots.py → render5.py
  (`m=$(grep -n "^def shot_op" ../video3/render3.py | cut -d: -f1) && { cat render5-basis.py render5-shots.py; echo; tail -n +$m ../video3/render3.py; } > render5.py`).
  ZR() mag halve zinnen (49.5). `ZINNEN=<bestand>` om met andere tijden te renderen.
- Foto's: `echt/zoek.py` + `echt/dl.py naam=Titeldeel` (Wikimedia, credits in echt/bronnen.tsv). AI-beelden: `ai/prompts.txt` + `tools/comfy/comfy_batch.py`.
- Thumbnail: `video5/thumb_markt2.py <beeld> <regel1> <regel2> <uit> [regel3] [--geen-lijn]`; derde regel = prikkel, per video anders (niet steeds WHY?).
- Shorts: `shorts/maak_short.py` (knipt nu altijd vóór de volgende zin); woorden.json nakijken op dubbele stukken van Whisper.
- Beelden, stem en mp4 staan alleen op de pc (niet in git). Eigen stemopnames alleen in `~/vox-lux-stemmen/`.
