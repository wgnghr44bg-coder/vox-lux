"""Na het bouwen van scene.json (eigenaar 22 nov: "beelden lopen over elkaar heen"):
1) per bord nooit twee dingen tegelijk tekenen: start = max(kernwoord, einde vorige + 0.15); loopt het te ver uit, dan sneller tekenen
   (minimaal 1.2 s voor een tekening, 0.6 s voor tekst);
2) controle of vakken (tekening/foto/tekst/grafiek) op elkaar liggen -> melding met de twee onderdelen.
  python volgorde.py scene.json"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
FH = "C:/Windows/Fonts/segoeprb.ttf"
p = sys.argv[1]; sc = json.load(open(p, encoding="utf-8")); its = sc["items"]
TEKEN = ("beeld", "foto", "tekst", "streep")
def is_f(i): return "personage" in i.get("beeld", "")
for bord in sorted({i.get("bord", -1) for i in its}):
    rij = sorted([i for i in its if i.get("bord", -1) == bord and any(k in i for k in TEKEN) and not is_f(i)], key=lambda i: i["start"])
    eind = -1
    for i in rij:
        minimaal = 0.6 if "tekst" in i else 1.2
        if i["start"] < eind + 0.15:
            te_laat = eind + 0.15 - i["start"]; i["start"] = round(eind + 0.15, 2)
            i["teken"] = round(max(minimaal, i.get("teken", 1) - te_laat), 2)
        eind = i["start"] + i.get("teken", 1) + (i.get("kleur", 0) if "beeld" in i or "foto" in i else 0) * 0.5
# overlapcontrole
def vak(i):
    if "beeld" in i or "foto" in i:
        pad = i.get("beeld") or i.get("foto")
        im = Image.open(pad).convert("RGB"); a = np.asarray(im).astype(int)
        if "beeld" in i:
            a[:6], a[-6:], a[:, :6], a[:, -6:] = 255, 255, 255, 255
            ys, xs = np.nonzero(a.min(axis=2) < 245); w0, h0 = xs.max() - xs.min() + 12, ys.max() - ys.min() + 12
        else: h0, w0 = a.shape[:2]
        s = min(i["breed"] / w0, i.get("hoog", 10000) / h0); w, h = int(w0 * s), int(h0 * s)
        x = int(i["x"] + (i["breed"] - w) / 2) if i.get("midden") else i["x"]
        extra = 60 if "foto" in i else 0
        return (x, i["y"], x + w, i["y"] + h + extra)
    if "tekst" in i:
        d = ImageDraw.Draw(Image.new("RGB", (10, 10))); b = d.textbbox((i["x"], i["y"]), i["tekst"], font=ImageFont.truetype(FH, i.get("maat", 44)))
        return b
    if "data" in i or "dagen" in i or "balken" in i: return (i["x"], i["y"], i["x"] + i["breed"], i["y"] + i["hoog"])
    if "logo" in i and "data" not in i: return (i["x"], i["y"], i["x"] + int(i["hoog"] * 4.5), i["y"] + i["hoog"])
    return None
fout = 0
for bord in sorted({i.get("bord", -1) for i in its}):
    rij = [(i, vak(i)) for i in its if i.get("bord", -1) == bord and not is_f(i)]
    rij = [(i, v) for i, v in rij if v]
    for a in range(len(rij)):
        for b in range(a + 1, len(rij)):
            (i, v), (j, w) = rij[a], rij[b]
            ox = min(v[2], w[2]) - max(v[0], w[0]); oy = min(v[3], w[3]) - max(v[1], w[1])
            if ox > 8 and oy > 8:
                fout += 1
                naam = lambda q: q.get("tekst") or q.get("beeld") or q.get("foto") or q.get("logo") or q.get("data") or q.get("dagen") or "balken"
                print(f"OVERLAP bord {bord}: {naam(i)}  <->  {naam(j)}  ({ox}x{oy} px)")
# laatste bord: video duurt minstens tot alles af is + 1,2 s
laatste = max(i["start"] + i.get("teken", 0) + (i.get("kleur", 0) if ("beeld" in i or "foto" in i) else 0) for i in its if any(k in i for k in TEKEN))
if laatste + 1.2 > sc["duur"]: print(f"video verlengd: {sc['duur']} -> {round(laatste + 1.2, 2)} s"); sc["duur"] = round(laatste + 1.2, 2)
json.dump(sc, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("volgorde gezet;", "GEEN overlap" if not fout else f"{fout} overlap(s)")
