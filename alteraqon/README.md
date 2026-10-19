# Alteraqon – "What if"-documentaires (YouTube: @alteraqon)

Apart kanaal, los van IfScape3D (3D-render, Atlas-stem) en Sleep Archives.

## Stijl
> **Beeldmodel sinds 19 okt 2026: FLUX.2 [klein] 4B** in ComfyUI (`C:\comfy-workflows\flux2klein_api.json`), Z-Image alleen als reserve.
> **Vaste regel (eigenaar 13 okt 2026): xAI ALLEEN nog voor de stem.** Beelden én clips uitsluitend via ComfyUI op de pc van de eigenaar
> (beelden: Z-Image Turbo, clips: Wan 2.2 5B), niet meer via xAI. `make_images.py` en `make_clips.py` (xAI) staan uit; alleen na uitdrukkelijk ja.
> Werkwijze: cloudsessie schrijft `prompts.txt` + `comfy-clips.txt`, commit + pusht en vraagt de eigenaar op zijn pc te draaien:
> `python alteraqon/tools/comfy_batch.py zimage_api.json <map>` (Short: `--short`) → `afbeeldingen/NAAM.png`, daarna
> `python alteraqon/tools/comfy_batch.py wan_i2v_api.json <map>` → `clips/NAAM.mp4`. Pas na zijn push verder (contactsheet, stem, video).
> Oude video's houden hun xAI-`.jpg`/`.mp4`; een ComfyUI-`.png` of `clips/NAAM.mp4` met dezelfde naam gaat altijd voor.

- Verticaal 1080x1920, ca. 60–70 s, Engels.
- AI-foto's, één beeld per gesproken zin, langzame zoom/pan, koele documentaire-grade + lichte filmkorrel.
- **Vaste stem (eigenaar 13 okt 2026): Chatterbox lokaal, `chatterbox_als_bm_george_rustig`** → `tools/make_voice_local.py <map> [cache]
  --pause-ms 700 --long-pause-ms 1600 --sentence-pause-ms 600 --speed 0.92` op zijn pc (stem-env), gratis.
  (Eigenaar 19 okt 2026: nog rustiger; eerder 350/800/250 en 500/1200/400 – "te snel". Script ±105–120 woorden.) Getallen voluit schrijven ("nineteen seventy-nine").
- Vroeger: stem xAI **Lux**, tempo 0.9, pauzes 900/1700 ms + 600 ms na elke zin (`[pause]` achter elke regel).
- Tijdstempels als korte lower-third (~2,6 s): goud lijntje schuift in, label in Inter SemiBold, groot getal in Inter Display Light.
- Ondertitels in Inter SemiBold. Donkere drone + lage klap bij elke tijdstempel.

## Per video
Map `<datum>-<slug>/`: `script-cues.txt` (tekst + `{img:Sxx}`), `prompts.txt`, `afbeeldingen/`, `voice.mp3`,
`voice-times.tsv`, `make.py` (beeld + tekst + eindmix), `upload.json`. Geen mp4 in git.

Kosten per video: alleen een paar cent stem (beelden gratis via ComfyUI; vroeger ≈13 xAI-beelden à $0,02).

