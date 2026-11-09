import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402
import risico  # noqa: E402
import strategie  # noqa: E402
from test_bot import maak_candles  # noqa: E402


class NepOanda:
    def __init__(self, candles):
        self.candles_ = candles
        self.orders = []

    def samenvatting(self):
        return {"NAV": "10000", "balance": "10000", "currency": "EUR"}

    def open_trades(self):
        return []

    def candles(self, inst, gran, n):
        return self.candles_

    def instrument_info(self, inst):
        return {"displayPrecision": 5, "minimumTradeSize": "1"}

    def prijs(self, inst):
        c = self.candles_[-1]["c"]
        return {"bid": c - 0.00005, "ask": c + 0.00005, "handelbaar": True, "omrekening": {"USD": 0.9}}

    def market_order(self, inst, units, stop, doel, dec):
        self.orders.append((inst, units, stop, doel))
        return {"orderFillTransaction": {"price": "1.1"}}


def test_ronde_plaatst_order_met_stop(tmp_path, monkeypatch):
    monkeypatch.setattr(bot, "LOG", str(tmp_path / "log.jsonl"))
    monkeypatch.setattr(risico, "DAGSTAND", str(tmp_path / "dag.json"))
    monkeypatch.setattr(risico, "NOODSTOP", str(tmp_path / "NOODSTOP"))
    c = maak_candles()
    eind = next(i for i in range(210, len(c)) if strategie.signaal(c[:i]))
    api = NepOanda(c[:eind])
    cfg = bot.laad_instellingen()
    cfg["instrumenten"] = ["EUR_USD"]
    bot.ronde(api, cfg, {})
    assert len(api.orders) == 1
    inst, units, stop, doel = api.orders[0]
    p = api.prijs(inst)
    instap = p["ask"] if units > 0 else p["bid"]
    verlies = abs(units) * abs(instap - stop) * 0.9
    assert 45 < verlies <= 50.01            # ±0,5% van 10.000
    # zelfde candle nog eens: geen nieuwe order
    bot.ronde(api, cfg, {"EUR_USD": c[eind - 1]["tijd"]})
    assert len(api.orders) == 1
    # noodstop aan: geen order
    risico.zet_noodstop(True)
    api2 = NepOanda(c[:eind])
    bot.ronde(api2, cfg, {})
    assert api2.orders == []
