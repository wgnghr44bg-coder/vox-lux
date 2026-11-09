"""Test de strategie op oude koersen voordat er gehandeld wordt.

  python backtest.py BTC-EUR                    # ±5000 uur-candles van Bitvavo (geen sleutel nodig)
  python backtest.py ETH-EUR --kosten-pct 0.15  # andere kosten per order
  python backtest.py BTC-EUR --csv koersen.csv  # of uit een csv met kolommen tijd,o,h,l,c
Alleen koopsignalen, 0,25% kosten per aan- en verkoop meegerekend.

Uitkomst in R: 1R = het bedrag dat je per trade riskeert (standaard 0,5% van je saldo).
"""
import argparse
import csv
import json
import os

import strategie

MAP = os.path.dirname(os.path.abspath(__file__))


def simuleer(candles, inst_cfg=None, spread=0.0, alleen_koop=False, kosten_pct=0.0):
    p = {**strategie.STANDAARD, **(inst_cfg or {})}
    start = p["trend"] + 2
    trades, i = [], start
    while i < len(candles):
        sig = strategie.signaal(candles[:i], p)
        if not sig or (alleen_koop and sig["richting"] != "koop"):
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
        uitkomst -= sig["instap"] * kosten_pct / 100 * 2 / risico   # kosten bij kopen en verkopen
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
    ap.add_argument("--kosten-pct", type=float, default=0.25, help="kosten per order in %%")
    a = ap.parse_args()
    with open(os.path.join(MAP, "instellingen_bitvavo.json")) as f:
        cfg = json.load(f)
    if a.csv:
        candles = lees_csv(a.csv)
    else:
        from bitvavo import Publiek
        candles = Publiek().candles(a.instrument, cfg["interval"], 5000)
    trades = simuleer(candles, cfg["strategie"], alleen_koop=True, kosten_pct=a.kosten_pct)
    print(f"{a.instrument}: {len(candles)} candles")
    for k, v in rapport(trades, cfg["risico"]["risico_per_trade_pct"]).items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
