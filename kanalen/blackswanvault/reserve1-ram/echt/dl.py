"""Download gekozen Commons-beelden uit zoek-*.json -> <naam>.jpg + regel in bronnen.tsv. Gebruik: python dl.py naam=Titeldeel ..."""
import json, sys, glob, io
from wm import get
from PIL import Image
rows = [r for f in glob.glob("zoek-*.json") for v in json.load(open(f)).values() for r in v]
for a in sys.argv[1:]:
    naam, deel = a.split("=", 1)
    r = next(r for r in rows if deel in r["titel"])
    im = Image.open(io.BytesIO(get(r["url"], raw=True))).convert("RGB")
    im.save(f"{naam}.jpg", quality=92)
    open("bronnen.tsv", "a", encoding="utf-8").write(f'{naam}\t{r["titel"]}\t{r["artist"]}\t{r["lic"]}\t{r["page"]}\n')
    print(naam, im.size, r["lic"], r["titel"][5:70])
