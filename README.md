# VOX Lux

YouTube voice studio — **Lux only**. Dutch UI.

Recreatie van [VOX](https://aurora-ocean-terra-prairie.grok.me/) met één stem: **Lux** (oude slaapstem / documentaire).

Live (GitHub Pages): https://wgnghr44bg-coder.github.io/vox-lux/

## Nederlands

### Starten

```bash
cd /workspace/vox-lux
npm install
npm run dev
```

Open de URL die Vite toont (meestal `http://localhost:5173/vox-lux/`).

Lokaal praat de app met **Vite middleware** `POST /api/tts` (package `edge-tts-universal`, geen API-key).

### Build

```bash
npm run build
npm run preview
```

### TTS — Microsoft Edge neural (Lux-stand-in)

| | |
|---|---|
| Default stem | `en-US-ChristopherNeural` (diep/kalm mannelijk US) |
| NL | `nl-NL-MaartenNeural` |
| Tempo | default **0.7×** (featured sleep voice) |
| Output | echte **MP3** (`audio/mpeg`) — afspelen + download op iPhone |
| Footnote | *Gratis Edge-stem (Lux-achtig) — niet de officiële Grok Lux.* |

**Hoe audio wordt opgehaald**

1. `POST` OpenAI-compatibel JSON `{ model, input, voice, speed }` → `audio/mpeg`
2. Lokaal / `vite preview`: Vite-plugin `plugins/edge-tts-middleware.ts` op `/api/tts` (praat server-side met Edge Read Aloud)
3. **GitHub Pages (static)**: browser kan Edge-WebSocket-headers niet zetten → client valt terug op een CORS Edge-relay (`https://tts.reincarnatey.net/v1/audio/speech`), override met `VITE_EDGE_TTS_URL`
4. Optioneel: deploy `workers/edge-tts-worker.js` op Cloudflare Workers en zet `VITE_EDGE_TTS_URL=https://jouw-worker.workers.dev/v1/audio/speech`
5. Als Edge of `audio.play()` faalt → **geen** Web Speech-fallback; duidelijke fouttoast ("Edge-stem mislukt — geen robot-fallback"). iOS: audio-unlock bij eerste tap vóór network-TTS.
6. Stemkeuze EN: `en-US-ChristopherNeural` (default, kalm/documentaire). `en-US-GuyNeural` is dieper maar punchier — niet default.

**CORS op Pages:** de default-relay stuurt `Access-Control-Allow-Origin: *`. Eigen worker moet dat ook doen. Direct `speech.platform.bing.com` vanuit Chrome/Safari/iPhone faalt (custom WS-headers).

**Tags:** `[pause]` / `[long pause]` → ellipsen; overige speech-tags worden gestript (Edge escaped XML in plain text).

### Testen

1. `npm run dev` → Sample / Voorproef / Volledige voice-over
2. Controleer Network: `POST .../api/tts` → `audio/mpeg`
3. **Download MP3** wordt actief na generatie; op iPhone: deelblad → *Bewaar in Bestanden*
4. Production-build zonder eigen proxy: zelfde UI, requests gaan naar de Edge-relay

```bash
# Snelle API-check (lokaal met dev-server)
curl -X POST http://localhost:5173/vox-lux/api/tts \
  -H 'Content-Type: application/json' \
  -d '{"model":"tts-1","input":"Hello from Lux.","voice":"en-US-ChristopherNeural","speed":0.7}' \
  --output /tmp/lux.mp3
```

## English

Lux-only VOX studio. Edge neural TTS (`en-US-ChristopherNeural`) → real MP3 play/download. Vite middleware locally; static Pages uses a CORS Edge relay (or your `VITE_EDGE_TTS_URL` worker). No automatic Web Speech fallback (avoids robotic iOS voices).

## Stack

- Vite 8 · React 19 · TypeScript · Tailwind CSS 4 · lucide-react · edge-tts-universal
