"""Hype-wachter (eigenaar 12 nov 2026: "bouw iets als planning die erna kijkt wat hype is, welke grote gebeurtenissen
er komen, via de pc, die je dan een seintje geeft op tijd").

Elke dag (Taakplanner "Sleep Archives hype", 08:30) op de pc, alleen lezen, kost niets (alleen YouTube API-quota):
  1. hype: slaapvideo's van grote kanalen die nu hard groeien (views per dag, laatste 30 dagen, tools/sleep_trends.py)
  2. kalender: bekende gebeurtenissen, jubilea, feestdagen en films in de komende 10 weken (stories/kalender.json)
Bij elk punt: staat er al een video van ons in de planning over dit onderwerp (en wanneer)?
Uitkomst: stories/hype.json (voor de statuswebsite, kaart "Hype en kansen") en stories/HYPE-SIGNAAL.md.
Nieuwe kansen komen één keer in stories/ROUTINE-LOG.md, zodat ze ook in het logboek van de website staan.
14 nov 2026 (eigenaar: "kun je die hype-wachter aanpassen dat hij daar beter naar kijkt"):
  - timing: ook te VROEG gepland (meer dan een week vóór de jaardag) geeft een seintje met de beste plek (za)
  - reservescripts (zonder datum) die bij een jaardag of hype passen: "inplannen op <beste plek>"
  - hype: onderwerpen die bij meerdere kanalen tegelijk groeien heten BREED (sterkste signaal)
Wat ermee gebeurt, beslist de eigenaar (of Claude op zijn verzoek): planning.txt aanpassen, vrije maandag vullen.

  python tools/hype_wacht.py               # bijwerken (zonder te pushen; het dashboard pusht)
  python tools/hype_wacht.py --zonder-youtube
"""
import datetime as dt, json, re, sys
from datetime import timezone
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
STORIES = HIER.parent / "stories"
VOORUIT = 70                      # dagen vooruit kijken
MIN_PER_DAG = 3000                # groei vanaf hier telt als hype
STOP = set("""the a an of in on to and for with how what why who was were did does life really like when that this from
into before after during your you its it is are be at by as one two all ever history sleep documentary fall asleep hours
hour boring relaxing story stories bedtime facts entire everything we know actually than more most could would
ancient medieval winter humans human people ordinary secrets secret hidden empire world freezing survive survived
death life inside years year night nights disturbing haunted strange stranger truth dark really without think
incredible something minds mind bending mysteries mystery hours happened happen complete overthrown
after body general great first last made make""".split())


def woorden(t):
    w = {w for w in re.findall(r"[a-z][a-z'-]{3,}", t.lower()) if w not in STOP}
    return w | ({"ice-age"} if "ice age" in t.lower() else set())   # korte maar belangrijke onderwerpen


def onze_planning():
    uit = []
    for p in STORIES.glob("*/planning.txt"):
        t = p.read_text(encoding="utf-8", errors="replace")
        d = re.search(r"^datum\s+\S+\s+(\d{4}-\d{2}-\d{2})", t, re.M)
        tekst = " ".join((re.search(rf"^{k}\s+(.+)$", t, re.M) or [None, ""])[1] for k in ("onderwerp", "titel"))
        gemaakt = bool(re.search(r"^link\s+https://youtu", t, re.M) or re.search(r"^status\s+klaar", t, re.M))
        uit.append({"map": p.parent.name, "datum": d.group(1) if d else "", "tekst": tekst, "gemaakt": gemaakt})
    return uit


def zoek_in_planning(zoekwoorden, plan):
    """Video's van ons waarvan onderwerp/titel een zoekwoord bevat."""
    gevonden = []
    for z in zoekwoorden:
        for v in plan:
            if re.search(rf"\b{re.escape(z.lower())}", v["tekst"].lower()) and v not in gevonden:
                gevonden.append(v)
    return gevonden


def lijkt_op_planning(titel, plan):
    """Twee of meer gewone woorden gelijk (of één bijzonder woord, met hoofdletter, zoals Babylon of Titanic)."""
    w = woorden(titel)
    namen = {x.lower() for x in re.findall(r"\b[A-Z][a-z]{4,}\b", titel)} - STOP
    beste = []
    for v in plan:
        vw = woorden(v["tekst"])
        if len(w & vw) >= 2 or (namen & vw) or ("ice-age" in (w & vw)):
            beste.append(v)
    return beste


def pasen(j):
    a, b, c = j % 19, j // 100, j % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return dt.date(j, (h + l - 7 * m + 114) // 31, (h + l - 7 * m + 114) % 31 + 1)


def thanksgiving(j):
    d = dt.date(j, 11, 1)
    return d + dt.timedelta(days=(3 - d.weekday()) % 7 + 21)


