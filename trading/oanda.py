"""Kleine OANDA v20 REST-client (alleen wat de bot nodig heeft).

Sleutels komen uit omgevingsvariabelen, nooit uit de code:
  OANDA_TOKEN    persoonlijke API-token (Mijn account > API-toegang beheren)
  OANDA_ACCOUNT  rekeningnummer, bv. 101-004-1234567-001
  OANDA_OMGEVING "practice" (oefengeld, standaard) of "live" (echt geld)
"""
import os
import requests

HOSTS = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}


class OandaFout(RuntimeError):
    pass


class Oanda:
    def __init__(self, token=None, account=None, omgeving=None, timeout=20):
        self.token = token or os.environ.get("OANDA_TOKEN", "")
        self.account = account or os.environ.get("OANDA_ACCOUNT", "")
        self.omgeving = (omgeving or os.environ.get("OANDA_OMGEVING", "practice")).lower()
        if self.omgeving not in HOSTS:
            raise OandaFout(f"OANDA_OMGEVING moet practice of live zijn, niet {self.omgeving!r}")
        if not self.token or not self.account:
            raise OandaFout("Zet eerst OANDA_TOKEN en OANDA_ACCOUNT (zie trading/README.md)")
        self.basis = HOSTS[self.omgeving]
        self.timeout = timeout
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": "RFC3339",
        })

    # --- intern -------------------------------------------------------
    def _req(self, methode, pad, **kw):
        r = self.s.request(methode, self.basis + pad, timeout=self.timeout, **kw)
        if r.status_code >= 400:
            raise OandaFout(f"{methode} {pad} -> {r.status_code}: {r.text[:300]}")
        return r.json() if r.text else {}

    @property
    def _acc(self):
        return f"/v3/accounts/{self.account}"

    # --- lezen --------------------------------------------------------
    def samenvatting(self):
        return self._req("GET", self._acc + "/summary")["account"]

    def open_trades(self):
        return self._req("GET", self._acc + "/openTrades")["trades"]

    def candles(self, instrument, granularity="H1", aantal=300):
        """Afgesloten candles als lijst dicts: tijd, o, h, l, c, volume."""
        d = self._req("GET", f"/v3/instruments/{instrument}/candles",
                      params={"granularity": granularity, "count": aantal, "price": "M"})
        uit = []
        for c in d["candles"]:
            if not c["complete"]:
                continue
            m = c["mid"]
            uit.append({"tijd": c["time"], "o": float(m["o"]), "h": float(m["h"]),
                        "l": float(m["l"]), "c": float(m["c"]), "volume": c["volume"]})
        return uit

    def prijs(self, instrument):
        """Bied/laat-prijs plus omrekenfactoren naar de rekeningvaluta."""
        d = self._req("GET", self._acc + "/pricing",
                      params={"instruments": instrument, "includeHomeConversions": "true"})
        p = d["prices"][0]
        return {
            "bid": float(p["bids"][0]["price"]),
            "ask": float(p["asks"][0]["price"]),
            "handelbaar": p.get("tradeable", True),
            "omrekening": {h["currency"]: float(h["accountLoss"]) for h in d.get("homeConversions", [])},
        }

    def instrument_info(self, instrument):
        d = self._req("GET", self._acc + "/instruments", params={"instruments": instrument})
        return d["instruments"][0]

    # --- handelen -----------------------------------------------------
    def market_order(self, instrument, units, stop_loss, take_profit, decimalen):
        """units > 0 = kopen, < 0 = verkopen. Altijd met stop-loss en take-profit."""
        order = {
            "type": "MARKET",
            "instrument": instrument,
            "units": str(int(units)),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"price": f"{stop_loss:.{decimalen}f}"},
            "takeProfitOnFill": {"price": f"{take_profit:.{decimalen}f}"},
        }
        return self._req("POST", self._acc + "/orders", json={"order": order})

    def sluit_trade(self, trade_id):
        return self._req("PUT", self._acc + f"/trades/{trade_id}/close")
