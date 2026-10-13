"""Tijdlijn voor de 3D-video (Remotion).

Leest voice-times.tsv (gemaakt door tools/comfy/make_voice_local.py op de pc). Ontbreekt die nog,
dan schat het de tijden uit script-cues.txt (proefversie zonder stem).
Schrijft tools/remotion/demo/src/whatif/buried-timeline.ts en kopieert voice.mp3 naar public/buried/.
Gebruik (vanuit vox-lux): python3 alteraqon/2026-10-13-buried-or-cremated/make_timeline.py
"""
import json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import xai_voiceover as xv

DEMO = os.path.join(ROOT, "tools", "remotion", "demo")
OUT_TS = os.path.join(DEMO, "src", "whatif", "buried-timeline.ts")
PUB = os.path.join(DEMO, "public", "buried")
LEAD, PAUSE, LONG, SENT = 0.8, 350, 800, 250
TAIL = 1.6  # beeld blijft na de laatste zin nog even staan

rows, has_voice = [], os.path.exists(os.path.join(HERE, "voice-times.tsv"))
if has_voice:
    for line in open(os.path.join(HERE, "voice-times.tsv"), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        _, s, e, cue, text = line.rstrip("\n").split("\t", 4)
        rows.append((float(s), float(e), cue, text))
else:
    xv.PAUSE_MS, xv.LONG_PAUSE_MS, xv.SENTENCE_PAUSE_MS = PAUSE, LONG, SENT
    t = LEAD
    for p in xv.split_script(open(os.path.join(HERE, "script-cues.txt"), encoding="utf-8").read()):
        text = " ".join(xv.TAG_RE.sub("", p.text).split())
        d = len(text.split()) / 2.5 + text.count("…") * 0.35 + 0.25
        rows.append((t, t + d, p.cue or "", text))
        t += d + p.silence_after_ms / 1000

shots, cur = [], None
for s, e, cue, text in rows:
    if cue:
        start = 0.0 if not shots else s
        cur = {"id": cue, "start": round(start, 2)}
        shots.append(cur)
end = round(rows[-1][1] + TAIL, 2)
for a, b in zip(shots, shots[1:] + [{"start": end}]):
    a["end"] = b["start"]
subs = [{"start": round(s, 2), "end": round(e, 2), "text": text} for s, e, _, text in rows]

os.makedirs(os.path.dirname(OUT_TS), exist_ok=True)
with open(OUT_TS, "w", encoding="utf-8") as f:
    f.write("// Gegenereerd door alteraqon/2026-10-13-buried-or-cremated/make_timeline.py - niet met de hand aanpassen.\n")
    f.write(f"export const HAS_VOICE = {str(has_voice).lower()};\n")
    f.write(f"export const DURATION_S = {end};\n")
    f.write(f"export const SHOTS = {json.dumps(shots, indent=1)};\n")
    f.write(f"export const SUBS = {json.dumps(subs, indent=1, ensure_ascii=False)};\n")
os.makedirs(PUB, exist_ok=True)
if has_voice:
    shutil.copy(os.path.join(HERE, "voice.mp3"), os.path.join(PUB, "voice.mp3"))
print(f"{'echte stem' if has_voice else 'GESCHAT (nog geen stem)'}: {len(shots)} shots, {end:.1f} s")
