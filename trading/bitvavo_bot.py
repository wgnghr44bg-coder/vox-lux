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
from bitvavo import UUR_MS, Bitvavo, BitvavoFout, Papier, hoeveelheid_decimalen

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


def _r(p, prijs):
    return (prijs - p["instap"]) / (p["instap"] - p["stop_start"])


def beheer_posities(api, posities, koersen, infos):
    """Open posities: stop geraakt? doel bereikt? na TP1 stop naar instap (break-even)."""
    for m in list(posities):
        p = posities[m]
        if p.get("status") == "wacht":
            continue
        status = api.order_status(m, p["stop_id"])
        if status == "filled":
            log("stop geraakt", markt=m, instap=p["instap"], stop=p["stop"], R=round(_r(p, p["stop"]), 2))
            del posities[m]
            continue
        base = m.split("-")[0]
        if status in EINDE:                       # stop verdwenen: opnieuw beschermen
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
            vrij = api.saldi().get(base, (0, 0))[0]
            res = api.verkoop_markt(m, min(vrij, p["aantal"]) or vrij, hoeveelheid_decimalen(infos[m]))
            log("doel bereikt", markt=m, instap=p["instap"], verkocht=res["prijs"], R=round(_r(p, res["prijs"]), 2))
            del posities[m]
            continue
        if p.get("tp1") and not p.get("be") and bid >= p["tp1"] and p["stop"] < p["instap"]:
            api.annuleer(m, p["stop_id"])
            vrij = api.saldi().get(base, (0, 0))[0]
            p["stop_id"] = api.stop_order(m, vrij, p["instap"], infos[m])
            p["stop"], p["be"], p["aantal"] = p["instap"], True, vrij
            log("stop naar instap", markt=m, tp1=p["tp1"], stop=p["instap"])


def beheer_wachtend(api, posities, koersen, infos, nav, cfg):
    """Wachtende limieten: vervallen, TP1 eerst geraakt (annuleren), of koers op de limiet (kopen)."""
    nu = int(time.time() * 1000)
    for m in list(posities):
        p = posities[m]
        if p.get("status") != "wacht":
            continue
        k = koersen[m]
        if nu > p["verloopt_ms"]:
            log("limiet vervallen", markt=m, limiet=p["limiet"])
            del posities[m]
        elif k["bid"] >= p["tp1"]:
            log("limiet vervallen", markt=m, limiet=p["limiet"], reden="TP1 eerder bereikt")
            del posities[m]
        elif k["ask"] <= p["limiet"]:
            del posities[m]
            pos = koop_en_bescherm(api, m, cfg, infos, nav, koersen, p["stop"], p["doel"], tp1=p["tp1"])
            if pos:
                posities[m] = pos


