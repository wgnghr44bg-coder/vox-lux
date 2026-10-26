"""Standaardstem (gratis, op de pc): Chatterbox doet Kokoro bm_george na, rustig (eigenaar 13 okt 2026).

Maakt van een script (zelfde opmaak als voor xAI: {img:ID} op een eigen regel, [pause] / [long pause])
<map>/voice.mp3 + <map>/voice-times.tsv (tijden in s, stem start op 0,8 s; zelfde kolommen als alteraqon/make_voice.py).
Proef van de stem: tools/comfy/stem/standaardstem-proef.mp3. Voorbeeldstem voor Chatterbox: tools/comfy/stem/voorbeeld-george.mp3.

Installeren: zie voice_test_local.py (aparte omgeving met chatterbox-tts; ffmpeg op PATH).
Gebruik (vanuit de map vox-lux, stem-env actief):
  python tools/comfy/make_voice_local.py <map>                     # leest <map>/script-cues.txt
  python tools/comfy/make_voice_local.py <map> --script script.txt --dry-run   # alleen de zinnen tonen
"""
import argparse, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import xai_voiceover as xv                                   # alleen voor het opsplitsen van het script (geen xAI-aanroep)

REF = os.path.join(HERE, "stem", "voorbeeld-george.mp3")
EXAGGERATION, CFG = 0.4, 0.5                                 # "rustig" uit de stemtest
SPEED = 0.87      # tempo van de Titanic-stem (eigenaar 26 okt 2026): George spreekt ± 5,3 lettergrepen/s, Titanic ± 4,5
LEAD = 0.8

ap = argparse.ArgumentParser()
ap.add_argument("map"); ap.add_argument("--script", default="script-cues.txt")
ap.add_argument("--pause-ms", type=int, default=900); ap.add_argument("--long-pause-ms", type=int, default=1700)
ap.add_argument("--sentence-pause-ms", type=int, default=600); ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--speed", type=float, default=SPEED, help="1.0 = Chatterbox zelf; lager = langzamer, zelfde toonhoogte")
a = ap.parse_args()
xv.PAUSE_MS, xv.LONG_PAUSE_MS, xv.SENTENCE_PAUSE_MS = a.pause_ms, a.long_pause_ms, a.sentence_pause_ms
pieces = xv.split_script(open(os.path.join(a.map, a.script), encoding="utf-8").read())
pieces = [xv.Piece(" ".join(xv.TAG_RE.sub("", p.text).split()), p.silence_after_ms, p.cue) for p in pieces]
for i, p in enumerate(pieces, 1):
    print(f"{i:>3}. {p.cue or '':>5} {p.text[:70]!r} + {p.silence_after_ms} ms")
if a.dry_run: sys.exit()

import torch, torchaudio as ta
from chatterbox.tts import ChatterboxTTS
model = ChatterboxTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
sr = model.sr
tmp_dir = tempfile.mkdtemp()

def slower(wav):
    """Zelfde toonhoogte, ander tempo (ffmpeg atempo)."""
    if abs(a.speed - 1) < 1e-3:
        return wav
    src, dst = os.path.join(tmp_dir, "in.wav"), os.path.join(tmp_dir, "out.wav")
    ta.save(src, wav, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"atempo={a.speed}", dst], check=True)
    return ta.load(dst)[0]

parts, rows, t = [torch.zeros(1, int(LEAD * sr))], [], LEAD
for i, p in enumerate(pieces, 1):
    wav = slower(model.generate(p.text, audio_prompt_path=REF, exaggeration=EXAGGERATION, cfg_weight=CFG))
    d = wav.shape[1] / sr
    rows.append(f"{i}\t{t:.2f}\t{t + d:.2f}\t{p.cue}\t{p.text}")
    parts += [wav, torch.zeros(1, int(p.silence_after_ms / 1000 * sr))]
    t += d + p.silence_after_ms / 1000
    print(f"klaar {i}/{len(pieces)}")
with tempfile.TemporaryDirectory() as tmp:
    ta.save(os.path.join(tmp, "voice.wav"), torch.cat(parts, dim=1), sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, "voice.wav"), "-b:a", "192k",
                    os.path.join(a.map, "voice.mp3")], check=True)
with open(os.path.join(a.map, "voice-times.tsv"), "w", encoding="utf-8") as f:
    f.write("#\tstart\tend\timage\ttext\n" + "\n".join(rows) + "\n")
print(f"voice.mp3 + voice-times.tsv: {len(rows)} regels, stem eindigt op {t:.1f} s")
