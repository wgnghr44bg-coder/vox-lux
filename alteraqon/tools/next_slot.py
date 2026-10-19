"""Alteraqon: eerstvolgende vrije publicatietijd volgens alteraqon/schedule.json.

Gebruik:  python alteraqon/tools/next_slot.py short|long     -> print RFC3339 UTC-tijd (bijv. 2026-10-21T16:00:00Z)
Een tijdstip is "bezet" als een upload.json in alteraqon/*/ al "publish_at" met die tijd heeft.
Minstens 1 uur in de toekomst (YouTube eist dat een inplanning in de toekomst ligt).
"""
import datetime as dt, glob, json, os, sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def next_slot(kind: str) -> str:
    cfg = json.load(open(os.path.join(ROOT, "schedule.json"), encoding="utf-8"))
    tz = ZoneInfo(cfg["timezone"]); s = cfg[kind]
    times = s.get("times") or [s["time"]]                 # meerdere tijden per dag mogelijk
    every = int(s.get("every_days", 1))                    # bijv. 2 = om de dag (telt vanaf "start")
    start = dt.date.fromisoformat(s.get("start", "2026-10-20"))
    days = s.get("days", DAYS)
    taken = set()
    for p in glob.glob(os.path.join(ROOT, "*", "upload.json")):
        try: taken.add(json.load(open(p, encoding="utf-8")).get("publish_at"))
        except Exception: pass
    now = dt.datetime.now(tz) + dt.timedelta(hours=1)
    day = now.date()
    for _ in range(800):
        if DAYS[day.weekday()] in days and (day - start).days % every == 0:
            for tm in sorted(times):
                hh, mm = map(int, tm.split(":"))
                t = dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
                utc = t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                if t > now and utc not in taken:
                    return utc
        day += dt.timedelta(days=1)
    sys.exit("Geen vrij tijdstip gevonden.")


if __name__ == "__main__":
    print(next_slot(sys.argv[1] if len(sys.argv) > 1 else "short"))