def kalender(vandaag, plan):
    k = json.loads((STORIES / "kalender.json").read_text(encoding="utf-8"))
    eind = vandaag + dt.timedelta(days=VOORUIT)
    uit = []
    for j in (vandaag.year, vandaag.year + 1):
        for g in k["gebeurtenissen"]:
            d = dt.date(j, int(g["datum"][:2]), int(g["datum"][3:]))
            if not vandaag <= d <= eind:
                continue
            jaren = j - g["jaar"] - (1 if g["jaar"] < 0 else 0)
            rond = jaren % 25 == 0 or jaren % 10 == 0
            ons = zoek_in_planning(g["zoek"], plan)
            if g["jaar"] == 0:                              # jaarlijks, zonder jubileum (kerst, zonnewende)
                uit.append({"soort": "gebeurtenis", "datum": d.isoformat(), "naam": g["naam"], "sterk": True, "ons": ons})
                continue
            uit.append({"soort": "jubileum" if rond else "gebeurtenis", "datum": d.isoformat(),
                        "naam": f"{g['naam']} ({jaren} jaar)", "sterk": rond or bool(ons), "ons": ons})
        for f in k["feestdagen"]:
            s = f["datum"]
            d = pasen(j) if s == "pasen" else thanksgiving(j) if s == "thanksgiving" else \
                dt.date.fromisoformat(s) if len(s) == 10 else dt.date(j, int(s[:2]), int(s[3:]))
            if vandaag <= d <= eind and d.year == j:
                uit.append({"soort": "feestdag", "datum": d.isoformat(), "naam": f["naam"], "sterk": True,
                            "ons": zoek_in_planning(f.get("zoek", f["naam"].split()[:1]), plan)})
    for f in k.get("films", []):
        d = dt.date.fromisoformat(f["datum"])
        if vandaag <= d <= eind:
            uit.append({"soort": "film", "datum": d.isoformat(), "naam": f["naam"], "sterk": True,
                        "ons": zoek_in_planning(f.get("zoek", []), plan)})
    uit = [dict(x) for x in {(x["datum"], x["naam"]): x for x in uit}.values()]
    return sorted(uit, key=lambda x: x["datum"])


def hype(plan):
    import sleep_trends as st
    token = st.access_token()
    nu = dt.datetime.now(timezone.utc)
    ids = sorted(st.recent_ids(token, nu - dt.timedelta(days=30)))
    rijen, alle = [], []
    for i in range(0, len(ids), 50):
        for v in st.get(token, "videos", part="snippet,statistics", id=",".join(ids[i:i + 50])).get("items", []):
            t, kanaal = v["snippet"]["title"], v["snippet"]["channelTitle"]
            if kanaal == "Sleep Archives":
                continue
            slaap = "sleep" in t.lower() or kanaal in st.CHANNELS.values()
            pub = dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
            per_dag = int(v["statistics"].get("viewCount", 0)) / max((nu - pub).total_seconds() / 86400, 1)
            if slaap:                                       # 15 nov: alle titels bewaren voor de titelwachter
                alle.append({"titel": t, "kanaal": kanaal, "per_dag": round(per_dag), "datum": pub.date().isoformat()})
            if per_dag >= MIN_PER_DAG and slaap:
                rijen.append({"soort": "hype", "per_dag": round(per_dag), "titel": t, "kanaal": kanaal,
                              "id": v["id"], "datum": pub.date().isoformat(), "ons": lijkt_op_planning(t, plan)})
    # BREED: hetzelfde onderwerp (naam met hoofdletter, of 2 gewone woorden) groeit bij meerdere kanalen tegelijk
    for r in rijen:
        n = {x.lower() for x in re.findall(r"\b[A-Z][a-z]{3,}\b", r["titel"])} - STOP
        w = woorden(r["titel"])
        andere = {q["kanaal"] for q in rijen if q is not r and q["kanaal"] != r["kanaal"]
                  and (n & ({x.lower() for x in re.findall(r"\b[A-Z][a-z]{3,}\b", q["titel"])} - STOP) or len(w & woorden(q["titel"])) >= 2)}
        r["breed"] = len(andere)
    rijen.sort(key=lambda r: -(r["per_dag"] * (1 + 0.5 * r["breed"])))
    (STORIES / "concurrent.json").write_text(json.dumps({"bijgewerkt": nu.strftime("%Y-%m-%d %H:%M"),
                                                         "videos": sorted(alle, key=lambda r: -r["per_dag"])},
                                                        indent=1, ensure_ascii=False), encoding="utf-8")
    return rijen[:25]


PLEKDAGEN = (5,)                   # za 21:00 (eigenaar 19 nov avond: Sleep 1x per week)


BEZET = {}                         # datum -> map, gevuld in main()