def koop_en_bescherm(api, m, cfg, infos, nav, koersen, stop, doel, tp1=None, afstanden=None):
    """Koopt tegen marktprijs met 0,5% risico en zet direct een stop-loss op Bitvavo.

    afstanden=(stop, doel): stop en doel opnieuw rekenen vanaf de echte aankoopprijs (trend/smc).
    Zonder afstanden blijven stop en doel vaste prijzen (sweep).
    """
    ask = koersen[m]["ask"]
    if afstanden:
        stop, doel = ask - afstanden[0], ask + afstanden[1]
    if stop >= ask:
        log("overgeslagen", markt=m, reden="koers al onder de stop")
        return None
    units = risico.units_berekenen(nav, ask, stop, 1.0, cfg["risico"], geheel=False)
    eur = min(units * ask, nav * cfg["risico"].get("max_pct_per_trade", 25) / 100,
              api.saldi().get("EUR", (0, 0))[0] * 0.99)
    minimum = float(infos[m].get("minOrderInQuoteAsset", 5))
    if eur < minimum:
        log("overgeslagen", markt=m, reden=f"bedrag te klein (€{eur:.2f}, minimum €{minimum})")
        return None
    koop = api.koop_markt(m, eur)
    if not koop["aantal"]:
        log("geweigerd", markt=m, antwoord=str(koop)[:200])
        return None
    instap = koop["prijs"]
    if afstanden:
        stop, doel = instap - afstanden[0], instap + afstanden[1]
    base = m.split("-")[0]
    aantal = min(koop["aantal"], api.saldi().get(base, (0, 0))[0])
    if stop >= koersen[m]["bid"] or stop >= instap:
        log("overgeslagen", markt=m, reden="koers al onder de stop, direct verkocht")
        api.verkoop_markt(m, aantal, hoeveelheid_decimalen(infos[m]))
        return None
    try:
        stop_id = api.stop_order(m, aantal, stop, infos[m])
    except BitvavoFout as e:           # zonder stop geen positie: meteen weer verkopen
        log("fout", markt=m, melding=f"stop-loss mislukt, positie gesloten: {e}"[:300])
        api.verkoop_markt(m, aantal, hoeveelheid_decimalen(infos[m]))
        return None
    log("gekocht", markt=m, eur=round(eur, 2), prijs=instap, aantal=aantal,
        stop=round(stop, 8), doel=round(doel, 8), **({"tp1": round(tp1, 8)} if tp1 else {}))
    return {"status": "open", "aantal": aantal, "instap": instap, "stop": stop, "stop_start": stop,
            "doel": doel, "tp1": tp1, "be": False, "stop_id": stop_id,
            "sinds": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def ronde(api, cfg, laatste_candle, infos=None):
    infos = infos if infos is not None else {}
    posities = lees_posities(api)
    for m in set(cfg["markten"]) | set(posities):
        if m not in infos:
            infos[m] = api.market_info(m)
    nav, saldi, koersen = waarde(api, cfg["markten"], posities)
    beheer_posities(api, posities, koersen, infos)
    beheer_wachtend(api, posities, koersen, infos, nav, cfg)
    bewaar_posities(api, posities)
    stap_ms = UUR_MS.get(cfg["interval"], 3_600_000)

    for m in cfg["markten"]:
        candles = api.candles(m, cfg["interval"], cfg.get("aantal_candles", 300))
        if not candles or candles[-1]["tijd"] == laatste_candle.get(m):
            continue
        laatste_candle[m] = candles[-1]["tijd"]
        sig = strategie.signaal(candles, cfg["strategie"])
        if not sig or sig["richting"] != "koop":
            continue
        if m in posities:
            log("overgeslagen", markt=m, reden="al in bezit of limiet wacht")
            continue
        ok, reden = risico.mag_handelen(nav, len(posities), cfg["risico"],
                                        os.path.join(MAP, "data", f"dagstand_bitvavo_{'papier' if api.papier else 'echt'}.json"))
        if not ok:
            log("overgeslagen", markt=m, reden=reden)
            continue
        if sig.get("limiet"):
            if koersen[m]["ask"] <= sig["instap"]:
                pos = koop_en_bescherm(api, m, cfg, infos, nav, koersen, sig["stop"], sig["doel"], tp1=sig["tp1"])
                if pos:
                    posities[m] = pos
            else:
                verloopt = int(candles[-1]["tijd"]) + (sig["verloop_candles"] + 1) * stap_ms
                posities[m] = {"status": "wacht", "limiet": sig["instap"], "stop": sig["stop"],
                               "tp1": sig["tp1"], "doel": sig["doel"], "verloopt_ms": verloopt}
                log("limiet geplaatst", markt=m, limiet=sig["instap"], stop=sig["stop"],
                    tp1=sig["tp1"], doel=sig["doel"])
        elif sig.get("vast"):
            pos = koop_en_bescherm(api, m, cfg, infos, nav, koersen, sig["stop"], sig["doel"], tp1=sig.get("tp1"))
            if pos:
                posities[m] = pos
        else:
            pos = koop_en_bescherm(api, m, cfg, infos, nav, koersen, 0, 0,
                                   afstanden=(sig["instap"] - sig["stop"], sig["doel"] - sig["instap"]))
            if pos:
                posities[m] = pos
        bewaar_posities(api, posities)


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
