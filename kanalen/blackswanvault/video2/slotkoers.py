"""Na de beurssluiting (19 nov 2026): koers van ANT ophalen (Yahoo, 5 minuten) en de zin {SLOT} in script.txt invullen.
Schrijft data/ant-intraday.json en data/slot.json. Stopt met exit 1 als er nog geen slotkoers is."""
import json, sys, urllib.request
from pathlib import Path
H = Path(__file__).parent; (H / "data").mkdir(exist_ok=True)
UA = {"User-Agent": "BlackSwanVault-research/1.0 (https://www.youtube.com/@blackswanvault)"}
url = "https://query1.finance.yahoo.com/v8/finance/chart/ANT?range=1d&interval=5m"
r = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())
res = r["chart"]["result"][0]; meta = res["meta"]
closes = [v for v in res["indicators"]["quote"][0]["close"] if v]
if not closes or meta.get("currentTradingPeriod", {}).get("regular", {}).get("end", 0) > meta.get("regularMarketTime", 0) + 600:
    print("NOG GEEN SLOTKOERS", meta.get("regularMarketPrice")); sys.exit(1)
slot = round(meta.get("regularMarketPrice") or closes[-1], 2)
(H / "data/ant-intraday.json").write_text(json.dumps(r), encoding="utf-8")
pct = round(100 * (slot - 83) / 83)

EEN = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TIEN = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def woord(n):
    if n < 20: return EEN[n]
    if n < 100: return TIEN[n // 10] + ("" if n % 10 == 0 else "-" + EEN[n % 10])
    return EEN[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + woord(n % 100))
dol, cent = int(slot), int(round((slot - int(slot)) * 100))
prijs = f"{woord(dol)} dollars" + (f" and {woord(cent)} cents" if cent else "")
if pct > 0: zin = f"By the closing bell, it stood at {prijs}. Still {woord(pct)} percent above the IPO price."
elif pct < 0: zin = f"By the closing bell, it stood at {prijs}. That is {woord(-pct)} percent below the IPO price."
else: zin = f"By the closing bell, it stood at {prijs}, right around the IPO price."
s = (H / "script.txt").read_text(encoding="utf-8")
if "{SLOT}" in s:
    s = s.replace("{SLOT}", zin.replace(". ", ".\n")); (H / "script.txt").write_text(s, encoding="utf-8")
(H / "data/slot.json").write_text(json.dumps({"slot": slot, "pct": pct, "zin": zin}), encoding="utf-8")
print("SLOTKOERS", slot, f"{pct:+d}%", "|", zin)
