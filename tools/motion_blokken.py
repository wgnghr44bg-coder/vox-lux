"""Hervatbare versie van tools/motion.py: rendert in blokken van BLOK seconden.
Klare blokken blijven staan, dus na een container-herstart gaat het verder waar het was.
Effecten met een toestand (deeltjes) worden per blok exact vooruitgespoeld vanaf t=0, zonder te
tekenen; daardoor is elk blok precies gelijk aan een render in één keer (geen sprong op de naad).
Gebruik: python3 segmotion.py ROOT in.mp4 out.mp4 --plan motion.json --effecten effecten.tsv"""
import json, subprocess, sys, os
from pathlib import Path

ROOT = Path(sys.argv[1]); sys.path.insert(0, str(ROOT / "tools")); os.chdir(ROOT)
import argparse, numpy as np
import motion as M
from effects import read_list, apply_all, ParticleEffect, Regen, Gloed

BLOK = 600


def spoel(systems, tot, dt):
    """Zelfde toestand als motion.py na frame 0..tot-1: alleen de stappen die willekeur/positie veranderen."""
    for i in range(tot):
        t = i * dt
        for van, eind, eff in systems:
            if not (van <= t <= eind):
                continue
            if isinstance(eff, ParticleEffect):
                eff.parts.step(dt, t)
            elif isinstance(eff, Gloed) and eff.sparks:
                eff.sparks.parts.step(dt, t)
            elif isinstance(eff, Regen):
                eff.y += eff.v * dt
                eff.x += eff.v * eff.slant * dt
                out = eff.y > eff.h + 40
                eff.y[out] = eff.rng.uniform(-200, -20, out.sum())
                eff.x[out] = eff.rng.uniform(-0.2 * eff.w, eff.w, out.sum())
ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--plan"); ap.add_argument("--effecten")
ap.add_argument("--seed", type=int, default=3)
a = ap.parse_args(sys.argv[2:])
FF = M.FF
w, h, fps, dur = M.probe(a.inp)
out = Path(a.out); seg = out.with_name(out.stem + "-blokken"); seg.mkdir(exist_ok=True)
n = int(dur // BLOK) + 1
fb, dt = w * h * 3, 1 / fps

for k in range(n):
    s, e = k * BLOK, min((k + 1) * BLOK, dur)
    f = seg / f"{k:03d}.mp4"
    if f.exists():
        continue
    try:  # slot per blok: meerdere werkers tegelijk zonder dubbel werk
        os.close(os.open(seg / f"{k:03d}.lock", os.O_CREAT | os.O_EXCL))
    except FileExistsError:
        continue
    # zelfde start-toestand als motion.py: zelfde seed, opbouw voor elk blok opnieuw
    c = M.Canvas(w, h); rng = np.random.default_rng(a.seed)
    parts = M.build(json.load(open(a.plan)) if a.plan else {}, c, dur, rng)
    systems = read_list(a.effecten, w, h, rng) if a.effecten else []
    start = round(s * fps); stop = round(e * fps); first = start
    spoel(systems, start, dt)
    dec = subprocess.Popen([FF, "-v", "error", "-ss", f"{first / fps:.6f}", "-i", a.inp, "-frames:v", str(stop - first),
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    tmp = seg / f"tmp-{k:03d}.mp4"
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
                            "-i", "-", "-c:v", "libx264", "-preset", M.PRESET, "-crf", "22", "-pix_fmt", "yuv420p", str(tmp)],
                           stdin=subprocess.PIPE)
    i = first
    while i < stop:
        buf = dec.stdout.read(fb)
        if len(buf) < fb:
            break
        t = i * dt
        act = [p for p in parts if p.a <= t < p.b]
        if act or any(x[0] <= t <= x[1] for x in systems):
            fr = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32) / 255
            fr, _ = apply_all(fr, systems, t, dt)
            for p in act:
                fr = p.draw(fr, t - p.a)
            buf = (np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
        if i >= start:
            enc.stdin.write(buf)
        i += 1
    enc.stdin.close(); dec.stdout.close()
    if enc.wait():
        sys.exit("ffmpeg gaf een fout")
    dec.wait()
    tmp.rename(f)
    print(f"blok {k + 1}/{n} klaar ({e / 60:.0f} min)", flush=True)

if not all((seg / f"{k:03d}.mp4").exists() for k in range(n)):
    sys.exit(0)  # andere werker is nog bezig; die zet het straks aan elkaar
try:
    os.close(os.open(seg / "concat.lock", os.O_CREAT | os.O_EXCL))
except FileExistsError:
    sys.exit(0)
lst = seg / "lijst.txt"
lst.write_text("".join(f"file '{seg.resolve() / f'{k:03d}.mp4'}'\n" for k in range(n)))
tmp = out.with_name("tmp-" + out.name)
subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", a.inp,
                "-map", "0:v", "-map", "1:a?", "-c", "copy", "-movflags", "+faststart", str(tmp)], check=True)
tmp.rename(out)
print("KLAAR", out, flush=True)
