"""Test de strategie op oude koersen voordat er gehandeld wordt.

  python backtest.py EUR_USD                    # haalt ±5000 uur-candles bij OANDA (token nodig)
  python backtest.py EUR_USD --csv koersen.csv  # of uit een csv met kolommen tijd,o,h,l,c
  python backtest.py EUR_USD --spread 0.00012   # spreadkosten per trade meerekenen

Uitkomst in R: 1R = het bedrag dat je per trade riskeert (standaard 0,5% van je saldo).
"""
import argparse
import csv
import json
import os

import strategie

MAP = os.path.dirname(os.path.abspath(__file__))


def simuleer(candles, inst_cfg=None, spread=0.0):
    p = {**strategie.STANDAARD, **(inst_cfg or {})}
    start = p["trend"] + 2
    trades, i = [], start
    while i < len(candles):
        sig = strategie.signaal(candles[:i], p)
        if not sig:
            i += 1
            continue
        risico = abs(sig["instap"] - sig["stop"])
        koop = sig["richting"] == "koop"
        uitkomst, j = None, i
        while j < len(candles):
            c = candles[j]
            geraakt_stop = c["l"] <= sig["stop"] if koop else c["h"] >= sig["stop"]
            geraakt_doel = c["h"] >= sig["doel"] if koop else c["l"] <= sig["doel"]
            if geraakt_stop:            # beide in één candle: voorzichtig, tel als verlies
                uitkomst = -1.0
                break
            if geraakt_doel:
                uitkomst = abs(sig["doel"] - sig["instap"]) / risico
                break
            j += 1
        if uitkomst is None:
            break                       # trade loopt nog aan het eind van de data
        uitkomst -= spread / risico
        trades.append({"tijd": candles[i - 1]["tijd"], "richting": sig["richting"], "R": round(uitkomst, 3)})
        i = j + 1
    return trades


def rapport(trades, risico_pct=0.5):
    if not trades:
        return {"trades": 0}
    r = [t["R"] for t in trades]
    stand = top = diepste = 0.0
    for x in r:
        stand += x
        top = max(top, stand)
        diepste = min(diepste, stand - top)
    winst = sum(1 for x in r if x > 0)
    return {
        "trades": len(r),
        "gewonnen_pct": round(winst / len(r) * 100, 1),
        "totaal_R": round(stand, 2),
        "gemiddeld_R": round(stand / len(r), 3),
        "grootste_daling_R": round(diepste, 2),
        "totaal_pct_saldo_ongeveer": round(stand * risico_pct, 1),
    }


def lees_csv(pad):
    with open(pad, newline="") as f:
        return [{"tijd": r["tijd"], "o": float(r["o"]), "h": float(r["h"]),
                 "l": float(r["l"]), "c": float(r["c"])} for r in csv.DictReader(f)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instrument")
    ap.add_argument("--csv")
    ap.add_argument("--granularity", default="H1")
    ap.add_argument("--spread", type=float, default=0.0, help="spread in prijs, bv. 0.00012 voor EUR_USD")
    a = ap.parse_args()
    with open(os.path.join(MAP, "instellingen.json")) as f:
        cfg = json.load(f)

    if a.csv:
        candles = lees_csv(a.csv)
    else:
        from oanda import Oanda
        api = Oanda()
        candles = api.candles(a.instrument, a.granularity, 5000)
    trades = simuleer(candles, cfg["strategie"], a.spread)
    print(f"{a.instrument}: {len(candles)} candles")
    for k, v in rapport(trades, cfg["risico"]["risico_per_trade_pct"]).items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
