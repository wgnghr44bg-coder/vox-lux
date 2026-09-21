# VOX Lux

YouTube voice studio — **Lux only**. Dutch UI.

Recreatie van [VOX](https://aurora-ocean-terra-prairie.grok.me/) met één stem: **Lux** (oude slaapstem / documentaire).

## Nederlands

### Starten

```bash
cd /workspace/vox-lux
npm install
npm run dev
```

Open de URL die Vite toont (meestal `http://localhost:5173`).

### Build

```bash
npm run build
npm run preview
```

### Functies

- Scripteditor met spraak-chips (Pauze, Fluister, Nadruk, …)
- Voorbeelden: Shorts-hook, Tutorial, Top 5, Review, Storytime, Faceless docu
- Statistieken: woorden, geschatte duur (~150 wpm), tekens
- Alleen stem **Lux** (vooraf geselecteerd)
- Preview via **Web Speech API** (kiest bij voorkeur een lagere/oudere mannenstem)
- Download script als `.txt`
- **Download MP3** blijft disabled: browsers geven geen exportbaar audiobestand via `speechSynthesis`

### TTS-beperkingen

| Mogelijkheid | Status |
|---|---|
| Preview / sample / volle voorlees | ✅ Web Speech API (browserstem ≈ Lux-karakter) |
| Script `.txt` download | ✅ |
| Echte Lux / Grok Voice MP3 | ❌ Niet in deze lokale build |
| MediaRecorder-export van TTS | ❌ `speechSynthesis` speelt niet door een capture-stream |

Gebruik de preview om timing en tekst te checken; exporteer het script en genereeer finale audio elders indien nodig.

## English

Lux-only VOX studio (Dutch UI). Vite + React + TypeScript + Tailwind.

```bash
npm install && npm run dev
```

**TTS note:** Preview uses the browser Web Speech API (prefers older/lower male voices). There is no server-side Lux/Grok voice and no MP3 export from `speechSynthesis` — script download always works; **Download MP3** stays disabled unless a real audio blob is present.

## Stack

- Vite 8 · React 19 · TypeScript · Tailwind CSS 4 · lucide-react
