"""Strategie 'smart money' (eigen versie van het idee achter Smart Money Concepts).

Stappen, alleen op afgesloten candles:
1. Toppen en bodems (swings): een candle met de hoogste top / laagste bodem van `swing` candles links en rechts.
2. Structuur: slot boven de laatste top = breuk omhoog. Was de trend omlaag, dan heet dat CHoCH (wending),
   anders BOS (voortzetting). Andersom voor omlaag.
3. Vraagzone (order block): bij een breuk omhoog de candle met de laagste bodem tussen de vorige top en de breuk.
   De zone loopt van die bodem tot de top van die candle. Zakt de koers erdoor (slot onder de zone), dan vervalt hij.
4. Kopen als: trend omhoog (laatste breuk was omhoog), koers boven SMA 200 (en SMA 20 boven SMA 50 als
   `sma_kruis` aan staat), en de koers zakt de zone in maar sluit erboven. Elke zone één keer.
5. Stop-loss: onder de zone (min `stop_atr` x ATR). Doel: `rr` keer het risico.
"""

STANDAARD = {"swing": 5, "sma_kort": 20, "sma_mid": 50, "sma_lang": 200, "sma_kruis": False,
             "atr": 14, "stop_atr": 0.3, "rr": 2.5, "venster": 600, "min_risico_pct": 1.5}


def sma(waarden, periode):
    if len(waarden) < periode:
        return [None] * len(waarden)
    uit = [None] * (periode - 1)
    s = sum(waarden[:periode])
    uit.append(s / periode)
    for i in range(periode, len(waarden)):
        s += waarden[i] - waarden[i - periode]
        uit.append(s / periode)
    return uit


def structuur(candles, swing=5):
    """Loopt door de candles en geeft de stand op de laatste candle.

    Uit: dict met trend ('op'/'neer'/None), gebeurtenissen [(index, 'BOS'/'CHoCH', 'op'/'neer')],
         zones (lijst actieve vraagzones {laag, hoog, index, gebruikt}).
    """
    n = len(candles)
    trend, top, bodem = None, None, None          # top/bodem = (index, prijs) laatst bevestigde swing
    top_gebroken = bodem_gebroken = True
    gebeurtenissen, zones = [], []
    for i in range(n):
        # swing bevestigd op i - swing (heeft nu `swing` candles rechts)
        j = i - swing
        if j >= swing:
            venster = candles[j - swing:i + 1]
            if candles[j]["h"] == max(c["h"] for c in venster):
                top, top_gebroken = (j, candles[j]["h"]), False
            if candles[j]["l"] == min(c["l"] for c in venster):
                bodem, bodem_gebroken = (j, candles[j]["l"]), False
        c = candles[i]
        # zones die doorbroken zijn vervallen
        zones = [z for z in zones if c["c"] >= z["laag"]]
        if top and not top_gebroken and c["c"] > top[1]:
            soort = "CHoCH" if trend == "neer" else "BOS"
            trend, top_gebroken = "op", True
            gebeurtenissen.append((i, soort, "op"))
            k = min(range(top[0], i + 1), key=lambda x: candles[x]["l"])
            zones.append({"laag": candles[k]["l"], "hoog": max(candles[k]["o"], candles[k]["c"]),
                          "index": k, "gebruikt": False})
            zones = zones[-5:]
        if bodem and not bodem_gebroken and c["c"] < bodem[1]:
            soort = "CHoCH" if trend == "op" else "BOS"
            trend, bodem_gebroken = "neer", True
            gebeurtenissen.append((i, soort, "neer"))
    return {"trend": trend, "gebeurtenissen": gebeurtenissen, "zones": zones}


def signaal(candles, inst=None):
    from strategie import atr
    p = {**STANDAARD, **(inst or {})}
    candles = candles[-p["venster"]:]
    if len(candles) < p["sma_lang"] + 2 * p["swing"] + 2:
        return None
    sluit = [c["c"] for c in candles]
    lang = sma(sluit, p["sma_lang"])[-1]
    kort, mid = sma(sluit, p["sma_kort"])[-1], sma(sluit, p["sma_mid"])[-1]
    nu = candles[-1]
    if lang is None or nu["c"] <= lang:
        return None
    if p["sma_kruis"] and not kort > mid:
        return None
    # zones van vóór deze candle, zodat de aanraking echt nu gebeurt
    st = structuur(candles[:-1], p["swing"])
    if st["trend"] != "op":
        return None
    a = atr(candles, p["atr"])[-1]
    vorige = candles[-2]
    for z in reversed(st["zones"]):
        if z["index"] >= len(candles) - 2:
            continue
        geraakt = nu["l"] <= z["hoog"] and nu["c"] > z["hoog"] and vorige["l"] > z["hoog"]
        if not geraakt:
            continue
        instap = nu["c"]
        stop = z["laag"] - a * p["stop_atr"]
        risico = instap - stop
        if risico <= 0 or risico / instap * 100 < p["min_risico_pct"]:
            return None   # stop te dicht: kosten zouden de winst opeten
        return {"richting": "koop", "instap": instap, "stop": stop, "doel": instap + risico * p["rr"],
                "atr": a, "zone": (z["laag"], z["hoog"])}
    return None
