"""Bitvavo-koppeling (spot crypto in euro's).

Twee standen met dezelfde functies:
  Bitvavo  - echte rekening (sleutel nodig, echt geld)
  Papier   - oefenstand: echte koersen van Bitvavo, nepgeld, geen sleutel nodig

Sleutels (alleen voor echt geld), uit omgevingsvariabelen:
  BITVAVO_KEY, BITVAVO_SECRET   (Bitvavo > Instellingen > API; ALLEEN 'handelen' aanvinken, NOOIT 'opnemen')
  BITVAVO_OPERATOR_ID           getal dat je zelf kiest om orders van deze bot te herkennen (standaard 1001)
"""
import hashlib
import hmac
import json
import math
import os
import time
import uuid

import requests

BASIS = "https://api.bitvavo.com/v2"
UUR_MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000,
          "2h": 7_200_000, "4h": 14_400_000, "6h": 21_600_000, "8h": 28_800_000, "12h": 43_200_000,
          "1d": 86_400_000}
MAP = os.path.dirname(os.path.abspath(__file__))


class BitvavoFout(RuntimeError):
    pass


def afronden_omlaag(x, decimalen):
    f = 10 ** decimalen
    return math.floor(x * f + 1e-9) / f


def prijs_afronden(prijs, info):
    """Bitvavo wil prijzen met een beperkt aantal significante cijfers (of op tickSize)."""
    if info.get("tickSize"):
        t = float(info["tickSize"])
        return round(round(prijs / t) * t, 12)
    sig = int(info.get("pricePrecision") or 5)
    if prijs <= 0:
        return prijs
    dec = sig - int(math.floor(math.log10(abs(prijs)))) - 1
    return round(prijs, max(dec, 0))


def hoeveelheid_decimalen(info):
    return int(info.get("quantityDecimals", 8))


class Publiek:
    """Openbare gegevens: geen sleutel nodig."""

    def __init__(self, timeout=20):
        self.s = requests.Session()
        self.timeout = timeout

    def _get(self, pad, params=None):
        r = self.s.get(BASIS + pad, params=params, timeout=self.timeout)
        if r.status_code >= 400:
            raise BitvavoFout(f"GET {pad} -> {r.status_code}: {r.text[:300]}")
        return r.json()

    def candles(self, market, interval="1h", aantal=300, eind_ms=None):
        """Afgesloten candles, oud -> nieuw, als dicts tijd/o/h/l/c/volume."""
        stap = UUR_MS[interval]
        nu = int(time.time() * 1000)
        uit, eind = [], eind_ms
        while len(uit) < aantal:
            params = {"interval": interval, "limit": min(1440, aantal - len(uit))}
            if eind:
                params["end"] = eind
            rijen = self._get(f"/{market}/candles", params)
            if not rijen:
                break
            for t, o, h, l, c, v in rijen:                  # nieuwste eerst
                if t + stap > nu:
                    continue                                 # candle nog niet af
                uit.append({"tijd": int(t), "o": float(o), "h": float(h), "l": float(l),
                            "c": float(c), "volume": float(v)})
            eind = int(rijen[-1][0]) - 1
            if len(rijen) < params["limit"]:
                break
        uit = {c["tijd"]: c for c in uit}
        return [uit[k] for k in sorted(uit)][-aantal:]

    def boek(self, market):
        d = self._get("/ticker/book", {"market": market})
        return {"bid": float(d["bid"]), "ask": float(d["ask"])}

    def market_info(self, market):
        return self._get("/markets", {"market": market})