## Video's
- `2026-10-10-humans-vanish/` – What if all humans vanished? (eindversie: `doc/make-doc-lux.py`)
- `2026-10-10-struck-by-lightning/` – What if you got struck by lightning? (`make.py`)
- `2026-10-10-iron-vanished/` – What if every piece of iron vanished? (`make.py` → tools/make_video.py + shots.py) – geüpload 11 okt (privé): https://youtu.be/xY-blDzbe7c
- `2026-10-10-asteroid-missed/` – What if the asteroid that killed the dinosaurs had missed? **Lange video**, 16:9 1920x1080, ca. 3 min (`make.py`, `make_thumbnail.py` → `thumbnail.jpg`)
- `2026-10-11-ai-smarter/` – What if AI becomes smarter than humans? (`make.py` → tools/make_video.py + shots.py)
- `2026-10-11-venom-superman/` – What if Venom took over Superman? (snelle versie: **Atlas-stem**, tempo 1.05, korte pauzes, ~35 s, harde opening zonder fade-in, geen titeltekst; beelden zonder officiële logo's)
- `2026-10-11-spiders-hunt/` – What if all spiders hunted together? (snelle stijl: Atlas-stem tempo 1.0, ~51 s, harde opening, geen titeltekst)
- `2026-10-11-clone-hates-you/` – What if every human had a clone that hated them? (snelle stijl: Atlas-stem tempo 1.0, ~53 s, harde opening, geen titeltekst)
- `2026-10-11-sky-countdown/` – What if the sky displayed a countdown? **Lange video**, 16:9 1920x1080, ca. 3 min 7 s; Atlas-stem
  zoals de snelle shorts (`make_voice.py <map> <cache> --voice atlas --speed 1.0 --pause-ms 300 --long-pause-ms 600 --sentence-pause-ms 200`),
  harde opening, geen titeltekst; aftellende cijfers in de lucht zelf getekend (ASS in `make.py`), `make_music.py`, `make_thumbnail.py`
  – geüpload 11 okt (privé): https://youtu.be/Cy7LxOLVcPU (thumbnail handmatig in Studio: API mag geen eigen thumbnail zetten)
- `2026-10-11-volcano-city/` – What if a volcano erupted in your city? (**mix-stijl**: 2 xAI-lite-clips + gratis effecten, Atlas-stem, ~51 s)
- `2026-10-11-random-superpower/` – What if every human got a random superpower? (**mix-stijl**: 2 lite-clips K01 + K03, effecten, Atlas-stem, ~55 s; twist: Bajau-milt, SCN9A, tetrachromatie)
  – geüpload 11 okt (openbaar): https://youtu.be/8ErptEFbUnA
- `2026-10-11-flat-earth/` – What if the Earth was flat? (**snelle stijl, test – AFGEWEZEN** door de eigenaar: "te veel en te druk"; niet uploaden)
- `2026-10-18-moon-disappeared/` – What if the Moon disappeared? (`make.py` → tools/make_video.py + shots.py)
- `2026-10-18-grow-1cm-every-minute/` – What if you grew 1cm every minute? (`make.py` → tools/make_video.py + shots.py)
- `2026-10-19-sun-never-sets/` – What if the Sun never stopped shining? (`make.py` → tools/make_video.py + shots.py)
- `2026-10-19-whale-swallowed-you/` – What if a whale swallowed you? (`make.py` → tools/make_video.py + shots.py)

- **Omgeving (eigenaar 13 okt 2026):** geen vaste stad; elk beeld toont letterlijk wat er gezegd wordt en past bij het onderwerp
  ("wow"-beelden: spectaculair, ook wetenschappelijke 3D-renders voor lichaam/natuur).

## Beweging (mix-stijl, eigenaar okt 2026)
- **Gratis effecten** op foto's: 6e veld in een shot in `shots.py`, bijv. `(5,"K06","out","",None,"ash")`.
  Effecten uit `tools/fx.py`: `embers`, `ash`, `dust`, `rain` (combineren met `+`).
- **Echte bewegende clips:** via ComfyUI/Wan (zie hieronder) → `clips/NAAM.mp4`; make_video gebruikt die clip i.p.v. de foto.
  Short: **alle beelden mogen bewegen** (eigenaar 13 okt 2026: via ComfyUI gratis, max 5 s per beeld; make_video rekt een korte clip vanzelf op); lange video: 15–20+. In elke clip-prompt: "Everything stays solid and unchanged, no morphing,
  no new objects, slow gentle movement". (Vroeger xAI `make_clips.py`, $0,19 per clip – staat uit.)
- **Eigen ComfyUI (gratis, pc eigenaar: RTX 2080 Super, 8 GB):** `python alteraqon/tools/comfy_batch.py <workflow_api.json> <map>`.
  Wan 2.2 5B + `comfy-clips.txt` → `<map>/clips/NAAM.mp4` (1024x576, 5 s); Z-Image Turbo + `prompts.txt` → `<map>/afbeeldingen/NAAM.png` (`--short` = staand: beelden 768x1344, clips 576x1024)
  (uitleg bovenin het script). Voorbeeld: `2026-10-13-donut-earth/`.
- Clips (bronmateriaal) mogen in git; de eind-mp4 niet.
- **Snelle stijl: NIET gebruiken** (eigenaar okt 2026: te veel beelden, te druk; houd het rustig, ±1 beeld per zin).
  Technisch kan het nog (alleen foto's, veel beelden): in `shots.py` mag het eerste veld ook `(regel, extra seconden)` zijn,
  bijv. `((2,0.9),"F03",...)` = 0,9 s na het begin van regel 2; zo wisselt het beeld binnen een zin. Voorbeeld: `2026-10-11-flat-earth/`.

Meld hem bij de verzamelsessie **"mp4 alteraqon shorts"** (`session_0149vZSeTdq1ZbZMfe47EX4e`) met send_message:
`Nieuwe video: alteraqon/<datum>-<slug>` (na commit + push). Die sessie rendert de mp4 en zet hem met de
kopieerbare titel/beschrijving/tags (uit upload.json) klaar voor de eigenaar.

## Opbouw van elke video (sjabloon = de lightning-video)
Kopieer `_sjabloon/` naar `<datum>-<slug>/` en vul in. Verhaal in 6 stappen, ca. 18 zinnen, 65–75 s:
1. **Opening:** "Imagine… <onderwerp>. What would happen…?" (zegt meteen waar de video over gaat; geen titel in beeld)
2. **POV-opbouw:** jij staat ergens, kleine voortekenen, spanning.
3. **Het moment:** één kort woord ("Then.") + witte flits en knal (`BANG` in shots.py).
4. **Feiten met grote getallen:** elk feit een eigen beeld + tijdstempel (label + getal, ~2,6 s in beeld).
5. **Dieptepunt, dan de twist ("But…"):** verrassend detail, goede afloop, een bizar echt record.
6. **Slot:** "So remember." + les of vraag aan de kijker.

Regels: één beeld per (deel)zin, wissel precies op de stem; elke zin eindigt op `[pause]` of `[long pause]`;
feiten alleen als ze algemeen bekend en controleerbaar zijn; ca. 13 afbeeldingen (ComfyUI, gratis).

Stappen (vanuit de map `vox-lux`):
```
cp -r alteraqon/_sjabloon alteraqon/<datum>-<slug>       # daarna script-cues.txt, prompts.txt, shots.py, upload.json invullen
# beelden: eigenaar draait op zijn pc  python alteraqon/tools/comfy_batch.py zimage_api.json alteraqon/<datum>-<slug> --short
python3 alteraqon/tools/make_voice.py  alteraqon/<datum>-<slug>
python3 alteraqon/tools/make_video.py  alteraqon/<datum>-<slug> <tmpmap>    # -> <tmpmap>/<slug>.mp4
```
In `shots.py` verwijst het eerste getal naar de regel in `voice-times.tsv` (pas invullen ná make_voice).

## Lange video (16:9, ca. 3 min) – voorbeeld: de asteroid-video
Zelfde stijl, maar liggend en ca. 40–48 zinnen/beelden (beelden gratis via ComfyUI + een paar cent stem):
- beelden: eigenaar draait `comfy_batch.py zimage_api.json <map>` (16:9, 1280x720; `T01` = basis voor de thumbnail)
- `python3 alteraqon/tools/make_voice.py <map> <cachemap buiten repo>` (cache: na inkorten alleen nieuwe zinnen betalen)
- `make.py`: beelden volgen de kolom `image` in voice-times.tsv; tijdstempels per regelnummer; label linksboven
  scheidt feiten (`REAL HISTORY`) van speculatie (`ALTERNATE TIMELINE · SPECULATION`).
- Muziek: `make_music.py` in de videomap maakt een eigen score (`music.mp3`, gesynthetiseerd, geen auteursrecht) die de
  scènes volgt; make.py mixt die onder de stem (zachter zodra Lux praat, stem ~17 dB boven de muziek).
  ElevenLabs Music kan niet: vraagt een betaald ElevenLabs-abonnement.
- Thumbnail 1280x720 met `make_thumbnail.py` in de videomap (tekst links, YouTube zet de duur rechtsonder).
- YouTube-tekst als hieronder, maar zonder `#shorts`.

## Online zetten (eigenaar 18 okt 2026)
Pas als de eigenaar de video goedkeurt en zegt **"zet online"**, in de cloudsessie (daar staat de sleutel van @alteraqon):
```
python3 alteraqon/tools/upload_short.py alteraqon/<datum>-<slug> <tmpmap>/<slug>.mp4      # standaard openbaar
```
Titel, beschrijving en tags komen uit `upload.json`; categorie Wetenschap & technologie, niet voor kinderen,
"gewijzigde of synthetische content" = ja. De link wordt in `upload.json` bewaard; nooit twee keer uploaden.
Na de upload wordt ook de TikTok-tekst (`"tiktok"` in upload.json) getoond om zelf bij TikTok te plakken.

## YouTube-tekst (vaste opzet, eigenaar okt 2026: kort en simpel)
Per video invullen met het onderwerp. De beschrijving is **algemeen** (eigenaar okt 2026): ze maakt nieuwsgierig naar het onderwerp,
maar herhaalt niet wat er letterlijk in de video staat (geen getallen/feiten uit het script, de twist niet verklappen).

- **Titel:** `What if <vraag>? <emoji>`
- **Beschrijving:** één of twee algemene, prikkelende zinnen over het onderwerp (wat-als-situatie, sfeer), een vraag aan de kijker met 👇, dan 4 hashtags.
- **Tags:** 4 stuks: `what if`, onderwerp, langere zoekterm, `science`.
- In Studio: "Gewijzigde of synthetische content" → **Ja**.

Voorbeeld (lightning):
```
What if you got struck by lightning? ⚡
```
```
One flash from the sky, and suddenly it's you. What really happens to the human body when lightning hits?

Would you go outside during a storm? 👇

#whatif #lightning #science #shorts
```
```
what if, lightning, struck by lightning, science
```
