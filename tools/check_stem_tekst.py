"""Controle of de stem precies het script zegt (eigenaar, 31 okt 2026: "Oregon slaat dubbel in het begin met
woord ... zorg dat er een controle komt op dit soort dingen").

Whisper (lokaal, gratis) schrijft elke zin van <map>/video/stem-met-pauzes.wav uit (tijden uit tijdlijn-pauzes.tsv) en legt hem naast
de tekst van die zin. Gemeld wordt: dubbele woorden (stem zegt een woord twee keer)
en weggevallen woorden, met de tijd in de video. Getallen, leestekens en spelling tellen niet.

Draaien met de OmniVoice-omgeving (heeft torch + transformers + Whisper):
  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/check_stem_tekst.py stories/<map> [--wav ...]
Exitcode 0 en "TEKST GOED" = stem zegt wat er staat; anders de genoemde plekken eerst herstellen.
"""
import argparse, difflib, re, sys

import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_video as cv

ap = argparse.ArgumentParser()
ap.add_argument("story", type=Path)
ap.add_argument("--wav", type=Path, help="standaard <map>/video/stem-met-pauzes.wav")
ap.add_argument("--zinnen", type=int, help="alleen de eerste N zinnen (test)")
ap.add_argument("--toon", action="store_true", help="laat per zin zien wat Whisper hoort")
a = ap.parse_args()
wav = a.wav or a.story / "video" / "stem-met-pauzes.wav"

import torch
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0",
               torch_dtype=torch.float16)


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))


x = cv.pcm(["-i", str(wav)], 16000) / 32768
# per zin (tijden uit tijdlijn-pauzes.tsv): betrouwbaarder dan lange stukken (geen woorden dubbel op de knip)
rows = [l.split("	") for l in open(a.story / "tijdlijn-pauzes.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
sec = lambda v: sum(float(p) * f for p, f in zip(v.split(":"), (3600, 60, 1)))
rows = rows[:a.zinnen] if a.zinnen else rows
tijden = [(sec(r[1]), sec(r[2])) for r in rows]
stukken = []
for i, (t0, t1) in enumerate(tijden):
    lo = max(t0 - 0.4, tijden[i - 1][1] if i else 0)
    hi = min(t1 + 0.4, tijden[i + 1][0] if i + 1 < len(tijden) else t1 + 0.4)
    stukken.append({"raw": x[int(lo * 16000):int(hi * 16000)], "sampling_rate": 16000})
# Whisper laat herhalingen normaal weg ("we are we are going" -> "we are going"); met dit voorbeeld schrijft
# hij letterlijk op wat er gezegd wordt (Oregon, 31 okt 2026: zo pas gevonden)
LETTERLIJK = asr.tokenizer.get_prompt_ids("Um, so, so we we went, uh, to to the the old house. I I mean, it it was",
                                          return_tensors="pt").to("cuda:0")
uit = []                                                    # los per zin: als lijst negeert de pipeline prompt_ids
for k, st in enumerate(stukken):
    uit.append(asr(st, generate_kwargs={"language": "en", "prompt_ids": LETTERLIJK, "num_beams": 1}))
    if k % 50 == 0:
        print(f"  zin {k}/{len(stukken)}", end="\r", flush=True)

STOP = {"the", "a", "an", "and", "of", "to", "in", "on", "at", "is", "it", "for", "with", "as", "or", "but"}
fouten = []
for r, (t0, _), u in zip(rows, tijden, uit):
    tekst = re.sub(r"[—–-]", " ", r[4])
    sw = [norm(w) for w in tekst.split() if norm(w)]
    hw = [norm(w) for w in u["text"].replace("-", " ").split() if norm(w)]
    if a.toon:
        print(r[0], u["text"])
    if hw[:3] == ["um", "so", "so"]:                        # soms zet Whisper het voorbeeld zelf ervoor
        print("  (voorbeeld herhaald, zin overgeslagen)", r[0])
        continue
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, sw, hw, autojunk=False).get_opcodes():
        if op == "equal" or any(c.isdigit() for c in " ".join(sw[i1:i2] + hw[j1:j2])):
            continue
        s_, h_ = " ".join(sw[i1:i2]), " ".join(hw[j1:j2])
        if op == "insert" and set(hw[j1:j2]) <= {"um", "uh", "so"}:
            continue
        if op == "insert" and all(w in hw[max(j1 - 3, 0):j1] + hw[j2:j2 + 3] for w in hw[j1:j2]):
            fouten.append((t0, "DUBBEL", s_, h_, r[4]))
        elif op == "delete" and (i2 - i1 >= 2 or sw[i1] not in STOP):
            fouten.append((t0, "weg", s_, h_, r[4]))
        elif op == "replace" and (i2 - i1) - (j2 - j1) >= 2:
            fouten.append((t0, "weg", s_, h_, r[4]))

# losse luide geluidjes tussen stiltes (stem blijft hangen, bv. "On a ... slow afternoon"); zachte tikjes haalt
# tools/stil_tikjes.py weg, deze niet: die zin opnieuw inspreken
import bisect
starts = [t0 for t0, _ in tijden]
for t in cv.hang_plekken(wav):
    if t > tijden[-1][1] + 1 or np.abs(x[int((t - .05) * 16000):int((t + .3) * 16000)]).max() <= 0.1:
        continue
    k = max(bisect.bisect_right(starts, t + 0.3) - 1, 0)
    k = k if tijden[k][1] > t or k + 1 == len(rows) else k + 1
    fouten.append((t, "HANGT", "", "los geluidje", rows[k][4]))
zin_nr = {r[4]: r[0] for r in rows}
fouten.sort()
for tijd, soort, s_, h_, zin in fouten:
    print(f"zin {zin_nr[zin]:>4} {int(tijd // 60)}:{tijd % 60:04.1f}  {soort:6}  script: {s_!r:24} stem: {h_!r:24} | {zin[:70]}")
print(f"{len(rows)} zinnen gecontroleerd, {len(fouten)} plekken met dubbele, weggevallen of hangende woorden")
if fouten:
    print("TEKST FOUT: deze zinnen opnieuw laten inspreken: tools/herstel_zinnen.py", a.story,
          " ".join(sorted({zin_nr[f[4]] for f in fouten}, key=int)))
    sys.exit(1)
print("TEKST GOED")
