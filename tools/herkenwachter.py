"""Herkenwachter (eigenaar 24 nov 2026, na een stuk gamestoel dat op een telefoon leek: "pas de controle aan, ik blijf niet
elke keer zelf testen").

Elk voorwerp dat de renderer via de scènewachter meldt (WACHT.plaats), wordt los uitgeknipt op het moment dat het in beeld is
(zonder camera-zoom, zonder koppen/ondertitels), met een rood kader eromheen en een NUMMER, zonder naam. Een nakijk-hulpje dat
het verhaal niet kent, moet per nummer zeggen wat het is (tools/NAKIJKEN.md, laag 4). Noemt het iets anders dan bedoeld
(sleutel.json), dan is het voorwerp onherkenbaar getekend -> opnieuw tekenen.

  python tools/herkenwachter.py <renderer-map> [module=maak_miljoen] [stap=0.5]
Uitvoer: <map>/herkennen/blad-NN.jpg (12 per blad) + sleutel.json (nummer -> bedoelde naam, achtergrond, tijd).
"""
import importlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def main():
    map_ = Path(sys.argv[1]).resolve(); mod = sys.argv[2] if len(sys.argv) > 2 else "maak_miljoen"
    stap = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    sys.path.insert(0, str(map_)); m = importlib.import_module(mod)
    for t in np.arange(0, m.EIND, stap): m.frame(float(t))           # verzamelt WACHT.gezien
    uit = map_ / "herkennen"; uit.mkdir(exist_ok=True)
    for f in uit.glob("*"): f.unlink()
    m.ZOOM_AAN = False; m.TEKST_AAN = False
    f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)
    sleutel, crops = {}, []
    for (naam, bg), lijst in sorted(m.WACHT.gezien.items(), key=lambda kv: kv[1][0][0]):
        t, box = lijst[len(lijst) // 2]                                  # midden van de tijd dat het in beeld is
        x0, y0, x1, y1 = box
        if x1 < 0 or x0 > m.W: continue                                  # (nog) buiten beeld
        im = m.frame(t); mg = 70
        c = im.crop((max(0, int(x0 - mg)), max(0, int(y0 - mg)), min(m.W, int(x1 + mg)), min(m.H, int(y1 + mg))))
        d = ImageDraw.Draw(c); ox, oy = max(0, int(x0 - mg)), max(0, int(y0 - mg))
        d.rectangle((x0 - ox - 6, y0 - oy - 6, x1 - ox + 6, y1 - oy + 6), outline=(255, 0, 0), width=5)
        c.thumbnail((600, 400)); vak = Image.new("RGB", (620, 470), "white"); vak.paste(c, ((620 - c.width) // 2, 60))
        nr = len(crops) + 1; ImageDraw.Draw(vak).text((12, 8), f"#{nr}", font=f, fill=(200, 0, 0))
        crops.append(vak); sleutel[nr] = {"naam": naam, "achtergrond": bg, "t": round(t, 1)}
    for b in range(0, len(crops), 12):
        pl = Image.new("RGB", (620 * 3, 470 * 4), (200, 200, 200))
        for i, c in enumerate(crops[b:b + 12]): pl.paste(c, (620 * (i % 3), 470 * (i // 3)))
        pl.save(uit / f"blad-{b // 12:02d}.jpg", quality=85)
    (uit / "sleutel.json").write_text(json.dumps(sleutel, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"KLAAR: {len(crops)} voorwerpen op {(len(crops) + 11) // 12} bladen -> {uit}")

if __name__ == "__main__":
    main()
