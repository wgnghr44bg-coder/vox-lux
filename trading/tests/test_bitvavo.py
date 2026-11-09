import hashlib
import hmac
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bitvavo  # noqa: E402
import bitvavo_bot  # noqa: E402
import risico  # noqa: E402
import strategie  # noqa: E402
from test_bot import maak_candles  # noqa: E402


class NepPapier(bitvavo.Papier):
    """Papier-stand met koersen uit een lijst i.p.v. internet."""

    def __init__(self, candles, pad):
        self.candles_ = candles
        self.prijs_ = candles[-1]["c"]
        super().__init__(start_eur=1000, pad=pad)

    def candles(self, market, interval="1h", aantal=300, eind_ms=None):
        return self.candles_

    def boek(self, market):
        return {"bid": self.prijs_ * 0.9995, "ask": self.prijs_ * 1.0005}

    def market_info(self, market):
        return {"market": market, "pricePrecision": 5, "minOrderInQuoteAsset": "5"}


@pytest.fixture
def omgeving(tmp_path, monkeypatch):
    monkeypatch.setattr(bitvavo_bot, "LOG", str(tmp_path / "log.jsonl"))
    monkeypatch.setattr(bitvavo_bot, "MAP", str(tmp_path))
    monkeypatch.setattr(risico, "DAGSTAND", str(tmp_path / "dag.json"))
    monkeypatch.setattr(risico, "NOODSTOP", str(tmp_path / "NOODSTOP"))
    # koersen schalen naar ~60.000 zodat het op BTC lijkt
    c = [{**x, **{k: x[k] * 55000 for k in "ohlc"}} for x in maak_candles(2000, seed=3)]
    eind = next(i for i in range(210, len(c))
                if (s := strategie.signaal(c[:i], {"stop_atr": 2.0, "doel_atr": 4.0})) and s["richting"] == "koop")
    api = NepPapier(c[:eind], str(tmp_path / "papier.json"))
    cfg = json.load(open(os.path.join(os.path.dirname(bitvavo_bot.__file__), "instellingen_bitvavo.json")))
    cfg["markten"] = ["BTC-EUR"]
    cfg["strategie"] = {"soort": "trend", "trend": {**cfg["strategie"]["trend"]}}
    return api, cfg, tmp_path


def test_handtekening_formaat(monkeypatch):
    api = bitvavo.Bitvavo(key="k", secret="geheim")
    gezien = {}

    class Antwoord:
        status_code, text = 200, "[]"

        def json(self):
            return []

    def nep_request(methode, url, headers, data, timeout):
        gezien.update(methode=methode, url=url, headers=headers, data=data)
        return Antwoord()

    monkeypatch.setattr(api.s, "request", nep_request)
    monkeypatch.setattr(bitvavo.time, "time", lambda: 1700000000.123)
    api._prive("POST", "/order", body={"market": "BTC-EUR", "side": "buy"})
    body = '{"market":"BTC-EUR","side":"buy"}'
    verwacht = hmac.new(b"geheim", ("1700000000123POST/v2/order" + body).encode(), hashlib.sha256).hexdigest()
    assert gezien["headers"]["Bitvavo-Access-Signature"] == verwacht
    assert gezien["headers"]["Bitvavo-Access-Timestamp"] == "1700000000123"
    assert gezien["data"] == body and gezien["url"].endswith("/v2/order")


def test_prijs_afronden():
    assert bitvavo.prijs_afronden(61234.567, {"pricePrecision": 5}) == 61235
    assert bitvavo.prijs_afronden(0.123456, {"pricePrecision": 5}) == 0.12346
    assert bitvavo.prijs_afronden(101.37, {"tickSize": "0.5"}) == 101.5
    assert bitvavo.afronden_omlaag(0.123456789, 8) == 0.12345678


def test_kopen_dan_doel(omgeving):
    api, cfg, tmp = omgeving
    bitvavo_bot.ronde(api, cfg, {})
    pos = bitvavo_bot.lees_posities(api)
    assert "BTC-EUR" in pos
    p = pos["BTC-EUR"]
    assert p["stop"] < p["instap"] < p["doel"]
    risico_eur = p["aantal"] * (p["instap"] - p["stop"])
    assert risico_eur <= 1000 * 0.005 + 0.01          # max 0,5% van €1000
    assert p["stop_id"] in api.st["orders"]           # stop-loss staat klaar
    assert api.saldi()["BTC"][0] == pytest.approx(0)  # alles vast in de stop-order
    # koers stijgt tot boven het doel -> verkocht
    api.prijs_ = p["doel"] * 1.01
    bitvavo_bot.ronde(api, cfg, {"BTC-EUR": api.candles_[-1]["tijd"]})
    assert bitvavo_bot.lees_posities(api) == {}
    assert api.st["EUR"] > 1000 and "BTC" not in api.st["bezit"]


def test_kopen_dan_stop(omgeving):
    api, cfg, tmp = omgeving
    bitvavo_bot.ronde(api, cfg, {})
    p = bitvavo_bot.lees_posities(api)["BTC-EUR"]
    api.prijs_ = p["stop"] * 0.99
    bitvavo_bot.ronde(api, cfg, {"BTC-EUR": api.candles_[-1]["tijd"]})
    assert bitvavo_bot.lees_posities(api) == {}
    verlies = 1000 - api.st["EUR"]
    assert 0 < verlies < 10                            # ±0,5% plus kosten
    log = open(tmp / "log.jsonl").read()
    assert "stop geraakt" in log


def test_noodstop_koopt_niet(omgeving):
    api, cfg, tmp = omgeving
    risico.zet_noodstop(True)
    bitvavo_bot.ronde(api, cfg, {})
    assert bitvavo_bot.lees_posities(api) == {}
    assert api.st["EUR"] == 1000


def test_echt_geld_vraagt_sleutel(monkeypatch):
    monkeypatch.delenv("BITVAVO_KEY", raising=False)
    monkeypatch.delenv("BITVAVO_SECRET", raising=False)
    with pytest.raises(bitvavo.BitvavoFout):
        bitvavo_bot.maak_api(True, {})
    assert bitvavo_bot.maak_api.__defaults__ is None   # geen standaard naar echt geld


def test_backtest_alleen_koop():
    import backtest
    c = maak_candles(3000)
    t = backtest.simuleer(c, alleen_koop=True, kosten_pct=0.25)
    assert t and all(x["richting"] == "koop" for x in t)
