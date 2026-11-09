import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backtest  # noqa: E402
import smc  # noqa: E402
import strategie  # noqa: E402
from test_bot import maak_candles  # noqa: E402


def pad_naar_candles(punten):
    prijzen = []
    for a, b, n in punten:
        prijzen += [a + (b - a) * k / n for k in range(1, n + 1)]
    uit, vorige = [], prijzen[0]
    for i, p in enumerate(prijzen):
        uit.append({"tijd": i, "o": vorige, "h": max(vorige, p) + 0.2, "l": min(vorige, p) - 0.2, "c": p})
        vorige = p
    return uit


def test_bos_en_choch():
    c = pad_naar_candles([(100, 110, 10), (110, 104, 6), (104, 116, 12), (116, 108, 8),
                          (108, 112, 4), (112, 100, 12), (100, 101, 8)])
    st = smc.structuur(c, swing=3)
    soorten = [(s, r) for _, s, r in st["gebeurtenissen"]]
    assert soorten[0] == ("BOS", "op")
    assert ("CHoCH", "neer") in soorten
    assert st["trend"] == "neer"


def test_zone_na_breuk_omhoog():
    c = pad_naar_candles([(100, 110, 10), (110, 104, 6), (104, 116, 12), (116, 113, 3)])
    st = smc.structuur(c, swing=3)
    assert st["trend"] == "op" and st["zones"]
    z = st["zones"][-1]
    assert 103 < z["laag"] < 105 and z["laag"] < z["hoog"]


def test_signalen_kloppen():
    c = maak_candles(4000, seed=7)
    gevonden = 0
    for i in range(250, len(c)):
        s = strategie.signaal(c[:i], {"soort": "smc", "min_risico_pct": 0})
        if s:
            gevonden += 1
            assert s["richting"] == "koop"
            assert s["stop"] < s["zone"][0] <= s["zone"][1] < s["instap"] < s["doel"]
            sl = [x["c"] for x in c[:i]]
            assert s["instap"] > smc.sma(sl, 200)[-1]          # boven SMA 200
    assert gevonden > 0


def test_backtest_snel_genoeg():
    c = maak_candles(3000, seed=2)
    t0 = time.time()
    backtest.simuleer(c, {"soort": "smc"}, alleen_koop=True, kosten_pct=0.25)
    assert time.time() - t0 < 120


def test_kies_strategie():
    cfg = {"soort": "trend", "trend": {"trend": 200, "snel": 20}, "smc": {"swing": 5}}
    assert strategie.kies(cfg) == ("trend", {"trend": 200, "snel": 20, "soort": "trend"})
    assert strategie.kies({**cfg, "soort": "smc"})[1]["swing"] == 5
    soort, p = strategie.kies(cfg)
    assert strategie.kies(p) == (soort, p)          # twee keer kiezen geeft hetzelfde
