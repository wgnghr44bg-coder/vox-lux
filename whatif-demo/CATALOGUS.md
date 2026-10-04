# What if — catalogus

Alles om een nieuwe low-poly "What if"-video te maken voor $0 (behalve de voice-over).
Stijl = earth-stops: three.js low-poly, 9:16, Playfair/Cormorant-teksten, teller linksboven, captions, eindkaart.
Lees dit eerst; hergebruik wat er is en bouw alleen wat ontbreekt (nieuwe onderdelen meteen in `lib/` of `make_audio.py`).

## Werkwijze (kopie van earth-stops)

```sh
cd whatif-demo && npm install                       # three + fonts (eenmalig); pip install numpy scipy
mkdir <onderwerp> && cd <onderwerp>                 # script.txt, scene.html, sound.py, .gitignore (zie internet-gone)
python3 ../../tools/xai_voiceover.py script.txt --proxy-auth --voice lux --speed 1.0 \
  -o $PWD/voice.mp3 --timeline $PWD/voice-times.tsv --cache-dir $PWD/.vo-cache   # ABSOLUTE paden (anders faalt de concat)
cd ..
node lib/render.mjs <onderwerp> sheet 5 30 45 60 72 84     # 6 testbeelden naast elkaar -> <onderwerp>/stills/sheet.jpg
node lib/render.mjs <onderwerp> timeline                   # -> timeline.json (TL + EVENTS) voor het geluid
node lib/render.mjs <onderwerp> video <onderwerp>/silent.mp4 4   # ± 40 min voor 90 s met 4 workers
python3 make_audio.py <onderwerp>                          # -> sfx-bed.wav + mix.wav (-14 LUFS, stem bovenop)
sh lib/finish.sh <onderwerp> <naam>.mp4                    # 1080x1920, H.264 + AAC
```

- Script: Engels, 170–220 woorden, jij-vorm, `[pause]` / `[long pause]`; tijdens de climax 5–8× `[long pause]` (stem zwijgt).
- Tijdlijn: video-tijd = `voice-times.tsv` + `VO_OFFSET` (0.8 s). Alle beats staan in het `TL`-blok bovenaan `scene.html`.
- Verhaal: rustig → er klopt iets niet → eerste effecten → escalatie → climax (stil) → stilte → laatste zin (eindkaart).

## Gedeelde code — `lib/`

