"""Risicobeheer: hoeveel units, en mag er nog gehandeld worden?"""
import json
import os
from datetime import datetime, timezone

STANDAARD = {
    "risico_per_trade_pct": 0.5,   # % van het saldo dat één trade maximaal mag verliezen
    "max_dagverlies_pct": 2.0,     # daarna stopt de bot tot morgen
    "max_open_trades": 3,
    "max_units": 100000,           # harde bovengrens per order
}

MAP = os.path.dirname(os.path.abspath(__file__))
NOODSTOP = os.path.join(MAP, "NOODSTOP")      # bestaat dit bestand, dan handelt de bot niet
DAGSTAND = os.path.join(MAP, "data", "dagstand.json")


def units_berekenen(saldo, instap, stop, omrekenfactor, cfg=None, geheel=True):
    """Aantal units zodat verlies bij de stop = risico_per_trade_pct van het saldo.

    omrekenfactor: 1 eenheid quotevaluta = zoveel rekeningvaluta (OANDA homeConversions).
    geheel: hele units (forex); False voor crypto (0,0123 BTC).
    """
    c = {**STANDAARD, **(cfg or {})}
    afstand = abs(instap - stop)
    if afstand <= 0 or omrekenfactor <= 0 or saldo <= 0:
        return 0
    risico = saldo * c["risico_per_trade_pct"] / 100
    units = risico / (afstand * omrekenfactor)
    if geheel:
        units = int(units)
    return max(0, min(units, c["max_units"]))


def noodstop_aan():
    return os.path.exists(NOODSTOP)


def zet_noodstop(aan: bool):
    if aan:
        with open(NOODSTOP, "w") as f:
            f.write(datetime.now(timezone.utc).isoformat())
    elif os.path.exists(NOODSTOP):
        os.remove(NOODSTOP)


def dagverlies_bereikt(nav, cfg=None, pad=None):
    """Onthoudt de NAV aan het begin van de (UTC-)dag en vergelijkt."""
    c = {**STANDAARD, **(cfg or {})}
    pad = pad or DAGSTAND
    vandaag = datetime.now(timezone.utc).date().isoformat()
    stand = {}
    if os.path.exists(pad):
        try:
            with open(pad) as f:
                stand = json.load(f)
        except (OSError, ValueError):
            stand = {}
    if stand.get("dag") != vandaag:
        stand = {"dag": vandaag, "start_nav": nav}
        os.makedirs(os.path.dirname(pad), exist_ok=True)
        with open(pad, "w") as f:
            json.dump(stand, f)
    start = stand["start_nav"]
    verlies_pct = (start - nav) / start * 100 if start else 0
    return verlies_pct >= c["max_dagverlies_pct"], verlies_pct


def mag_handelen(nav, aantal_open, cfg=None, pad=None):
    c = {**STANDAARD, **(cfg or {})}
    if noodstop_aan():
        return False, "noodstop staat aan"
    bereikt, pct = dagverlies_bereikt(nav, c, pad)
    if bereikt:
        return False, f"dagverlies {pct:.2f}% bereikt (max {c['max_dagverlies_pct']}%)"
    if aantal_open >= c["max_open_trades"]:
        return False, f"al {aantal_open} trades open (max {c['max_open_trades']})"
    return True, "ok"
