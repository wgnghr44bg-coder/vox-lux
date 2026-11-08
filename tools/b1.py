"""De vaste stem- en muziekinstellingen: "B1-stem met achtergrondmuziek" (eigenaar 7-8 nov 2026: "Ik wil gewoon dat hij
dezelfde instellingen heeft, dat er geen fouten kunnen zijn in stem en geluid").

Eén bron: audio_engine/B1.json. engine_stem.py, zachte_stem.py, herstel_zinnen.py en engine_muziek.py lezen allemaal
laad(<map>). Een stories/<map>/stem.json mag alleen afwijken als hij "eigenaar_afwijking": "<wat de eigenaar zei>"
bevat; anders wordt B1 gebruikt en komt er een WAARSCHUWING bij elke afwijking. Ontbreekt stem.json, dan is het B1.
"""
import json
from pathlib import Path

B1 = Path(__file__).resolve().parent.parent / "audio_engine" / "B1.json"
GELUID = ("engine_voice", "speed", "seed", "pauze", "klank", "tempo", "muziek_onder", "muziek_seed", "muziek")


def standaard():
    return json.loads(B1.read_text(encoding="utf-8"))


def laad(map_):
    std = standaard()
    std.setdefault("tempo", 1.0)
    sj = Path(map_) / "stem.json"
    if not sj.exists():
        return std
    eigen = json.loads(sj.read_text(encoding="utf-8"))
    if eigen.get("eigenaar_afwijking"):
        print(f"let op: {sj} wijkt bewust af van B1 ({eigen['eigenaar_afwijking']})", flush=True)
        return {**std, **eigen}
    for k in GELUID:
        if k in eigen and eigen[k] != std.get(k) and not (k == "tempo" and float(eigen[k]) == 1.0):
            print(f"WAARSCHUWING: {sj} heeft {k}={eigen[k]!r}, B1 is {std.get(k)!r}: B1 wordt gebruikt", flush=True)
    return std
