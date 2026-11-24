"""Overzicht van alle gebaren (24 nov) -> gebaren.jpg"""
import os
from PIL import Image, ImageDraw
import pop_short as ps
G = [None, "zwaai", "wijs", "juich", "schrik", "denk", "facepalm", "heupen", "klap", "duim", "praat", "armen-open", "stamp", "schouders", "knik", "nee"]
NL = {None: "staan", "zwaai": "zwaaien", "wijs": "wijzen", "juich": "juichen", "schrik": "schrikken", "denk": "denken", "facepalm": "facepalm", "heupen": "handen in zij",
      "klap": "klappen", "duim": "duim omhoog", "praat": "praten", "armen-open": "armen open", "stamp": "stampen", "schouders": "schouders op", "knik": "knikken", "nee": "nee schudden"}
W, Hh = 270, 420; S = ps.SS
pl = Image.new("RGB", (W * 8, Hh * 2), (250, 244, 232))
for i, g in enumerate(G):
    laag = Image.new("RGBA", (W * S, Hh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    ps.poppetje(d, "you", W / 2, 370, 1.05, 0.33, gebaar=g, verbaasd=g in ("schrik",), boos=g in ("heupen", "stamp"))
    laag = laag.resize((W, Hh), Image.LANCZOS); x0, y0 = W * (i % 8), Hh * (i // 8); pl.paste(laag, (x0, y0), laag)
    ImageDraw.Draw(pl).text((x0 + W / 2, y0 + 398), NL[g], font=ps.font(ps.FB, 26), fill=(40, 35, 40), anchor="mm")
pl.save("gebaren.jpg", quality=88); print("gebaren.jpg")
