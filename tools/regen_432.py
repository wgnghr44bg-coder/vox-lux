"""Zachte, heldere regen onder de 432 Hz-muziek (eigenaar, 31 okt 2026: "helder 4 is prima"; vaste achtergrond).

Maakt 5 minuten natuurlijke regen (ruisend waas + duizenden druppels van verschillende grootte, links/rechts los,
naadloos herhaalbaar) en mengt die door <muziek>.wav, 13 dB zachter dan de muziek. Het origineel blijft als
<muziek>-zonder-regen.wav. Draai dit na tools/ambient_432.py en vóór make_video.py (of vóór stil_tikjes.py, dat de
muziek opnieuw onder de stem zet). make_video.py --muziek-db -26 blijft gelijk.

Gebruik: python tools/regen_432.py stories/<map>/video/muziek432.wav
"""
import re, shutil, subprocess, sys, tempfile, wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy.signal import butter, sosfilt

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR, D, NAAD = 44100, 300, 10                   # 5 min regen, 10 s overlap voor een naadloze herhaling
ONDER_MUZIEK = 13.0                            # dB (eigenaar 31 okt 2026, proef "432 mid harder": muziek -26, regen 13 dB eronder)
DICHT, WAAS, LAAG, GROOTTE = 350, 0.25, 5000, 3.5


def regen(seed=9):
    rng = np.random.default_rng(seed)
    dur = D + NAAD; n = int(SR * dur); t = np.arange(n) / SR
    f = lambda x, typ, fr, o=2: sosfilt(butter(o, fr, typ, fs=SR, output="sos"), x)

    def traag(sec):
        xp = np.arange(0, dur + 2 * sec, sec)
        return np.interp(t, xp, rng.uniform(0, 1, len(xp)))
    out = np.zeros((n, 2))
    for c in range(2):
        w = rng.standard_normal(n); w = f(w, "bandpass", [250, 6000]) + 0.5 * f(w, "lowpass", 400)
        w = f(w, "lowpass", 3500, 1)
        out[:, c] += w / np.abs(w).max() * WAAS * (0.8 + 0.2 * traag(4))
        dicht = DICHT * (1 + 0.6 * traag(5)); k = 0.0
        while True:
            k += rng.exponential(1 / dicht[min(int(k * SR), n - 1)]); a = int(k * SR)
            if a >= n - 2000:
                break
            g = rng.pareto(GROOTTE); L = int(SR * min(0.0015 + 0.004 * g, 0.03))
            d = rng.standard_normal(L) * np.exp(-np.arange(L) / max(L / 4, 1))
            lo = max(4500 / (1 + g), 600)
            out[a:a + L, c] += f(d, "bandpass", [lo, min(lo * 3, 12000)], 1) * min(0.02 + 0.06 * g, 0.35)
    out = np.stack([f(out[:, c], "lowpass", LAAG) for c in range(2)], 1)
    for dly, gg in ((0.009, 0.3), (0.021, 0.2), (0.034, 0.12)):          # buitenklank
        s = int(dly * SR); out[s:] += out[:-s][:, ::-1] * gg
    m = int(NAAD * SR); r = np.linspace(0, 1, m)[:, None]                  # einde over het begin: naadloze lus
    out[:m] = out[:m] * r + out[-m:] * (1 - r)
    out = out[:-m]
    return out / np.abs(out).max() * 0.8


def lufs(pad, sec=600):
    uit = subprocess.run([FF, "-hide_banner", "-nostats", "-t", str(sec), "-i", str(pad), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", uit)[-1])


muziek = Path(sys.argv[1])
orig = muziek.with_name(muziek.stem + "-zonder-regen.wav")
if not orig.exists():
    shutil.move(muziek, orig)
with tempfile.TemporaryDirectory() as tmp:
    r = Path(tmp) / "regen.wav"
    with wave.open(str(r), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((regen() * 32767).astype("<i2").tobytes())
    gain = lufs(orig) - ONDER_MUZIEK - lufs(r)
    subprocess.run([FF, "-v", "error", "-y", "-i", str(orig), "-stream_loop", "-1", "-i", str(r), "-filter_complex",
                    f"[1:a]volume={gain:.2f}dB,aresample=44100[r];[0:a][r]amix=inputs=2:duration=first:normalize=0",
                    "-ar", "44100", str(muziek)], check=True)
print(f"regen erbij ({ONDER_MUZIEK} dB onder de muziek) -> {muziek} (zonder regen: {orig.name})")
