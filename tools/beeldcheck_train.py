"""Traint de tweede beeldcontrole: een kleine detector op CLIP-kenmerken, geleerd van echte afgekeurde beelden
(stories/*/afgekeurd/) tegenover goedgekeurde (stories/*/afbeeldingen/). Eerlijk gemeten met 5-voudige kruisvalidatie
(steeds getest op beelden die hij niet gezien heeft). Slaat op: tools/beeldcheck_clip.npz (gewichten + drempel).

  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/beeldcheck_train.py
Draai opnieuw als er nieuwe afgekeurde beelden bij komen (dan wordt hij beter).
"""
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

HIER = Path(__file__).resolve().parent
S = HIER.parent / "stories"
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").eval()
proc = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")


def kenmerken(paden):
    uit = []
    with torch.no_grad():
        for p in paden:
            inp = proc(text=["a photo"], images=Image.open(p).convert("RGB"), return_tensors="pt", padding=True)
            e = model(**inp).image_embeds[0].numpy()
            uit.append(e / np.linalg.norm(e))
    return np.array(uit)


slecht = sorted(p for m in S.iterdir() if (m / "afgekeurd").is_dir() for p in (m / "afgekeurd").glob("*.png"))
goed = sorted(p for m in S.iterdir() if (m / "afgekeurd").is_dir() for p in (m / "afbeeldingen").glob("*.png"))
print(len(slecht), "afgekeurd,", len(goed), "goedgekeurd", flush=True)
X = np.vstack([kenmerken(slecht), kenmerken(goed)])
y = np.array([1] * len(slecht) + [0] * len(goed))


def train(X, y, l2=1.0, stappen=3000, lr=0.5):
    w, b = np.zeros(X.shape[1]), 0.0
    gew = np.where(y == 1, len(y) / (2 * y.sum()), len(y) / (2 * (len(y) - y.sum())))
    for _ in range(stappen):
        p = 1 / (1 + np.exp(-(X @ w + b)))
        g = (p - y) * gew
        w -= lr * (X.T @ g / len(y) + l2 * w / len(y))
        b -= lr * g.mean()
    return w, b


rng = np.random.default_rng(1)
idx = rng.permutation(len(y))
kans = np.zeros(len(y))
for k in range(5):
    test = idx[k::5]
    leer = np.setdiff1d(idx, test)
    w, b = train(X[leer], y[leer])
    kans[test] = 1 / (1 + np.exp(-(X[test] @ w + b)))
drempel = float(np.quantile(kans[y == 0], 0.95))           # hooguit ± 5% goede beelden onterecht afgekeurd
vangt = int((kans[y == 1] > drempel).sum())
vals = int((kans[y == 0] > drempel).sum())
print(f"kruisvalidatie: vangt {vangt}/{y.sum()} afgekeurde beelden, keurt {vals}/{(y == 0).sum()} goede onterecht af "
      f"(drempel {drempel:.3f})")
w, b = train(X, y)
np.savez(HIER / "beeldcheck_clip.npz", w=w, b=b, drempel=drempel)
print("opgeslagen: tools/beeldcheck_clip.npz")
