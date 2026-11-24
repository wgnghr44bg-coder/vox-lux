"""Tekstcheck (eigenaar 24 nov: "ik zie fouten in de afbeeldingen met tekst, zorg dat alles goed is").
Maakt van elk moment waarop tekst in beeld komt (koppen, prijskaartje, spreadsheet, biljet, tv, telefoon) een beeld op
halve grootte (960x540) en zet ze per 6 op een blad: tekstcheck-N.jpg. Zo is elke tekst leesbaar na te lopen."""
import sys
from PIL import Image, ImageDraw
import maak_miljoen as m

tijden = set()
for sc in m.SC:
    for st, *_ in sc["kop"]: tijden.add(round(st + 0.7, 2))
    for k in ("telefoon", "briefje", "biljet", "tv", "fooi", "huiswerk", "wasbeer", "accu"):
        v = sc.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool): tijden.add(round(v + 0.8, 2))
    for t0, *_ in sc.get("prijs", []): tijden.add(round(t0 + 0.7, 2))
    for t0, *_ in sc.get("sheet", []): tijden.add(round(t0 + 0.7, 2))
    if sc.get("slot"): tijden |= {round(sc["slot"][1] + 1.0, 2), round(sc["slot"][3] + 0.8, 2)}
    if sc.get("telefoon"): tijden |= {1.0, round(m.T_SALDO + 1.0, 2)}
tijden = sorted(t for t in tijden if t < m.EIND)
ims = []
for t in tijden:
    im = m.frame(t).resize((960, 540)); ImageDraw.Draw(im).text((10, 505), f"{int(t // 60)}:{t % 60:04.1f}", fill=(255, 0, 0), font=m.font(m.FB, 26)); ims.append(im)
for v in range(0, len(ims), 6):
    pl = Image.new("RGB", (960 * 2, 540 * 3), "black")
    for i, im in enumerate(ims[v:v + 6]): pl.paste(im, (960 * (i % 2), 540 * (i // 2)))
    pl.save(f"tekstcheck-{v // 6}.jpg", quality=85)
print(len(tijden), "momenten,", (len(ims) + 5) // 6, "bladen")
