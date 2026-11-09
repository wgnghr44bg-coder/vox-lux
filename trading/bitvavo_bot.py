"""Handelsbot voor Bitvavo (crypto, alleen kopen en weer verkopen).

Oefenstand, nepgeld, geen sleutel nodig (standaard):   python bitvavo_bot.py
Eén ronde en stoppen:                                    python bitvavo_bot.py --een-keer
Echt geld (pas na weken goede resultaten):               python bitvavo_bot.py --echt-geld

Na elke aankoop staat er direct een stop-loss-order op Bitvavo zelf, dus ook als de pc uitvalt.
Het koersdoel bewaakt de bot zelf (Bitvavo staat geen stop én doel tegelijk op dezelfde munten toe).
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import risico
import strategie
from bitvavo import Bitvavo, BitvavoFout, Papier, hoeveelheid_decimalen

MAP = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(MAP, "data", "log_bitvavo.jsonl")
EINDE = ("filled", "canceled", "expired", "rejected", "cancelledAuction", "cancelledSelfTradePrevention",
         "cancelledIOC", "cancelledFOK", "cancelledMarketProtection", "cancelledPostOnly")


def laad_instellingen():
    with open(os.path.join(MAP, "instellingen_bitvavo.json")) as f:
        return json.load(f)


def log(soort, **info):
    regel = {"tijd": datetime.now(timezone.utc).isoformat(timespec="seconds"), "soort": soort, **info}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(regel) + "\n")
    print(f"[{regel['tijd']}] {soort}: {info}", flush=True)


def posities_pad(api):
    return os.path.join(MAP, "data", f"posities_bitvavo_{'papier' if api.papier else 'echt'}.json")


def lees_posities(api):
    p = posities_pad(api)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {}


def bewaar_posities(api, pos):
    os.makedirs(os.path.join(MAP, "data"), exist_ok=True)
    with open(posities_pad(api), "w") as f:
        json.dump(pos, f, indent=1)


def waarde(api, markten, posities):
    """Totale waarde in euro (NAV) en de actuele koersen."""
    saldi = api.saldi()
    koersen = {m: api.boek(m) for m in set(markten) | set(posities)}
    nav = sum(saldi.get("EUR", (0, 0)))
    for m, k in koersen.items():
        base = m.split("-")[0]
        nav += sum(saldi.get(base, (0, 0))) * k["bid"]
    return nav, saldi, koersen


def beheer_posities(api, posities, koersen, infos):
    for m in list(posities):
        p = posities[m]
        status = api.order_status(m, p["stop_id"])
        if status == "filled":
            r = (p["stop"] - p["instap"]) / (p["instap"] - p["stop_start"])
            log("stop geraakt", markt=m, instap=p["instap"], stop=p["stop"], R=round(r, 2))
            del posities[m]
            continue
        if status in EINDE:                       # stop verdwenen: opnieuw beschermen
            base = m.split("-")[0]
            vrij = api.saldi().get(base, (0, 0))[0]
            if vrij <= 0:
                log("positie weg", markt=m, status=status)
                del posities[m]
                continue
            p["aantal"] = vrij
            p["stop_id"] = api.stop_order(m, vrij, p["stop"], infos[m])
            log("stop opnieuw geplaatst", markt=m, status=status, stop=p["stop"])
        bid = koersen[m]["bid"]
        if bid >= p["doel"]:
            api.annuleer(m, p["stop_id"])
            base = m.split("-")[0]
            vrij = api.saldi().get(base, (0, 0))[0]
            res = api.verkoop_markt(m, min(vrij, p["aantal"]) or vrij, hoeveelheid_decimalen(infos[m]))
            r = (res["prijs"] - p["instap"]) / (p["instap"] - p["stop_start"])
            log("doel bereikt", markt=m, instap=p["instap"], verkocht=res["prijs"], R=round(r, 2))
            del posities[m]


def ronde(api, cfg, laatste_candle, infos=None):
    infos = infos if infos is not None else {}
    posities = lees_posities(api)
    for m in set(cfg["markten"]) | set(posities):
        if m not in infos:
            infos[m] = api.market_info(m)
    nav, saldi, koersen = waarde(api, cfg["markten"], posities)
    beheer_posities(api, posities, koersen, infos)
    bewaar_posities(api, posities)

    for m in cfg["markten"]:
        candles = api.candles(m, cfg["interval"], 300)
        if not candles or candles[-1]["tijd"] == laatste_candle.get(m):
            continue
        laatste_candle[m] = candles[-1]["tijd"]
        sig = strategie.signaal(candles, cfg["strategie"])
        if not sig or sig["richting"] != "koop":
            continue
        if m in posities:
            log("overgeslagen", markt=m, reden="al in bezit")
            continue
        ok, reden = risico.mag_handelen(nav, len(posities), cfg["risico"],
                                        os.path.join(MAP, "data", f"dagstand_bitvavo_{'papier' if api.papier else 'echt'}.json"))
        if not ok:
            log("overgeslagen", markt=m, reden=reden)
            continue

        ask = koersen[m]["ask"]
        afstand_stop = sig["instap"] - sig["stop"]
        afstand_doel = sig["doel"] - sig["instap"]
        units = risico.units_berekenen(nav, ask, ask - afstand_stop, 1.0, cfg["risico"], geheel=False)
        eur = units * ask
        eur = min(eur, nav * cfg["risico"].get("max_pct_per_trade", 25) / 100,
                  api.saldi().get("EUR", (0, 0))[0] * 0.99)
        minimum = float(infos[m].get("minOrderInQuoteAsset", 5))
        if eur < minimum:
            log("overgeslagen", markt=m, reden=f"bedrag te klein (€{eur:.2f}, minimum €{minimum})")
            continue

        koop = api.koop_markt(m, eur)
        if not koop["aantal"]:
            log("geweigerd", markt=m, antwoord=str(koop)[:200])
            continue
        instap = koop["prijs"]
        stop, doel = instap - afstand_stop, instap + afstand_doel
        if stop >= koersen[m]["bid"]:
            log("overgeslagen", markt=m, reden="koers al onder de stop")
            api.verkoop_markt(m, koop["aantal"], hoeveelheid_decimalen(infos[m]))
            continue
        base = m.split("-")[0]
        aantal = min(koop["aantal"], api.saldi().get(base, (0, 0))[0])
        try:
            stop_id = api.stop_order(m, aantal, stop, infos[m])
        except BitvavoFout as e:           # zonder stop geen positie: meteen weer verkopen
            log("fout", markt=m, melding=f"stop-loss mislukt, positie gesloten: {e}"[:300])
            api.verkoop_markt(m, aantal, hoeveelheid_decimalen(infos[m]))
            continue
        posities[m] = {"aantal": aantal, "instap": instap, "stop": stop, "stop_start": stop,
                       "doel": doel, "stop_id": stop_id,
                       "sinds": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        bewaar_posities(api, posities)
        log("gekocht", markt=m, eur=round(eur, 2), prijs=instap, aantal=aantal,
            stop=round(stop, 8), doel=round(doel, 8))


def maak_api(echt_geld, cfg):
    if echt_geld:
        return Bitvavo()
    return Papier(start_eur=cfg.get("papier_start_eur", 1000))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--een-keer", action="store_true")
    ap.add_argument("--echt-geld", action="store_true", help="handelen met echt geld op je Bitvavo-rekening")
    a = ap.parse_args()
    cfg = laad_instellingen()
    api = maak_api(a.echt_geld, cfg)
    log("start", stand="ECHT GELD" if a.echt_geld else "oefenstand", markten=cfg["markten"],
        strategie=cfg["strategie"].get("soort", "trend"))
    laatste, infos, fouten = {}, {}, 0
    while True:
        try:
            ronde(api, cfg, laatste, infos)
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
