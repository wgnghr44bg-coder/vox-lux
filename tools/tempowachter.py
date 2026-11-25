"""Tempowachter (eigenaar 25 nov 2026, $1 Million-Short: "It's 6 a.m. Your bank app gaat te snel in een zin, klinkt heel raar").
Controleert de stem met de Whisper-woordtijden (woorden.json) en zinnen.json:
  1. ZINSGRENS: na een punt/vraagteken/uitroepteken binnen één regel moet een hoorbare pauze zitten (>= MIN_PAUZE s);
     anders plakt de stem twee zinnen aan elkaar ("a.m. Your bank app").
     Alleen voor de verteller: personages mogen in één adem roepen ("Mom! Dad! Check your phones!").
  2. TEMPO: per regel niet sneller dan MAX_WPM woorden per minuut (lange video ± 178 klinkt goed).
  python tools/tempowachter.py <map-met-zinnen.json-en-woorden.json>   -> TEMPOWACHTER.md, exit 1 bij fouten
stem.py van de What If-video's spreekt daarom elke zin LOS in en zet er zelf een pauze tussen.
"""
import json, re, sys
from pathlib import Path
import numpy as np, soundfile as sf

MIN_PAUZE, MAX_WPM = 0.15, 215                           # tempo alleen bij regels van 8+ woorden (korte uitroepen zijn vanzelf snel)
AFK = {"mr.", "mrs.", "dr.", "st.", "a", "p"}                # "a.m." aan het eind van een zin telt WEL (eigenaar: "6 a.m. Your bank app")

def stilte(a, sr, t0, t1, drempel):                       # langste stil stuk (20 ms-vakjes onder de drempel) tussen t0 en t1
    i0, i1 = max(0, int(t0 * sr)), min(len(a), int(t1 * sr)); n = int(0.02 * sr); best = cur = 0
    for k in range(i0, i1 - n, n):
        if np.sqrt((a[k:k + n] ** 2).mean()) < drempel: cur += 0.02; best = max(best, cur)
        else: cur = 0
    return best

def controleer(map_):
    Z = json.loads((map_ / "zinnen.json").read_text(encoding="utf-8")); W = json.loads((map_ / "woorden.json").read_text(encoding="utf-8"))
    AUD, sr = sf.read(map_ / "stem.wav", dtype="float32"); AUD = AUD.mean(axis=1) if AUD.ndim > 1 else AUD
    fout = []
    for i, z in enumerate(Z):
        seg = AUD[int(z[0] * sr):int(z[1] * sr)]; drempel = np.sqrt((seg ** 2).mean()) * 0.12 if len(seg) else 0.01
        n = len(z[2].split()); d = z[1] - z[0]; wpm = n / d * 60 if d > 0 else 0
        if n >= 8 and wpm > MAX_WPM: fout.append(f"regel {i} ({z[4]}): {wpm:.0f} woorden/min (max {MAX_WPM}): {z[2][:70]}")
        ww = [w for w in W if w[0] == i]
        for v, b in zip(ww, ww[1:]):
            if z[4] == "N" and re.search(r"[.!?]$", v[1]) and v[1].lower() not in AFK and b[1][:1].isalpha():
                p_ = stilte(AUD, sr, v[3] - 0.3, b[2] + 0.15, drempel)
                if p_ < MIN_PAUZE: fout.append(f"regel {i} ({z[4]}): geen pauze na '{v[1]}' -> '{b[1]}' (stilte {p_:.2f} s)")
    return fout

if __name__ == "__main__":
    m = Path(sys.argv[1]); f = controleer(m)
    (m / "TEMPOWACHTER.md").write_text("# Tempowachter\n\n**%d fouten**\n\n" % len(f) + "".join(f"- {x}\n" for x in f), encoding="utf-8")
    for x in f: print(x)
    print("TEMPOWACHTER:", len(f), "fouten"); sys.exit(1 if f else 0)
