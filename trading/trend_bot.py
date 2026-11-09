"""Trendfilter-bot voor Bitvavo: wekelijks inleggen + alleen in de markt boven het 200-daags gemiddelde.

Werking:
- Jij stort (bv. elke week via iDEAL) euro's op Bitvavo.
- Eén keer per dag (na middernacht UTC) kijkt de bot per munt of het slot van gisteren boven het
  gemiddelde van de laatste 200 dagen staat.
    boven  -> "in":  vrij geld gaat naar die munt, tot zijn deel van je totaal (bv. 70% BTC, 30% ETH)
    onder  -> "uit": alles van die munt wordt verkocht, het geld blijft in euro's staan
- Orders zijn limietorders (0,15% kosten). Niet gevuld binnen 15 minuten -> marktorder (0,25%).
- Geen stop-loss/doelen: het filter zelf is de bescherming. Er wordt niet heen-en-weer geschoven
  tussen munten; verkopen gebeurt alleen als de trend omslaat.

Oefenstand (standaard):   python trend_bot.py
Echt geld:                python trend_bot.py --echt-geld
Backtest op echte koersen (geen sleutel nodig):   python trend_bot.py --backtest
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import risico
from bitvavo import Bitvavo, BitvavoFout, Papier, Publiek, hoeveelheid_decimalen

MAP = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(MAP, "data", "log_bitvavo.jsonl")
DAG = 86_400_000


def laad_instellingen():
    with open(os.path.join(MAP, "instellingen_trend.json")) as f:
        return json.load(f)


def log(soort, **info):
    regel = {"tijd": datetime.now(timezone.utc).isoformat(timespec="seconds"), "soort": soort, **info}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(regel) + "\n")
    print(f"[{regel['tijd']}] {soort}: {info}", flush=True)


def _pad(api, naam):
    return os.path.join(MAP, "data", f"{naam}_bitvavo_{'papier' if api.papier else 'echt'}.json")


def lees(api, naam, standaard):
    p = _pad(api, naam)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return standaard


def bewaar(api, naam, data):
    os.makedirs(os.path.join(MAP, "data"), exist_ok=True)
    with open(_pad(api, naam), "w") as f:
        json.dump(data, f, indent=1)


def trend(dag_candles, n=200):
    """'in' als het slot van de laatste afgesloten dag boven het gemiddelde van de laatste n dagen ligt."""
    if len(dag_candles) < n:
        return None, None
    slot = [c["c"] for c in dag_candles]
    sma = sum(slot[-n:]) / n
    return ("in" if slot[-1] > sma else "uit"), sma


def plaats(api, m, kant, eur_of_aantal, koers, info, cfg, staat):
    """Limietorder op de beste bied-/laatprijs (maker)."""
    if kant == "buy":
        prijs = koers["bid"]
        aantal = eur_of_aantal / prijs * 0.998          # ruimte voor kosten
    else:
        prijs = koers["ask"]
        aantal = eur_of_aantal
    oid = api.limiet_order(m, kant, aantal, prijs, info)
    staat["orders"][m] = {"id": oid, "kant": kant, "aantal": aantal, "prijs": prijs,
                          "sinds": int(time.time())}
    log("limiet geplaatst", markt=m, kant="kopen" if kant == "buy" else "verkopen",
        limiet=prijs, stop=None, tp1=None, doel=None, eur=round(aantal * prijs, 2))


def verwerk_order(api, m, staat, info, cfg):
    """Gevuld? -> klaar. Te lang open? -> annuleren en rest met een marktorder."""
    o = staat["orders"][m]
    st = api.order_info(m, o["id"])
    if st["status"] == "filled":
        log("gekocht" if o["kant"] == "buy" else "verkocht", markt=m, prijs=o["prijs"],
            aantal=st["gevuld"], eur=round(st["gevuld_eur"], 2), soort_order="limiet")
        _boek_instap(staat, m, o["kant"], st["gevuld"], st["gevuld_eur"])
        del staat["orders"][m]
        return
    if st["status"] in ("canceled", "expired", "rejected") or \
            time.time() - o["sinds"] > cfg.get("limiet_wacht_min", 15) * 60:
        if st["status"] not in ("canceled", "expired", "rejected"):
            api.annuleer(m, o["id"])
            st = api.order_info(m, o["id"])
        if st["gevuld"] > 0:
            _boek_instap(staat, m, o["kant"], st["gevuld"], st["gevuld_eur"])
        del staat["orders"][m]
        base = m.split("-")[0]
        if o["kant"] == "buy":
            rest_eur = (o["aantal"] - st["gevuld"]) * o["prijs"]
            rest_eur = min(rest_eur, api.saldi().get("EUR", (0, 0))[0] * 0.995)
            if rest_eur >= float(info.get("minOrderInQuoteAsset", 5)):
                res = api.koop_markt(m, rest_eur)
                _boek_instap(staat, m, "buy", res["aantal"], res["aantal"] * res["prijs"])
                log("gekocht", markt=m, prijs=res["prijs"], aantal=res["aantal"], eur=round(rest_eur, 2),
                    soort_order="markt (limiet niet gevuld)")
        else:
            vrij = api.saldi().get(base, (0, 0))[0]
            if vrij * o["prijs"] >= 5:
                res = api.verkoop_markt(m, vrij, hoeveelheid_decimalen(info))
                _boek_instap(staat, m, "sell", res["aantal"], res["aantal"] * res["prijs"])
                log("verkocht", markt=m, prijs=res["prijs"], aantal=res["aantal"],
                    soort_order="markt (limiet niet gevuld)")


def _boek_instap(staat, m, kant, aantal, eur):
    """Houdt de gemiddelde aankoopprijs bij (voor winst/verlies op het dashboard)."""
    g = staat["gemiddeld"].setdefault(m, {"aantal": 0.0, "eur": 0.0})
    if kant == "buy":
        g["aantal"] += aantal
        g["eur"] += eur
    else:
        if g["aantal"] > 0:
            deel = min(aantal / g["aantal"], 1.0)
            g["aantal"] -= g["aantal"] * deel
            g["eur"] -= g["eur"] * deel


def ronde(api, cfg, infos=None):
    infos = infos if infos is not None else {}
    staat = lees(api, "trendstaat", {"dag": None, "trend": {}, "orders": {}, "gemiddeld": {}})
    markten = cfg["markten"]                         # {"BTC-EUR": 0.7, "ETH-EUR": 0.3}
    for m in markten:
        if m not in infos:
            infos[m] = api.market_info(m)

    # 1. eens per dag de trend bepalen (na middernacht UTC, met afgesloten dagcandles)
    vandaag = datetime.now(timezone.utc).date().isoformat()
    if staat["dag"] != vandaag:
        for m in markten:
            dagen = api.candles(m, "1d", cfg.get("sma_dagen", 200) + 5)
            t, sma = trend(dagen, cfg.get("sma_dagen", 200))
            if t is None:
                log("fout", melding=f"te weinig dagcandles voor {m}")
                continue
            oud = staat["trend"].get(m)
            staat["trend"][m] = t
            log("trend", markt=m, trend=t, slot=dagen[-1]["c"], sma=round(sma, 2),
                **({"omslag": True} if oud and oud != t else {}))
        staat["dag"] = vandaag
        if cfg.get("papier_storting_per_week") and api.papier and \
                datetime.now(timezone.utc).weekday() == cfg.get("stortingsdag", 0):
            api.st["EUR"] += cfg["papier_storting_per_week"]
            api._bewaar()
            log("storting (oefenstand)", eur=cfg["papier_storting_per_week"])

    # 2. openstaande limietorders afhandelen
    for m in list(staat["orders"]):
        verwerk_order(api, m, staat, infos[m], cfg)

    # 3. nieuwe orders
    saldi = api.saldi()
    koersen = {m: api.boek(m) for m in markten}
    waarde = {m: sum(saldi.get(m.split("-")[0], (0, 0))) * koersen[m]["bid"] for m in markten}
    eur_vrij = saldi.get("EUR", (0, 0))[0]
    totaal = sum(saldi.get("EUR", (0, 0))) + sum(waarde.values())
    reserve = cfg.get("reserve_eur", 0)
    stil = risico.noodstop_aan()
    for m, gewicht in markten.items():
        if m in staat["orders"] or stil:
            continue
        base = m.split("-")[0]
        minimum = float(infos[m].get("minOrderInQuoteAsset", 5))
        if staat["trend"].get(m) == "uit":
            vrij = saldi.get(base, (0, 0))[0]
            if vrij * koersen[m]["bid"] >= minimum:
                plaats(api, m, "sell", vrij, koersen[m], infos[m], cfg, staat)
        elif staat["trend"].get(m) == "in":
            tekort = gewicht * totaal - waarde[m]
            koop = min(tekort, eur_vrij - reserve)
            if koop >= max(minimum, cfg.get("min_order_eur", 10)):
                plaats(api, m, "buy", koop, koersen[m], infos[m], cfg, staat)
                eur_vrij -= koop
    bewaar(api, "trendstaat", staat)

    # 4. posities voor het dashboard
    pos = {}
    for m in markten:
        aantal = sum(saldi.get(m.split("-")[0], (0, 0)))
        g = staat["gemiddeld"].get(m, {})
        if aantal * koersen[m]["bid"] >= 1:
            gem = g["eur"] / g["aantal"] if g.get("aantal") else koersen[m]["bid"]
            pos[m] = {"status": "open", "aantal": aantal, "instap": gem, "stop": None, "doel": None,
                      "trend": staat["trend"].get(m)}
        elif m in staat["orders"]:
            o = staat["orders"][m]
            pos[m] = {"status": "wacht", "limiet": o["prijs"], "stop": None, "doel": None}
    bewaar(api, "posities", pos)
    return staat


def backtest(maanden=None):
    """Vasthouden vs. wekelijks kopen vs. trendfilter, op echte Bitvavo-dagkoersen (geen sleutel nodig)."""
    cfg = laad_instellingen()
    n, f = cfg.get("sma_dagen", 200), 0.0015
    pub = Publiek()
    for m in cfg["markten"]:
        d = pub.candles(m, "1d", 2000)
        c = [x["c"] for x in d]
        start = n
        hold = c[-1] / c[start] - 1
        eq, inm, piek, dd, wissels = 1.0, False, 1.0, 0.0, 0
        p, hdd = c[start], 0.0
        for i in range(start, len(c)):
            if inm:
                eq *= c[i] / c[i - 1]
            wil = c[i] > sum(c[i - n + 1:i + 1]) / n
            if wil != inm:
                eq *= 1 - f
                inm, wissels = wil, wissels + 1
            piek, dd = max(piek, eq), max(dd, 1 - eq / piek)
            p, hdd = max(p, c[i]), max(hdd, 1 - c[i] / p)
        van = datetime.fromtimestamp(d[start]["tijd"] / 1000, timezone.utc).date()
        print(f"{m} vanaf {van}: vasthouden {hold * 100:+.0f}% (grootste daling {hdd * 100:.0f}%) | "
              f"trendfilter {(eq - 1) * 100:+.0f}% (grootste daling {dd * 100:.0f}%, {wissels} wissels)")


def maak_api(echt_geld, cfg):
    return Bitvavo() if echt_geld else Papier(start_eur=cfg.get("papier_start_eur", 1000))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--een-keer", action="store_true")
    ap.add_argument("--echt-geld", action="store_true")
    ap.add_argument("--backtest", action="store_true")
    a = ap.parse_args()
    if a.backtest:
        return backtest()
    cfg = laad_instellingen()
    api = maak_api(a.echt_geld, cfg)
    log("start", stand="ECHT GELD" if a.echt_geld else "oefenstand", markten=list(cfg["markten"]),
        strategie="trendfilter SMA200")
    infos, fouten = {}, 0
    while True:
        try:
            ronde(api, cfg, infos)
            fouten = 0
        except (BitvavoFout, OSError, ValueError, KeyError) as e:
            fouten += 1
            log("fout", melding=str(e)[:300], achter_elkaar=fouten)
            if fouten >= 10:
                log("stop", reden="10 fouten achter elkaar")
                sys.exit(1)
        if a.een_keer:
            break
        time.sleep(cfg.get("controle_elke_sec", 60))


if __name__ == "__main__":
    main()