def beste_plek(datum, vandaag):
    """Laatste publicatiedag (za) op of vóór de jaardag, minstens 2 dagen vanaf vandaag. Een plek die al door
    een andere video bezet is, krijgt '(bezet door <map>, ruilen?)' erachter als er in die week geen vrije plek is."""
    d = dt.date.fromisoformat(datum)
    kand = [d - dt.timedelta(days=i) for i in range(0, 7)]
    kand = [k for k in kand if k.weekday() in PLEKDAGEN and k >= vandaag + dt.timedelta(days=2)]
    if not kand:
        return ""
    eerste = kand[0].isoformat()
    if eerste not in BEZET:
        return eerste
    vrij = next((k.isoformat() for k in kand if k.isoformat() not in BEZET), "")
    return f"{eerste} (bezet door {BEZET[eerste]}, ruilen?)" + (f", of vrij op {vrij}" if vrij else "")


def advies(x, vandaag):
    toekomst = [v for v in x["ons"] if v["datum"] and v["datum"] >= vandaag.isoformat()]
    reserve = [v for v in x["ons"] if not v["datum"] and not v.get("gemaakt") and not v["map"].startswith("_")]
    plek = beste_plek(x["datum"], vandaag) if x["soort"] != "hype" else ""
    if toekomst:
        v = min(toekomst, key=lambda v: v["datum"])
        if x["soort"] != "hype" and v["datum"] > x["datum"]:
            return f"staat gepland op {v['datum']} ({v['map']}), NA de datum: naar voren halen" + (f", beste plek {plek}" if plek else "?")
        if x["soort"] != "hype" and (dt.date.fromisoformat(x["datum"]) - dt.date.fromisoformat(v["datum"])).days > 7:
            return f"staat gepland op {v['datum']} ({v['map']}), TE VROEG: beste plek {plek or x['datum']} (vlak voor de jaardag)"
        return f"staat gepland op {v['datum']} ({v['map']})" + (" GOED getimed" if x["soort"] != "hype" else "")
    if reserve:
        return f"KANS: reservescript {reserve[0]['map']} past hierop, inplannen" + (f" op {plek}" if plek else "")
    if x["ons"]:
        return f"al gemaakt ({x['ons'][0]['map']})"
    return "KANS: nog niets van ons over dit onderwerp" + (f" (beste plek {plek})" if plek else "")


def main():
    vandaag = dt.date.today()
    plan = onze_planning()
    BEZET.update({v["datum"]: v["map"] for v in plan if v["datum"]})
    punten = kalender(vandaag, plan)
    if "--zonder-youtube" not in sys.argv:
        try:
            punten = hype(plan) + punten
        except Exception as e:                             # geen internet/quota: kalender gaat gewoon door
            punten.insert(0, {"soort": "fout", "naam": f"hype-check mislukt: {e}"[:200], "datum": vandaag.isoformat(),
                              "ons": []})
    for p in punten:
        p["advies"] = advies(p, vandaag) if p["soort"] != "fout" else ""
        p["ons"] = [v["map"] for v in p["ons"]]
    uit = {"bijgewerkt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "punten": punten}
    oud = json.loads((STORIES / "hype.json").read_text(encoding="utf-8")) if (STORIES / "hype.json").exists() else {}
    gezien = {(p.get("naam") or p.get("titel")) for p in oud.get("punten", [])}
    log_t = (STORIES / "ROUTINE-LOG.md").read_text(encoding="utf-8", errors="replace")     # nooit twee keer hetzelfde seintje
    gezien |= {(p.get("naam") or p.get("titel")) for p in punten if f"SEINTJE {p.get('titel') or p.get('naam')} ->" in log_t}
    (STORIES / "hype.json").write_text(json.dumps(uit, indent=1, ensure_ascii=False), encoding="utf-8")
    regels = [f"# Hype en kansen ({uit['bijgewerkt']})", "",
              "Automatisch door tools/hype_wacht.py. KANS = nog niets van ons of een reservescript past; NA de datum = te laat; TE VROEG = ruim vóór de jaardag; BREED = groeit bij meerdere kanalen.", ""]
    for p in punten:
        if p["soort"] == "hype":
            breed = f" BREED (+{p['breed']} kanalen)" if p.get("breed") else ""
            regels.append(f"- HYPE {p['per_dag']:,}/dag{breed}: {p['titel']} ({p['kanaal']}) -> {p['advies']}")
        else:
            regels.append(f"- {p['datum']} {p['soort'].upper()}: {p['naam']} -> {p['advies']}")
    (STORIES / "HYPE-SIGNAAL.md").write_text("\n".join(regels) + "\n", encoding="utf-8")
    nieuw = [p for p in punten if (p.get("naam") or p.get("titel")) not in gezien
             and any(w in p.get("advies", "") for w in ("KANS", "naar voren", "TE VROEG"))
             and (p["soort"] == "hype" or p.get("sterk"))]
    if nieuw:
        with open(STORIES / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
            for p in nieuw[:5]:
                f.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} hype-wachter: SEINTJE {p.get('titel') or p['naam']}"
                        f" -> {p['advies']}\n")
    print("\n".join(regels))
    try:                                                    # 15 nov: daarna meteen de titels (tools/titel_wacht.py)
        import titel_wacht
        titel_wacht.main()
    except Exception as e:
        print("titelwachter:", e)


if __name__ == "__main__":
    main()
