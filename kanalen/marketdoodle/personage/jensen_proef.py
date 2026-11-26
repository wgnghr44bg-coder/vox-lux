"""Proef Jensen Huang in de gewone 2D-poppetjesstijl (26 nov 2026, eigenaar: "hou het op de oude style 2D, hoe kun je Jensen beter laten zien").
Herkenbaar aan vaste kenmerken: nu = zilver haar achterover, dunne rechthoekige bril, zwart leren jack; 1993 = zwart haar met scheiding, groot montuur, polo."""
import os, sys
from pathlib import Path
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
JENSEN_NU = dict(broek=(30, 30, 34), shirt=(32, 32, 36), tee=(16, 16, 18), haar=(205, 205, 212), kapsel="achterover", bril="recht", jack=True, groot=1.05)
JENSEN_1993 = dict(broek=(70, 70, 80), shirt=(40, 58, 110), haar=(22, 22, 26), kapsel="scheiding", bril="groot", polo=True, groot=1.05)
if __name__ == "__main__":
    ps.C["jensennu"] = JENSEN_NU; ps.C["jensen93"] = JENSEN_1993
    W, H, SS = 1080, 1350, ps.SS
    img = Image.open(HIER.parent / "short-nvidia" / "afbeeldingen" / "denny.png").convert("RGB").resize((1080, 1920)).crop((0, 400, 1080, 1750))
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    ps.poppetje(d, "jensen93", 290, 1230, 2.3, 0.3, kijk=0.3, mond=0.0)
    ps.poppetje(d, "jensennu", 790, 1230, 2.3, 0.3, kijk=-0.3, mond=0.0, gebaar="duim")
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); d = ImageDraw.Draw(img)
    for x, t in ((290, "JENSEN 1993"), (790, "JENSEN NOW")): d.text((x, 90), t, font=ps.font(ps.FB, 64), fill=(255, 215, 60), anchor="mm", stroke_width=6, stroke_fill=(20, 20, 30))
    img.save(HIER / "jensen-proef.jpg", quality=92); print("jensen-proef.jpg")
