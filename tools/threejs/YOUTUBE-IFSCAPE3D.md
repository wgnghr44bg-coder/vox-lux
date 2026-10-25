# YouTube-standaard voor IfScape3D (alle What If-video's)

**Elke What If-video (Short én lange video) gaat naar het kanaal IfScape3D, nooit naar Sleep Archives**
(eigenaar, 25 okt 2026). Sleep Archives is alleen voor History for Sleep.

Alleen uploaden als de eigenaar erom vraagt. Eerst alle controles uit `whatif-prompt.md` (contactbladen,
`check_flicker.py` op de echte MP4: geen "KNIPPEREN").

## Uploaden
```
python3 tools/youtube_upload.py <video>.mp4 --channel whatif \
    --title "What if <onderwerp>? #shorts" --description-file beschrijving.txt \
    --tags "what if,what if <onderwerp>,<3-6 onderwerp-tags>,science,3d animation,ifscape3d,shorts" \
    --category 28 --language en --privacy public
```
- `--channel whatif` gebruikt `YT_WHATIF_REFRESH_TOKEN` en controleert vóór het uploaden dat het kanaal
  "IfScape3D" heet; anders stopt het script.
- Upload de volle kwaliteit (1080x1920), niet de kleine versie voor de chat.
- `--privacy public` als de eigenaar zegt "zet het online"; anders `private` en de eigenaar publiceert zelf.

## Instellingen
- Categorie: Science & Technology (`--category 28`)
- Taal: Engels
- Niet voor kinderen, AI-inhoud gemarkeerd (`containsSyntheticMedia: true`, standaard in het script)

## Titel
- Short: `What if <onderwerp>? #shorts` (zoals "What if a whale swallowed you? #shorts"). Kleine letters behalve
  het begin; eventueel één emoji.
- Lange video (16:9): `What If <Onderwerp>? (<korte haak>)`, bv. "What If AI Became Smarter Than Humans? (It
  Decided WE Are the Threat)". Max. ± 70 tekens.

## Beschrijving (Engels)
Short:
```
<1–2 spannende zinnen uit het verhaal, met één emoji>

Would YOU <survive / want …>? 👇

#whatif #<onderwerp> #<onderwerp> #science #3danimation #shorts
```
Lange video: 2–4 zinnen, dan hoofdstukken (`00:00 …`, minstens 3), dan de hashtags.

## Tags
Altijd `what if`, `what if <onderwerp>`, `3d animation`, `ifscape3d`, `science` (Shorts ook `shorts`)
+ 3–6 onderwerp-tags.

## Na de upload
Meld de eigenaar de link. Thumbnail is bij Shorts niet nodig; bij een lange video vragen of hij er een wil.

## Gemaakt op dit kanaal (nieuwste eerst)
| Datum | Video | Link |
|---|---|---|
| 2026-10-25 | What if all the oceans dried up? #shorts | https://youtu.be/lnqpiSFU5CY |
