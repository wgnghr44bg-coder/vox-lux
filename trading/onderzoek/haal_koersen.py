"""Haalt 2 jaar uur- en 4-uurskoersen van Bitvavo op naar onderzoek/koersen/ (geen sleutel nodig)."""
import csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from bitvavo import Publiek

MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "koersen")
os.makedirs(MAP, exist_ok=True)
api = Publiek()
for m in ["BTC-EUR", "ETH-EUR", "SOL-EUR"]:
    for iv, n in [("1h", 17520), ("4h", 4380)]:
        c = api.candles(m, iv, n)
        with open(os.path.join(MAP, f"{m}_{iv}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["tijd", "o", "h", "l", "c"])
            for x in c: w.writerow([x["tijd"], x["o"], x["h"], x["l"], x["c"]])
        print(m, iv, len(c), "candles")
