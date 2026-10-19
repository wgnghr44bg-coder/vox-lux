"""Alteraqon: eenvoudige eigen achtergrondmuziek voor lange video's (zelf gesynthetiseerd, geen auteursrecht, gratis).

Gebruik:  python alteraqon/tools/make_music.py alteraqon/<map> [--mood dark|hopeful]
Leest de lengte uit voice-times.tsv en schrijft <map>/music.mp3: donkere filmische pads + lage drone, langzaam wisselende
akkoorden (A-mineur), zachte pulse in het midden, rustig einde. make_video.py mixt hem zacht onder de stem (LONG = True).
"""
import argparse, csv, os, subprocess, tempfile, wave
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("map"); ap.add_argument("--mood", default="dark")
a = ap.parse_args()
rows = [r for r in csv.reader(open(os.path.join(a.map, "voice-times.tsv"), encoding="utf-8"), delimiter="\t") if not r[0].startswith("#")]
END = float(rows[-1][2]) + 4
SR = 44100; N = int(END * SR); t = np.arange(N) / SR
rng = np.random.default_rng(7)
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]] if a.mood == "dark" else [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
L = np.zeros(N); R = np.zeros(N)
seg = 8.0
for k in range(int(END // seg) + 1):
    s0 = int(k * seg * SR); s1 = min(N, int((k + 1) * seg * SR) + SR)
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR
    e = np.sin(np.pi * np.clip(tt / (seg + 1), 0, 1)) ** 1.5
    for i, m in enumerate(prog[k % len(prog)]):
        f = hz(m - 12)
        v = sum(np.sin(2 * np.pi * f * (1 + d) * tt + rng.uniform(0, 6)) for d in (-0.003, 0, 0.003)) / 3
        L[s0:s1] += 0.10 * v * e * (1.0 if i % 2 else 0.7); R[s0:s1] += 0.10 * v * e * (0.7 if i % 2 else 1.0)
drone = 0.12 * np.sin(2 * np.pi * hz(33) * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t))
mid = ((t > END * 0.3) & (t < END * 0.75)).astype(float)
pulse = 0.05 * np.sin(2 * np.pi * hz(45) * t) * (np.sin(2 * np.pi * 1.0 * t) > 0.6) * mid
L += drone + pulse; R += drone + pulse
fade = np.minimum(1, np.minimum(t / 4, (END - t) / 6))
L *= fade; R *= fade
mx = max(np.abs(L).max(), np.abs(R).max()) or 1
st = (np.stack([L, R], 1) / mx * 0.8 * 32767).astype(np.int16)
tmp = tempfile.mktemp(suffix=".wav")
with wave.open(tmp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
out = os.path.join(a.map, "music.mp3")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "lowpass=f=3000", "-b:a", "160k", out], check=True)
os.remove(tmp)
print(out, f"{END:.1f} s")
