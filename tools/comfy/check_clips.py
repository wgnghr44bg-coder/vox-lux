#!/usr/bin/env python3
"""Visual check of Comfy/Wan clips before they go into an edit (verplichte stap).

Makes one contact sheet per clip: 10 frames (every ~0.5 s) with time stamps, big enough to see faces, jaws and tails.
Look at every sheet (Read the jpg) and check, frame by frame:
  1. Blijft het dier/de persoon dezelfde vorm? (geen ander dier, geen kop die verandert)
  2. Verschijnt er iets wat er niet hoort? (schoen, vlek, extra vin/poot/vinger, tekst)
  3. Smelt of vloeit er iets? (vlekken, uitlopende vormen)
Fout gezien vanaf X s -> clip opnieuw laten maken (andere seed) of in scenes.py USE[<naam>] = X - 0.3.
Usage: python3 tools/check_clips.py <map met clips> [--out <map>] [namen ...]"""
import cv2, numpy as np, sys, os, glob, argparse
ap = argparse.ArgumentParser(); ap.add_argument('dir'); ap.add_argument('names', nargs='*'); ap.add_argument('--out', default=None)
a = ap.parse_args(); out = a.out or os.path.join(a.dir, '..', 'build', 'check'); os.makedirs(out, exist_ok=True)
paths = [os.path.join(a.dir, n if n.endswith('.mp4') else n + '.mp4') for n in a.names] or sorted(glob.glob(os.path.join(a.dir, '*.mp4')))
for p in paths:
    c = cv2.VideoCapture(p); fps = c.get(cv2.CAP_PROP_FPS) or 24; fr = []
    while True:
        ok, f = c.read()
        if not ok: break
        fr.append(f)
    if not fr: print('LEEG', p); continue
    h, w = fr[0].shape[:2]; tw = 240; th = int(h * tw / w)
    tiles = []
    for j in np.linspace(0, len(fr) - 1, 10).astype(int):
        t = cv2.resize(fr[j], (tw, th), interpolation=cv2.INTER_AREA)
        cv2.rectangle(t, (0, 0), (62, 22), (0, 0, 0), -1); cv2.putText(t, f'{j / fps:.1f}s', (4, 16), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 255), 1)
        tiles.append(t)
    sheet = np.vstack([np.hstack(tiles[:5]), np.hstack(tiles[5:])])
    dst = os.path.join(out, os.path.basename(p)[:-4] + '.jpg'); cv2.imwrite(dst, sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f'{os.path.basename(p)}: {len(fr) / fps:.1f}s -> {dst}')
