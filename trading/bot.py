"""De handelsbot. Draait in een lus en kijkt elke minuut of er een nieuwe candle is.

Oefengeld (standaard):   python bot.py
Eén ronde en stoppen:    python bot.py --een-keer
Echt geld (pas na weken goede resultaten op oefengeld):
    OANDA_OMGEVING=live  python bot.py --echt-geld
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import risico
import strategie
from oanda import Oanda, OandaFout

MAP = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(MAP, "data", "log.jsonl")


def laad_instellingen():
    with open(os.path.join(MAP, "instellingen.json")) as f:
        return json.load(f)


def log(soort, **info):
    regel = {"tijd": datetime.now(timezone.utc).isoformat(timespec="seconds"), "soort": soort, **info}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(regel) + "\n")
    print(f"[{regel['tijd']}] {soort}: {info}", flush=True)


def ronde(api, cfg, laatste_candle):
    acc = api.samenvatting()
    nav = float(acc["NAV"])
    saldo = float(acc["balance"])
    trades = api.open_trades()
    open_per_inst = {t["instrument"] for t in trades}

    for inst in cfg["instrumenten"]:
        candles = api.candles(inst, cfg["granularity"], 300)
        if not candles or candles[-1]["tijd"] == laatste_candle.get(inst):
            continue                      # geen nieuwe afgesloten candle
        laatste_candle[inst] = candles[-1]["tijd"]

        sig = strategie.signaal(candles, cfg["strategie"])
        if not sig:
            continue
        if inst in open_per_inst:
            log("overgeslagen", instrument=inst, reden="er staat al een trade open")
            continue
        ok, reden = risico.mag_handelen(nav, len(trades), cfg["risico"])
        if not ok:
            log("overgeslagen", instrument=inst, reden=reden)
            continue

        info = api.instrument_info(inst)
        decimalen = int(info["displayPrecision"])
        quote = inst.split("_")[1]
        p = api.prijs(inst)
        if not p["handelbaar"]:
            log("overgeslagen", instrument=inst, reden="markt dicht")
            continue
        factor = p["omrekening"].get(quote, 1.0 if quote == acc["currency"] else 0)
        instap = p["ask"] if sig["richting"] == "koop" else p["bid"]
        afstand_stop = abs(sig["instap"] - sig["stop"])
        afstand_doel = abs(sig["doel"] - sig["instap"])
        if sig["richting"] == "koop":
            stop, doel = instap - afstand_stop, instap + afstand_doel
        else:
            stop, doel = instap + afstand_stop, instap - afstand_doel

        units = risico.units_berekenen(saldo, instap, stop, factor, cfg["risico"])
        min_units = float(info.get("minimumTradeSize", 1))
        if units < min_units:
            log("overgeslagen", instrument=inst, reden=f"te weinig units ({units})")
            continue
        if sig["richting"] == "verkoop":
            units = -units
        res = api.market_order(inst, units, stop, doel, decimalen)
        gevuld = res.get("orderFillTransaction")
        if gevuld:
            log("trade", instrument=inst, richting=sig["richting"], units=units,
                prijs=gevuld.get("price"), stop=round(stop, decimalen), doel=round(doel, decimalen))
            trades.append({"instrument": inst})
            open_per_inst.add(inst)
        else:
            log("geweigerd", instrument=inst, antwoord=str(res)[:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--een-keer", action="store_true", help="één ronde draaien en stoppen")
    ap.add_argument("--echt-geld", action="store_true", help="nodig om op een live-rekening te handelen")
    a = ap.parse_args()

    cfg = laad_instellingen()
    api = Oanda()
    if api.omgeving == "live" and not a.echt_geld:
        sys.exit("Live-rekening gekozen maar --echt-geld ontbreekt. Gestopt voor de veiligheid.")
    log("start", omgeving=api.omgeving, instrumenten=cfg["instrumenten"])

    laatste = {}
    fouten = 0
    while True:
        try:
            ronde(api, cfg, laatste)
            fouten = 0
        except (OandaFout, OSError, ValueError, KeyError) as e:
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
