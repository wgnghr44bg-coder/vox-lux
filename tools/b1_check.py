"""Controle: klinken stem en muziek nog precies als de vaste B1 met W3? (eigenaar 8 nov 2026: "zorg dat ik precies
dezelfde stem en muziek heb").

Maakt met audio_engine/B1.json één vaste zin met de B1-stem en 20 s W3-muziek, en vergelijkt die met het vastgelegde
voorbeeld in audio_engine/B1-referentie/. Draai dit vóór een nieuwe video en na elke update van de pc (Python, torch,
OmniVoice, ffmpeg). Geeft B1 GOED of B1 AFWIJKING (en dan geen video maken, eerst uitzoeken).

  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/b1_check.py            # vergelijken
  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/b1_check.py --vastleggen  # voorbeeld opnieuw vastleggen (alleen met OK eigenaar)
"""
import json, sys, tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent / "audio_engine"))
import numpy as np, soundfile as sf, librosa
import b1
from voice import omnivoice_engine as ov
from voice.batch_generator import trim
from voice.voice_config import VoiceConfig
from music.composition_engine import preset
from music.music_studio import generate

REF = HIER.parent / "audio_engine" / "B1-referentie"
ZIN = "Every window in Britain had to go completely dark at night. And then, something beautiful appeared in the sky."


def maak(uit):
    s = b1.standaard()
    cfg = VoiceConfig(voice=s["engine_voice"], speed=s["speed"], seed=s["seed"], num_step=s["model"]["num_step"],
                      guidance_scale=s["model"]["guidance_scale"], denoise=s["model"]["denoise"])
    y = trim(ov.speak([ZIN], cfg, seed=s["seed"])[0], ov.SR)
    sf.write(uit / "stem.wav", y, ov.SR)
    with tempfile.TemporaryDirectory() as t:
        generate(preset("referentie", duration=20.0, seed=s["muziek_seed"], **s["muziek"]), Path(t), stems=False,
                 progress=lambda *a: None)
        m, sr = sf.read(Path(t) / "music.wav")
    sf.write(uit / "muziek.wav", m, sr)


def maat(p):
    y, sr = librosa.load(p, sr=16000)
    f0, vf, _ = librosa.pyin(y, fmin=50, fmax=300, sr=16000)
    hz = float(np.nanmedian(f0[vf])) if vf.any() else 0.0
    cen = float(np.median(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))
    return {"duur": round(len(y) / sr, 2), "hz": round(hz, 1), "helderheid": round(cen)}


if "--vastleggen" in sys.argv:
    REF.mkdir(exist_ok=True)
    maak(REF)
    (REF / "maten.json").write_text(json.dumps({"stem": maat(REF / "stem.wav"), "muziek": maat(REF / "muziek.wav")},
                                               indent=1), encoding="utf-8")
    # de stem is sinds 11 nov 2026 de eigen stem van de eigenaar: het geluid niet in de (openbare) repo, alleen op de pc;
    # voor de controle zijn de maten in maten.json genoeg
    PC = Path.home() / "vox-lux-stemmen" / "B1-referentie"
    PC.mkdir(parents=True, exist_ok=True)
    (REF / "stem.wav").replace(PC / "stem.wav")
    print("voorbeeld vastgelegd in", REF, "(stem.wav in", PC, ")")
    sys.exit()

ref = json.loads((REF / "maten.json").read_text(encoding="utf-8"))
with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    maak(t)
    nu = {"stem": maat(t / "stem.wav"), "muziek": maat(t / "muziek.wav")}
    a, _ = librosa.load(REF / "muziek.wav", sr=16000)
    b, _ = librosa.load(t / "muziek.wav", sr=16000)
    n = min(len(a), len(b))
    gelijk_muziek = float(np.corrcoef(a[:n], b[:n])[0, 1])
fout = []
s0, s1 = ref["stem"], nu["stem"]
if abs(12 * np.log2(max(s1["hz"], 1) / s0["hz"])) > 0.7:
    fout.append(f"toonhoogte stem {s1['hz']} Hz, voorbeeld {s0['hz']} Hz")
if abs(s1["helderheid"] - s0["helderheid"]) / s0["helderheid"] > 0.08:
    fout.append(f"klank stem {s1['helderheid']} Hz, voorbeeld {s0['helderheid']} Hz")
if abs(s1["duur"] - s0["duur"]) / s0["duur"] > 0.12:
    fout.append(f"tempo stem {s1['duur']} s, voorbeeld {s0['duur']} s")
if gelijk_muziek < 0.98:
    fout.append(f"muziek wijkt af (gelijkenis {gelijk_muziek:.3f}, moet >= 0.98)")
print("stem nu", s1, "| voorbeeld", s0)
print(f"muziek gelijkenis {gelijk_muziek:.4f}")
print("B1 AFWIJKING: " + "; ".join(fout) if fout else "B1 GOED: stem en muziek zijn hetzelfde als het vaste voorbeeld")
sys.exit(1 if fout else 0)