class Bitvavo(Publiek):
    """Echte rekening."""
    papier = False

    def __init__(self, key=None, secret=None, operator_id=None, timeout=20):
        super().__init__(timeout)
        self.key = key or os.environ.get("BITVAVO_KEY", "")
        self.secret = secret or os.environ.get("BITVAVO_SECRET", "")
        self.operator_id = int(operator_id or os.environ.get("BITVAVO_OPERATOR_ID", "1001"))
        if not self.key or not self.secret:
            raise BitvavoFout("Zet eerst BITVAVO_KEY en BITVAVO_SECRET (zie trading/README.md)")

    def _prive(self, methode, pad, params=None, body=None):
        url = pad
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        tekst = json.dumps(body, separators=(",", ":")) if body is not None else ""
        ts = str(int(time.time() * 1000))
        handtekening = hmac.new(self.secret.encode(), (ts + methode + "/v2" + url + tekst).encode(),
                                hashlib.sha256).hexdigest()
        kop = {"Bitvavo-Access-Key": self.key, "Bitvavo-Access-Signature": handtekening,
               "Bitvavo-Access-Timestamp": ts, "Bitvavo-Access-Window": "10000",
               "Content-Type": "application/json"}
        r = self.s.request(methode, BASIS + url, headers=kop, data=tekst or None, timeout=self.timeout)
        if r.status_code >= 400:
            raise BitvavoFout(f"{methode} {pad} -> {r.status_code}: {r.text[:300]}")
        return r.json() if r.text else {}

    def saldi(self):
        """{'EUR': (beschikbaar, in_order), 'BTC': (...), ...}"""
        return {b["symbol"]: (float(b["available"]), float(b["inOrder"])) for b in self._prive("GET", "/balance")}

    def koop_markt(self, market, eur):
        d = self._prive("POST", "/order", body={
            "market": market, "side": "buy", "orderType": "market",
            "amountQuote": f"{eur:.2f}", "operatorId": self.operator_id})
        aantal = float(d.get("filledAmount", 0))
        betaald = float(d.get("filledAmountQuote", 0))
        return {"aantal": aantal, "prijs": betaald / aantal if aantal else 0, "id": d.get("orderId")}

    def verkoop_markt(self, market, aantal, decimalen=8):
        d = self._prive("POST", "/order", body={
            "market": market, "side": "sell", "orderType": "market",
            "amount": f"{afronden_omlaag(aantal, decimalen):.{decimalen}f}", "operatorId": self.operator_id})
        a = float(d.get("filledAmount", 0))
        return {"aantal": a, "prijs": float(d.get("filledAmountQuote", 0)) / a if a else 0}

    def stop_order(self, market, aantal, trigger, info):
        dec = hoeveelheid_decimalen(info)
        d = self._prive("POST", "/order", body={
            "market": market, "side": "sell", "orderType": "stopLoss",
            "amount": f"{afronden_omlaag(aantal, dec):.{dec}f}",
            "triggerAmount": str(prijs_afronden(trigger, info)),
            "triggerType": "price", "triggerReference": "lastTrade", "operatorId": self.operator_id})
        return d["orderId"]

    def order_status(self, market, order_id):
        return self._prive("GET", "/order", {"market": market, "orderId": order_id}).get("status")

    def annuleer(self, market, order_id):
        return self._prive("DELETE", "/order", {"market": market, "orderId": order_id,
                                                "operatorId": self.operator_id})


class Papier(Publiek):
    """Oefenstand met nepgeld. Echte koersen, 0,25% kosten per order, bewaard in data/papier_bitvavo.json."""
    papier = True
    KOSTEN = 0.0025

    def __init__(self, start_eur=1000.0, pad=None, timeout=20):
        super().__init__(timeout)
        self.pad = pad or os.path.join(MAP, "data", "papier_bitvavo.json")
        if os.path.exists(self.pad):
            with open(self.pad) as f:
                self.st = json.load(f)
        else:
            self.st = {"EUR": start_eur, "bezit": {}, "orders": {}}
            self._bewaar()

    def _bewaar(self):
        os.makedirs(os.path.dirname(self.pad), exist_ok=True)
        with open(self.pad, "w") as f:
            json.dump(self.st, f, indent=1)

    def saldi(self):
        in_order = {}
        for o in self.st["orders"].values():
            base = o["market"].split("-")[0]
            in_order[base] = in_order.get(base, 0) + o["aantal"]
        uit = {"EUR": (self.st["EUR"], 0.0)}
        for base, a in self.st["bezit"].items():
            uit[base] = (a - in_order.get(base, 0), in_order.get(base, 0))
        return uit

    def koop_markt(self, market, eur):
        eur = min(eur, self.st["EUR"])
        prijs = self.boek(market)["ask"]
        aantal = eur * (1 - self.KOSTEN) / prijs
        base = market.split("-")[0]
        self.st["EUR"] -= eur
        self.st["bezit"][base] = self.st["bezit"].get(base, 0) + aantal
        self._bewaar()
        return {"aantal": aantal, "prijs": prijs, "id": "papier"}

    def verkoop_markt(self, market, aantal, decimalen=8, prijs=None):
        base = market.split("-")[0]
        aantal = min(aantal, self.st["bezit"].get(base, 0))
        prijs = prijs or self.boek(market)["bid"]
        self.st["EUR"] += aantal * prijs * (1 - self.KOSTEN)
        self.st["bezit"][base] = self.st["bezit"].get(base, 0) - aantal
        if self.st["bezit"][base] <= 1e-12:
            del self.st["bezit"][base]
        self._bewaar()
        return {"aantal": aantal, "prijs": prijs}

    def stop_order(self, market, aantal, trigger, info):
        oid = "p-" + uuid.uuid4().hex[:10]
        self.st["orders"][oid] = {"market": market, "aantal": aantal, "trigger": trigger}
        self._bewaar()
        return oid

    def order_status(self, market, order_id):
        o = self.st["orders"].get(order_id)
        if not o:
            return "filled"
        prijs = self.boek(market)["bid"]
        if prijs <= o["trigger"]:
            del self.st["orders"][order_id]
            self._bewaar()
            self.verkoop_markt(market, o["aantal"], prijs=prijs)
            return "filled"
        return "awaitingTrigger"

    def annuleer(self, market, order_id):
        self.st["orders"].pop(order_id, None)
        self._bewaar()
        return {"orderId": order_id}
