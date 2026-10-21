# What If It Never Stopped Raining? – stem en MP4

De animatie is `tools/threejs/never-stopped-raining.html`. De geluidseffecten (regen, wind, onweer, vonken,
druppels, riool) worden in de pagina zelf gemaakt. Live zet je ze aan met de knop **Sound**.

## MP4 met geluidseffecten
Die maakt Claude in de cloud. Zelf maken kan ook, met node + playwright + ffmpeg:
```
node tools/threejs/export_mp4.mjs tools/threejs/never-stopped-raining.html never-stopped-raining.mp4
```
Duurt ongeveer 1,7 s per beeld op een cloud-CPU; op een pc met videokaart veel sneller.

## Stem erbij (gratis, op de pc)
Vanuit de map `vox-lux`, in de stem-omgeving (zie `tools/comfy/README.md`):
```
python tools/comfy/make_voice_local.py tools/threejs/never-stopped-raining
python tools/threejs/place_voice.py tools/threejs/never-stopped-raining --video never-stopped-raining.mp4
```
1. Maakt `voice.mp3` + `voice-times.tsv` uit `script-cues.txt` (Chatterbox als bm_george, rustig).
2. Zet elke zin op de tijd van zijn ondertitel (`cues.tsv`) → `voice-placed.mp3`,
   en mixt hem onder de video → `never-stopped-raining-voice.mp4`.

Past een zin niet in zijn tijdvak, dan wordt hij tot 15% versneld en geeft het script een waarschuwing.
Pas je ondertitels in de HTML aan, pas dan ook `cues.tsv` en `script-cues.txt` aan (zelfde tekst en tijden).
