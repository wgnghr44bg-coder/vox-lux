"""Haperingen zoeken in de stem van een video, zonder te luisteren (eigenaar 10 nov 2026: "haperingen moet je controleren
via de pc"). Per zin (voice.mp3 + voice-times.tsv; tijden in de video uit tijdlijn-pauzes.tsv):
  - hik:     een heel kort gat (40-200 ms) midden in een woord/zin, waar de stem even wegvalt
  - stilte:  een stilte > 0,6 s midden in de zin zonder komma/punt op die plek
  - herhaling: hetzelfde stukje klank (0,25-0,6 s) direct twee keer achter elkaar (stotteren)
  - tempo:   zin veel trager of sneller dan de rest (> 40 % afwijking in tekens per seconde)
  - klik:    plotselinge sprong in het geluid (tik/kraak)
Uitvoer: lijst met video-tijd, zinnummer, soort en tekst; laatste regel HAPERINGEN GOED of HAPERINGEN FOUT: <nrs>
(de nummers kun je zo aan engine_stem.py --hergebruik --opnieuw geven).
Gebruik: python tools/hapering_check.py stories/<map> [--json uit.json]
"""
import json, re, subprocess, sys
from pathlib import Path

import numpy as np

SR = 16000
m = Path(sys.argv[1])


def tsv(p):
    return [l.split("\t") for l in p.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]


def t(s):
    s = str(s)
    if ":" in s:
        d = [float(x) for x in s.split(":")]
        return d[0] * 3600 + d[1] * 60 + d[2] if len(d) == 3 else d[0] * 60 + d[1]
    return float(s)


def mmss(s):
    s = int(s)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", str(m / "voice.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout, np.float32)
vt = tsv(m / "voice-times.tsv")
tl = tsv(m / "tijdlijn-pauzes.tsv") if (m / "tijdlijn-pauzes.tsv").exists() else vt
HOP = int(0.01 * SR)                                        # 10 ms frames

cps, gevonden = [], []
for i, r in enumerate(vt):
    a, b, tekst = t(r[1]), t(r[2]), r[4] if len(r) > 4 else ""
    z = y[int(a * SR):int(b * SR)]
    if len(z) < SR // 4:
        continue
    e = np.sqrt(np.convolve(z ** 2, np.ones(HOP) / HOP, "same")[::HOP] + 1e-12)
    db = 20 * np.log10(e + 1e-9)
    ref = np.percentile(db, 90)
    stem = db > ref - 30
    idx = np.where(stem)[0]
    if len(idx) < 10:
        continue
    s0, s1 = idx[0], idx[-1]
    binnen = ~stem[s0:s1]
    # gaten in de spraak
    gaten, n = [], 0
    for k, v in enumerate(list(binnen) + [False]):
        if v:
            n += 1
        elif n:
            gaten.append((s0 + k - n, n))
            n = 0
    leestekens = len(re.findall(r"[,;:—–-]\s", tekst)) + len(re.findall(r"[.!?]\s", tekst))
    lang = [g for g in gaten if g[1] * 0.01 > 0.6]
    if len(lang) > leestekens:
        gevonden.append((i, "stilte", f"{len(lang)} lange stilte(s) midden in de zin"))
    hik = [g for g in gaten if 4 <= g[1] <= 20 and db[g[0]:g[0] + g[1]].min() < ref - 45]
    if len(hik) > 2 + leestekens:
        gevonden.append((i, "hik", f"stem valt {len(hik)}x heel kort weg"))
    # herhaling: spectrum van 0,25-0,6 s vergelijken met het stuk er direct na
    spec = np.abs(np.fft.rfft(z[: len(z) // 512 * 512].reshape(-1, 512) * np.hanning(512), axis=1))[:, 4:120]
    spec = np.log(spec + 1e-6)
    spec = (spec - spec.mean(1, keepdims=True)) / (spec.std(1, keepdims=True) + 1e-6)
    beste = 0.0
    for L in range(8, 19):                                  # 0,26-0,6 s bij 512/16000 = 32 ms per frame
        for s in range(0, len(spec) - 2 * L, 2):
            A, B = spec[s:s + L], spec[s + L:s + 2 * L]
            if np.abs(A).sum() == 0:
                continue
            c = float((A * B).mean())
            beste = max(beste, c)
    if beste > 0.82:
        gevonden.append((i, "herhaling", f"zelfde klank twee keer direct achter elkaar (gelijkenis {beste:.2f})"))
    # klik: sprong tussen opeenvolgende samples veel groter dan normaal in deze zin
    d = np.abs(np.diff(z))
    if d.max() > 12 * np.percentile(d, 99.5) and d.max() > 0.25:
        gevonden.append((i, "klik", "plotselinge tik/sprong in het geluid"))
    if len(tekst) > 20:
        cps.append((i, len(tekst) / ((s1 - s0) * 0.01 + 1e-6)))

if cps:
    med = float(np.median([c for _, c in cps]))
    for i, c in cps:
        if abs(c - med) / med > 0.40:
            gevonden.append((i, "tempo", f"{'trager' if c < med else 'sneller'} dan de rest ({c:.1f} tekens/s, normaal {med:.1f})"))

gevonden.sort()
for i, soort, uitleg in gevonden:
    vid = t(tl[i][1]) if i < len(tl) else 0
    print(f"{mmss(vid)}  zin {i + 1:4d}  {soort:9s} {uitleg}  | {vt[i][4][:70] if len(vt[i]) > 4 else ''}")
nrs = sorted({i + 1 for i, _, _ in gevonden})
if "--json" in sys.argv:
    Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(
        [{"zin": i + 1, "soort": s, "uitleg": u, "tijd": t(tl[i][1]) if i < len(tl) else 0} for i, s, u in gevonden], indent=1), encoding="utf-8")
print(f"{len(vt)} zinnen bekeken")
print("HAPERINGEN GOED" if not nrs else f"HAPERINGEN FOUT: {','.join(map(str, nrs))}")
