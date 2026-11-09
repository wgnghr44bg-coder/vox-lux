import json
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bitvavo  # noqa: E402
import risico  # noqa: E402
import trend_bot  # noqa: E402

DAG = 86_400_000


class NepPapier(bitvavo.Papier):
    def __init__(self, pad, prijzen):
        self.prijs_ = dict(prijzen)
        self.dagen_ = {}
        super().__init__(start_eur=1000, pad=pad)

    def boek(self, m):
        p = self.prijs_[m]
        return {"bid": p * 0.9995, "ask": p * 1.0005}

    def market_info(self, m):
        return {"tickSize": "0.01", "minOrderInQuoteAsset": "5", "quantityDecimals": 8}

    def candles(self, m, interval="1d", aantal=300, eind_ms=None):
        return self.dagen_[m][-aantal:]


def dagen(start, eind, n=210):
    t0 = (int(time.time() * 1000) // DAG - n) * DAG
    return [{"tijd": t0 + i * DAG, "o": 0, "h": 0, "l": 0,
             "c": start + (eind - start) * i / (n - 1)} for i in range(n)]


@pytest.fixture
def omg(tmp_path, monkeypatch):
    monkeypatch.setattr(trend_bot, "LOG", str(tmp_path / "log.jsonl"))
    monkeypatch.setattr(trend_bot, "MAP", str(tmp_path))
    monkeypatch.setattr(risico, "NOODSTOP", str(tmp_path / "NOODSTOP"))
    cfg = json.load(open(os.path.join(os.path.dirname(trend_bot.__file__), "instellingen_trend.json")))
    cfg["papier_storting_per_week"] = 0
    api = NepPapier(str(tmp_path / "papier.json"), {"BTC-EUR": 60000, "ETH-EUR": 3000})
    return api, cfg, tmp_path


def test_trend_bepaling():
    assert trend_bot.trend(dagen(100, 200))[0] == "in"
    assert trend_bot.trend(dagen(200, 100))[0] == "uit"
    assert trend_bot.trend(dagen(100, 200, 50))[0] is None


def test_kopen_volgens_verdeling_met_limiet(omg):
    api, cfg, tmp = omg
    api.dagen_ = {"BTC-EUR": dagen(40000, 60000), "ETH-EUR": dagen(2000, 3000)}
    st = trend_bot.ronde(api, cfg)
    assert st["trend"] == {"BTC-EUR": "in", "ETH-EUR": "in"}
    assert set(st["orders"]) == {"BTC-EUR", "ETH-EUR"}
    btc = st["orders"]["BTC-EUR"]
    assert btc["kant"] == "buy" and 690 < btc["aantal"] * btc["prijs"] < 700      # 70% van €1000
    # koers zakt een tikje: limieten gevuld (maker)
    api.prijs_ = {"BTC-EUR": 59900, "ETH-EUR": 2995}
    st = trend_bot.ronde(api, cfg)
    assert st["orders"] == {}
    assert api.st["bezit"]["BTC"] > 0 and api.st["bezit"]["ETH"] > 0
    assert api.st["EUR"] < 10
    pos = json.load(open(tmp / "data" / "posities_bitvavo_papier.json"))
    assert pos["BTC-EUR"]["trend"] == "in" and pos["BTC-EUR"]["instap"] > 59000


def test_limiet_niet_gevuld_dan_markt(omg, monkeypatch):
    api, cfg, tmp = omg
    api.dagen_ = {"BTC-EUR": dagen(40000, 60000), "ETH-EUR": dagen(4000, 3000)}   # ETH onder SMA
    st = trend_bot.ronde(api, cfg)
    assert list(st["orders"]) == ["BTC-EUR"] and st["trend"]["ETH-EUR"] == "uit"
    api.prijs_["BTC-EUR"] = 61000                                               # loopt weg
    nu = time.time()
    monkeypatch.setattr(trend_bot.time, "time", lambda: nu + 16 * 60)
    st = trend_bot.ronde(api, cfg)
    assert "BTC" in api.st["bezit"] and api.st["EUR"] < 310                      # 70% met marktorder
    assert "markt (limiet niet gevuld)" in open(tmp / "log.jsonl").read()


def test_trend_omslag_verkoopt(omg):
    api, cfg, tmp = omg
    api.dagen_ = {"BTC-EUR": dagen(40000, 60000), "ETH-EUR": dagen(2000, 3000)}
    trend_bot.ronde(api, cfg)
    api.prijs_ = {"BTC-EUR": 59900, "ETH-EUR": 2995}
    trend_bot.ronde(api, cfg)
    # volgende dag: BTC onder het gemiddelde
    staat = json.load(open(tmp / "data" / "trendstaat_bitvavo_papier.json"))
    staat["dag"] = "2000-01-01"
    json.dump(staat, open(tmp / "data" / "trendstaat_bitvavo_papier.json", "w"))
    api.dagen_["BTC-EUR"] = dagen(70000, 50000)
    st = trend_bot.ronde(api, cfg)
    assert st["trend"]["BTC-EUR"] == "uit" and st["orders"]["BTC-EUR"]["kant"] == "sell"
    api.prijs_["BTC-EUR"] = 60100                                               # verkooplimiet gevuld
    trend_bot.ronde(api, cfg)
    assert "BTC" not in api.st["bezit"] and api.st["EUR"] > 650
    assert "omslag" in open(tmp / "log.jsonl").read()


def test_noodstop_koopt_niet(omg):
    api, cfg, tmp = omg
    api.dagen_ = {"BTC-EUR": dagen(40000, 60000), "ETH-EUR": dagen(2000, 3000)}
    risico.zet_noodstop(True)
    st = trend_bot.ronde(api, cfg)
    assert st["orders"] == {} and api.st["EUR"] == 1000


def test_prijs_tekst():
    assert bitvavo.prijs_tekst(66590.4, {"tickSize": "1.00"}) == "66590"
    assert bitvavo.prijs_tekst(3012.346, {"tickSize": "0.01"}) == "3012.35"