| bestand | wat | aanroep |
|---|---|---|
| `lib/render.mjs` | stills / sheet / timeline / video (parallelle workers, `from`-seconde voor alleen de staart) | `node lib/render.mjs <dir> <mode> ...` |
| `lib/finish.sh` | silent.mp4 + mix.wav → 1080x1920 mp4 | `sh lib/finish.sh <dir> out.mp4` |
| `lib/core.js` | `rng, hash, clamp, smooth, lerp, noise, monotone, keyframes, C`; `setup()` (renderer, camera, luchtkoepel, hemi+zon met schaduw); `lam, glow, shadowed`; `facadeTex/facadeMats/facadeBox` (soorten `win`, `shop`, `tower`, `broken`, `glass`); `PALETTE, TOWER_PAL`; `canvasTex`, `puffTexture` (stof/rook), `glowSprite` (lichthalo's) | `import {...} from '../lib/core.js'` |
| `lib/hud.js` | `makeHud(TL)` → `hud(t, {num, second, secondOpacity, hudOpacity, black, haze})`: titel, teller, captions, eindkaart, fade (CSS + fonts zitten erin) | |
| `lib/street.js` | `makeStreet` (4 rijstroken, stoepen, strepen, zebra); `makePerson/posePerson` (lopen, stilstaan, hoofd omlaag/opzij, telefoon omhoog, zwaaien); `carMesh/setCarLights` (koplampen + halo, remlichten, taxi, politie met zwaailicht); `streetLamp` (lamp + lichtplas, `setOn(k)`); `plane` (vliegtuig + condensstreep, `fly(a,b,u)`) | |

`earth-stops/` is gemaakt vóór `lib/` en staat nog op zichzelf (eigen render.mjs en scene.html met dezelfde code); niet aanpassen tenzij nodig.

## Werelden / sets

| set | waar | bijzonderheden |
|---|---|---|
| Kuststad-avenue (evenaar) | `earth-stops/scene.html` | palmen, zee aan het eind, zebra + verkeerslichten, café-stoelen, wolkenkrabbers die omvallen; camera midden op straat |
| Financieel district (straatniveau) | `internet-gone/scene.html` | glazen torens met verlichte ramen (emissiveMap, per toren aan/uit), reclameschermen + ticker, winkels met rolluiken, geldautomaat (WELCOME → OFFLINE), straatlantaarns, file; camera op de stoeprand; dag → schemer → nacht |
| Yellowstone-proef | `scene.html` + `render.mjs` (hoofdmap) | eerste proef, `yellowstone-demo.mp4` |

## Effecten (in scènes, kopieerbaar)

- **Wind-fysica** (earth-stops): papier, bladeren, stoelen, auto's, glas, gevelbrokken, losscheurende verdiepingen, omvallende torens, stofwolken.
- **Schermen die uitvallen** (internet-gone `screen()/screenState()`): glitch-flikkering, "NO CONNECTION", dan zwart.
- **Ramen donker** (internet-gone `tower()`): per toren `offT`, enkele blijven 's nachts aan (`nightLit`).
- **Rolluiken** (internet-gone `shops`), **geldautomaat OFFLINE**, **verkeersinfarct** (internet-gone: rijstrook-volgmodel, scheefgezette blokkeerders, toeter-events), **menigte** (wandelaars, rij, drukte op straat), **vliegtuigen die verdwijnen**, **dag→nacht** (`keyframes` voor lucht, zon, hemi, mist), **dip naar zwart → lege straat**.

## Geluiden — `make_audio.py` + `sfx/` (alleen synthese, $0)

Generatoren in `make_audio.py` (`s_<naam>(rng, ...)`), standaardversie als `sfx/<naam>.wav` (`library()` schrijft ze allemaal):

| naam | wat | | naam | wat |
|---|---|---|---|---|
| `stad` | rustige stad: verkeer, auto's, vogels (loop 30 s) | | `ping` | meldingstoon telefoon (`pitch`) |
| `wind` | wind-loop | | `toeter` | autotoeter (`length`, `pitch`) |
| `gerommel` | diep gerommel | | `stemmen` | stemmen-geruis van een menigte, zonder woorden (loop 20 s) |
| `drone` | zachte donkere toon | | `sirene` | sirene in de verte (loop 10 s) |
| `klap` | betonklap | | `uitval` | scherm/stroom valt uit: klik, zoem, wegzakkende brom |
| `glas`, `barst` | brekend glas / één barst | | `rolluik` | rolluik dat dichtratelt + bons |
| `metaal`, `kraak` | buigend metaal / kreunend gebouw | | `foutpiep` | drie lage foutpiepjes (automaat) |
| `puin`, `rammel` | puin / rammelen | | `auto`, `tik` | voorbijrijdende auto / voetgangerstik |

Hulpjes: `place(bed, snd, t, gain, pan)`, `loop` via `np.tile`, `db()`, `smooth()`, `lp/hp/bp`, `stereo()`, `echo()`.
Per video: `<dir>/sound.py` met `build(topic) -> stereo bed` (`from make_audio import ...`); `make_audio.py <dir>` mixt dan automatisch met `voice.mp3` (ducking, −14 LUFS). Zonder `sound.py` gebruikt het de earth-stops-opbouw.

## Tellers

| teller | video | |
|---|---|---|
| EARTH'S SPIN / AT THE EQUATOR, mph + WIND | earth-stops | 1,037 → 0 |
| GLOBAL INTERNET / CONNECTIVITY, % + PEOPLE ONLINE (billion) | internet-gone | 100 → 75 → 50 → 25 → 0 |

Teller = `TL.counter` (punten `[t, waarde]`, monotone interpolatie), tekst via `hud(t, {num, second})`.

## Gemaakte video's

| video | map | stem | duur |
|---|---|---|---|
| What if Yellowstone erupted? (proef) | `yellowstone-demo.mp4` | – | |
| What if Earth stopped spinning? | `earth-stops/earth-stopped-spinning.mp4` | lux | 90 s |
| What if the Internet disappeared? | `internet-gone/internet-disappeared.mp4` | lux | 90 s |
