"""Stem met OmniVoice (engine van VoiceStudio, gratis op de pc): kloont een stem uit een korte opname.

Zelfde in- en uitvoer als make_voice_local.py: leest <map>/script-cues.txt en schrijft
<map>/voice.mp3 + <map>/voice-times.tsv (stem start op 0,8 s), dus de rest van de routine blijft gelijk.
Standaardstem sinds 31 okt 2026: "Slaap 3" (eigen ontworpen stem: oudere Britse man, heel laag; ref
stem/slaapstem-3.wav), langzaam (speed 0.8) met lange pauzes. Daarna tools/zachte_stem.py en muziek op -16.6 dB.

Installeren: aparte omgeving C:\\Users\\rane\\omnivoice-venv met torch 2.8 cu128 + `pip install omnivoice`.
Gebruik (vanuit de map vox-lux):
  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/comfy/make_voice_omni.py <map>      # Slaap 3
  ... --ref andere-opname-3-10s.wav --ref-text "..."                                  # andere stem
"""
import argparse, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import xai_voiceover as xv                                   # alleen voor het opsplitsen van het script (geen xAI-aanroep)

LEAD, SR = 0.8, 24000
REF = os.path.join(HERE, "stem", "slaapstem-3.wav")
REF_TEXT = "The evening is quiet now, and the kettle is warming slowly on the stove."

ap = argparse.ArgumentParser()
ap.add_argument("map"); ap.add_argument("--script", default="script-cues.txt")
ap.add_argument("--ref", default=REF); ap.add_argument("--ref-text", help="tekst van --ref (leeg bij een andere --ref: Whisper schrijft hem uit)")
ap.add_argument("--speed", type=float, default=0.8); ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--pause-ms", type=int, default=1500); ap.add_argument("--long-pause-ms", type=int, default=2800)
ap.add_argument("--sentence-pause-ms", type=int, default=1100); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
if a.ref == REF and not a.ref_text: a.ref_text = REF_TEXT
xv.PAUSE_MS, xv.LONG_PAUSE_MS, xv.SENTENCE_PAUSE_MS = a.pause_ms, a.long_pause_ms, a.sentence_pause_ms
pieces = xv.split_script(open(os.path.join(a.map, a.script), encoding="utf-8").read())
pieces = [xv.Piece(" ".join(xv.TAG_RE.sub("", p.text).split()), p.silence_after_ms, p.cue) for p in pieces]
for i, p in enumerate(pieces, 1):
    print(f"{i:>3}. {p.cue or '':>5} {p.text[:70]!r} + {p.silence_after_ms} ms")
if a.dry_run: sys.exit()

import numpy as np, soundfile as sf, torch
from omnivoice import OmniVoice
model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)
prompt = model.create_voice_clone_prompt(ref_audio=a.ref, ref_text=a.ref_text)
parts, rows, t = [np.zeros(int(LEAD * SR), np.float32)], [], LEAD
for i, p in enumerate(pieces, 1):
    torch.manual_seed(a.seed + i)
    wav = model.generate(text=p.text, voice_clone_prompt=prompt, speed=a.speed)[0].astype(np.float32)
    d = len(wav) / SR
    rows.append(f"{i}\t{t:.2f}\t{t + d:.2f}\t{p.cue}\t{p.text}")
    parts += [wav, np.zeros(int(p.silence_after_ms / 1000 * SR), np.float32)]
    t += d + p.silence_after_ms / 1000
    print(f"klaar {i}/{len(pieces)}", flush=True)
with tempfile.TemporaryDirectory() as tmp:
    sf.write(os.path.join(tmp, "voice.wav"), np.concatenate(parts), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, "voice.wav"), "-b:a", "192k",
                    os.path.join(a.map, "voice.mp3")], check=True)
with open(os.path.join(a.map, "voice-times.tsv"), "w", encoding="utf-8") as f:
    f.write("#\tstart\tend\timage\ttext\n" + "\n".join(rows) + "\n")
print(f"voice.mp3 + voice-times.tsv: {len(rows)} regels, stem eindigt op {t:.1f} s")
