"""Tweede ronde (alle Editors' Picks): Adaptive SuperSmoother, Chandelier, Donchian, Dual-Phase 9, RSMK.
Eerst: python haal_koersen.py   Dan: python vergelijk2.py
"""
import sys
from multiprocessing import Pool
import os
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S); sys.path.insert(0, os.path.join(S, ".."))
import kandidaten2 as k2, vergelijk as vh
G = 1762560000000

def hold(k):
    m = next(c for c in k if c["tijd"] >= G)["o"]
    return round((m / k[0]["o"] - 1) * 100, 1), round((k[-1]["c"] / m - 1) * 100, 1)

def een(t):
    naam, m, iv = t
    k = vh.lees(m, "1h") if iv in ("1h", "1d") else vh.lees(m, iv)
    if iv == "1d": k = vh.naar_dag(k)
    tr = k2.STRATEGIEEN[naam](k)
    return naam, m, iv, vh.resultaat(k, tr, 0, G), vh.resultaat(k, tr, G, 10**15), hold(k)

if __name__ == "__main__":
    taken = [(n, m, iv) for n in k2.STRATEGIEEN for m in ["BTC-EUR", "ETH-EUR", "SOL-EUR"] for iv in ["1h", "4h", "1d"]]
    with Pool(4) as p: uit = p.map(een, taken)
    btc = vh.naar_dag(vh.lees("BTC-EUR", "1h"))
    for m in ["ETH-EUR", "SOL-EUR"]:
        tr, kk = k2.rsmk(vh.naar_dag(vh.lees(m, "1h")), btc)
        uit.append(("RSMK t.o.v. BTC", m, "1d", vh.resultaat(kk, tr, 0, G), vh.resultaat(kk, tr, G, 10**15), hold(kk)))
    print(f"{'strategie':24s} {'mkt':4s} {'tf':3s} | {'jaar1 %':>8s} {'dd':>5s} {'n':>4s} {'win':>4s} | {'jaar2 %':>8s} {'dd':>5s} {'n':>4s} {'win':>4s} | vasthouden")
    for naam, m, iv, a, b, h in uit:
        print(f"{naam:24s} {m[:3]:4s} {iv:3s} | {a['rend']:8.1f} {a['dd']:5.1f} {a['n']:4d} {a['win']:4d} | {b['rend']:8.1f} {b['dd']:5.1f} {b['n']:4d} {b['win']:4d} | {h[0]:6.1f} / {h[1]:6.1f}")
