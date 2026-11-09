"""Vergelijkt de TradingView Editors' Picks-strategieën op echte Bitvavo-koersen, jaar 1 tegen jaar 2.
Eerst: python haal_koersen.py   Dan: python vergelijk.py
"""
import sys, json, csv, datetime as dt
from multiprocessing import Pool
import os
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S); sys.path.insert(0, os.path.join(S, ".."))
import kandidaten, backtest
TAKER, MAKER = 0.0025, 0.0015

def lees(m, iv):
    return backtest.lees_csv(f"{S}/koersen/{m}_{iv}.csv")

def naar_dag(k):
    out = {}
    for c in k:
        d = c["tijd"] // 86_400_000
        if d not in out: out[d] = {**c, "tijd": d * 86_400_000}
        else:
            o = out[d]; o["h"] = max(o["h"], c["h"]); o["l"] = min(o["l"], c["l"]); o["c"] = c["c"]
    return [out[d] for d in sorted(out)]

def resultaat(k, trades, van, tot):
    """Rendement bij 100% inleg per trade, samengesteld, met kosten. Alleen trades die starten in [van, tot)."""
    eq, piek, dd, n, win = 1.0, 1.0, 0.0, 0, 0
    for t in trades:
        if not (van <= k[t["i_in"]]["tijd"] < tot): continue
        f = (t["p_out"] * (1 - (MAKER if t["maker_out"] else TAKER))) / (t["p_in"] * (1 + (MAKER if t["maker_in"] else TAKER)))
        # laagste punt tijdens de trade voor drawdown
        laag = min(c["l"] for c in k[t["i_in"]:t["i_out"] + 1])
        dd = max(dd, 1 - eq * laag / t["p_in"] / piek)
        eq *= f; piek = max(piek, eq); n += 1; win += f > 1
    return {"rend": round((eq - 1) * 100, 1), "dd": round(dd * 100, 1), "n": n, "win": round(win / n * 100) if n else 0}

def een(taak):
    naam, m, iv = taak
    k = lees(m, "1h") if iv in ("1h", "1d") else lees(m, iv)
    if iv == "1d": k = naar_dag(k)
    tr = kandidaten.STRATEGIEEN[naam](k)
    grens = 1762560000000      # 8 nov 2025 00:00 UTC
    j1 = resultaat(k, tr, 0, grens); j2 = resultaat(k, tr, grens, 10**15)
    hold1 = round((next(c for c in k if c["tijd"] >= grens)["o"] / k[0]["o"] - 1) * 100, 1)
    hold2 = round((k[-1]["c"] / next(c for c in k if c["tijd"] >= grens)["o"] - 1) * 100, 1)
    return naam, m, iv, j1, j2, hold1, hold2

if __name__ == "__main__":
  taken = [(n, m, iv) for n in kandidaten.STRATEGIEEN for m in ["BTC-EUR", "ETH-EUR", "SOL-EUR"]
         for iv in (["1h"] if n == "One Percent A Week" else ["1h", "4h", "1d"])]
  with Pool(4) as p:
    uit = p.map(een, taken)
  json.dump(uit, open(f"{S}/vergelijk.json", "w"))
  print(f"{'strategie':20s} {'markt':8s} {'tf':3s} | {'jaar1 %':>8s} {'dd':>5s} {'n':>4s} {'win':>4s} | {'jaar2 %':>8s} {'dd':>5s} {'n':>4s} {'win':>4s} | vasthouden j1/j2")
  for naam, m, iv, j1, j2, h1, h2 in uit:
    print(f"{naam:20s} {m[:3]:8s} {iv:3s} | {j1['rend']:8.1f} {j1['dd']:5.1f} {j1['n']:4d} {j1['win']:4d} | {j2['rend']:8.1f} {j2['dd']:5.1f} {j2['n']:4d} {j2['win']:4d} | {h1:6.1f} / {h2:6.1f}")
