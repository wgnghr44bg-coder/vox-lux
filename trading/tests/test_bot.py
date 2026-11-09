import math
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backtest  # noqa: E402
import risico  # noqa: E402
import strategie  # noqa: E402


def maak_candles(n=1500, seed=1):
    rnd = random.Random(seed)
    prijs, uit = 1.10, []
    for i in range(n):
        trend = 0.0004 * math.sin(i / 120)
        o = prijs
        c = o + trend + rnd.gauss(0, 0.0015)
        h, l = max(o, c) + abs(rnd.gauss(0, 0.0007)), min(o, c) - abs(rnd.gauss(0, 0.0007))
        uit.append({"tijd": str(i), "o": o, "h": h, "l": l, "c": c})
        prijs = c
    return uit


def test_ema_en_atr():
    assert strategie.ema([1, 2, 3], 3)[-1] == 2
    e = strategie.ema([1.0] * 50, 10)
    assert abs(e[-1] - 1.0) < 1e-12
    a = strategie.atr(maak_candles(100), 14)
    assert a[13] is not None and all(x > 0 for x in a[13:])


def test_signaal_stop_aan_juiste_kant():
    c = maak_candles()
    gevonden = 0
    for i in range(210, len(c)):
        s = strategie.signaal(c[:i])
        if s:
            gevonden += 1
            if s["richting"] == "koop":
                assert s["stop"] < s["instap"] < s["doel"]
            else:
                assert s["doel"] < s["instap"] < s["stop"]
    assert gevonden > 0


def test_units_risico():
    # 10.000 saldo, 0,5% = 50 risico, stop 0,0020 weg, factor 0,9 -> 50/(0,0020*0,9)=27777
    assert risico.units_berekenen(10000, 1.1000, 1.0980, 0.9) == 27777
    assert risico.units_berekenen(10000, 1.1, 1.1, 0.9) == 0
    assert risico.units_berekenen(10**9, 1.1, 1.0, 1.0) == risico.STANDAARD["max_units"]


def test_dagverlies_en_max_trades():
    with tempfile.TemporaryDirectory() as d:
        pad = os.path.join(d, "dag.json")
        assert risico.mag_handelen(10000, 0, pad=pad)[0]
        assert not risico.mag_handelen(9790, 0, pad=pad)[0]    # 2,1% lager
        assert not risico.mag_handelen(10000, 3, pad=pad)[0]


def test_backtest_draait():
    trades = backtest.simuleer(maak_candles(3000))
    r = backtest.rapport(trades)
    assert r["trades"] == len(trades) > 0
    assert all(t["R"] == -1.0 or t["R"] > 0 for t in trades)
