"""Strategieën. Kies in instellingen_bitvavo.json met "soort": "trend" (hieronder), "smc" (smc.py)
of "sweep" (sweep_cisd.py).

Trend: trendvolger met twee voortschrijdende gemiddelden (EMA) en ATR-stop.

- Koopsignaal: snelle EMA kruist boven de langzame EMA én de koers ligt boven de trend-EMA.
- Verkoopsignaal: andersom.
- Stop-loss op ATR x stop_atr, take-profit op ATR x doel_atr.
Geen garantie op winst: eerst testen met backtest.py en het oefenaccount.
"""


def ema(waarden, periode):
    if len(waarden) < periode:
        return []
    k = 2 / (periode + 1)
    uit = [None] * (periode - 1)
    e = sum(waarden[:periode]) / periode
    uit.append(e)
    for v in waarden[periode:]:
        e = v * k + e * (1 - k)
        uit.append(e)
    return uit


def atr(candles, periode=14):
    if len(candles) <= periode:
        return []
    tr = [candles[0]["h"] - candles[0]["l"]]
    for vorige, c in zip(candles, candles[1:]):
        tr.append(max(c["h"] - c["l"], abs(c["h"] - vorige["c"]), abs(c["l"] - vorige["c"])))
    uit = [None] * (periode - 1)
    a = sum(tr[:periode]) / periode
    uit.append(a)
    for t in tr[periode:]:
        a = (a * (periode - 1) + t) / periode   # Wilder
        uit.append(a)
    return uit


STANDAARD = {"snel": 20, "langzaam": 50, "trend": 200, "atr": 14, "stop_atr": 1.5, "doel_atr": 3.0}


def kies(inst):
    """{'soort': 'smc', 'smc': {...}, 'trend': {...}} -> (soort, instellingen van die soort)."""
    inst = inst or {}
    soort = inst.get("soort", "trend")
    eigen = inst.get(soort)
    return soort, {**(eigen if isinstance(eigen, dict) else inst), "soort": soort}


def signaal(candles, inst=None):
    soort, p = kies(inst)
    if soort == "smc":
        import smc
        return smc.signaal(candles, p)
    if soort == "sweep":
        import sweep_cisd
        return sweep_cisd.signaal(candles, p)
    return trend_signaal(candles, p)


def trend_signaal(candles, inst=None):
    """Kijkt naar de laatste afgesloten candle.

    Geeft None of dict: richting ('koop'/'verkoop'), instap, stop, doel, atr.
    """
    p = {**STANDAARD, **(inst or {})}
    candles = candles[-max(600, p["trend"] * 3):]
    if len(candles) < p["trend"] + 2:
        return None
    sluit = [c["c"] for c in candles]
    snel, langzaam, trend = ema(sluit, p["snel"]), ema(sluit, p["langzaam"]), ema(sluit, p["trend"])
    a = atr(candles, p["atr"])[-1]
    if not a:
        return None
    nu, voor = -1, -2
    prijs = sluit[nu]
    omhoog = snel[voor] <= langzaam[voor] and snel[nu] > langzaam[nu] and prijs > trend[nu]
    omlaag = snel[voor] >= langzaam[voor] and snel[nu] < langzaam[nu] and prijs < trend[nu]
    if omhoog:
        return {"richting": "koop", "instap": prijs, "stop": prijs - a * p["stop_atr"],
                "doel": prijs + a * p["doel_atr"], "atr": a}
    if omlaag:
        return {"richting": "verkoop", "instap": prijs, "stop": prijs + a * p["stop_atr"],
                "doel": prijs - a * p["doel_atr"], "atr": a}
    return None
