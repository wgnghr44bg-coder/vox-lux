"""Controleert een script inhoudelijk, zonder Claude (eigenaar 9 nov 2026: "hij moet dat zelf doen vanuit de pc
controleren of alles goed werkt"). Aanleiding: het lokale Gettysburg-script had hoofdstukken over Soedan en Maersk en
"planes on the tarmac" in 1863, terwijl de vaste controles (lengte, leesbaarheid, afwisseling) goed waren.

Controles:
  1. vorm: 80-100 feitjes, 14.000-21.000 woorden, begin 200-340 woorden, slot 90-200 woorden met "another ... story ...
     on the screen", abonneren, en als laatste "Sleep well, and good night."; geen "Tonight/Hello" aan het begin
  2. tijd: woorden die niet bij de tijd passen (bv. plane, tarmac, phone, car vóór 1900), behalve in feitjes die
     duidelijk over later gaan (jaartal of "today")
  3. onderwerp: het lokale model (Ollama) beoordeelt per feitje en per hoofdstuktitel of het over het onderwerp gaat
  4. afwisseling: tools/check_afwisseling.py
Uitslag: <map>/scriptcheck.json en laatste regel SCRIPT GOED / SCRIPT FOUT (+ redenen).

  python tools/script_check.py stories/<map> [--zonder-model]
"""
import json, re, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER / "scriptgen"))

MODERN = {  # woord: vanaf welk jaar het kan bestaan
    "airplane": 1903, "aeroplane": 1903, "plane": 1903, "planes": 1903, "airport": 1910, "tarmac": 1910, "jet": 1940,
    "helicopter": 1940, "car": 1890, "cars": 1890, "automobile": 1890, "truck": 1900, "highway": 1920, "asphalt": 1870,
    "telephone": 1876, "phone": 1876, "radio": 1920, "television": 1930, "tv": 1930, "computer": 1940, "internet": 1990,
    "electric": 1880, "electricity": 1880, "light bulb": 1880, "neon": 1910, "plastic": 1910, "photograph": 1839,
    "camera": 1839, "railway": 1825, "train": 1825, "locomotive": 1825, "steamship": 1820, "rifle": 1500, "gun": 1350,
    "cannon": 1330, "printing press": 1450, "newspaper": 1605, "clock": 1300, "tea": 1600, "coffee": 1500, "potato": 1550,
    "tomato": 1550, "tobacco": 1550, "chocolate": 1550}


def jaar_van(m):
    t = (m / "planning.txt").read_text(encoding="utf-8", errors="replace") if (m / "planning.txt").exists() else ""
    bc = re.search(r"\b(\d{1,4}) ?(BC|v\.? ?Chr)", t)
    if bc:
        return -int(bc.group(1))
    j = re.findall(r"\b(1[0-9]{3})\b", (re.search(r"^onderwerp (.+)$", t, re.M) or [None, ""])[1] + " " + m.name)
    return int(j[0]) if j else None


def blokken(m):
    sf = m / "src-feiten"
    uit, topic = [], ""
    for p in sorted(sf.glob("deel*.txt"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0)):
        for b in re.split(r"\r?\n===\r?\n", p.read_text(encoding="utf-8")):
            t = re.search(r"^TOPIC:\s*(.+)$", b, re.M)
            if t:
                topic = t.group(1).strip()
                continue
            h = re.search(r"^HEAD:\s*(.+)$", b, re.M)
            bo = re.search(r"^BODY:\s*(.+)$", b, re.M | re.S)
            im = re.search(r"^IMG:\s*(.+?)\s*\|\s*(.+)$", b, re.M)
            if h and bo:
                uit.append({"topic": topic, "head": h.group(1).strip(), "body": " ".join(bo.group(1).split()),
                            "img": im.group(2).strip() if im else ""})
    return uit


SAMENGESTELD = [r"plane trees?", r"plane-trees?"]          # 'plane' als boom, niet als vliegtuig
ONTKENNING = re.compile(r"\b(no|not|never|without|nothing like|none|neither|nor|wasn't|weren't|didn't|had no|like ours|"
                        r"in a way|as if|long before|centuries before|would not exist|did not exist|yet to)\b", re.I)


def tijdwoord_in(w, tekst, ontkenning_telt=True):
    """Staat het moderne woord er echt in als iets dat er toen was? Niet bij 'plane trees', en (in de tekst) niet in een
    zin met een ontkenning of vergelijking ('There was no radio', 'no clocks like ours'): 10 nov 2026 werden Scott en
    Rome daardoor onterecht afgekeurd."""
    for s in SAMENGESTELD:
        tekst = re.sub(s, "", tekst, flags=re.I)
    for zin in re.split(r"(?<=[.!?])\s+", tekst):
        if re.search(rf"\b{re.escape(w)}\b", zin, re.I) and not (ontkenning_telt and ONTKENNING.search(zin)):
            return True
    return False


def woorden(t):
    return len(t.split())


def controleer(m, met_model=True):
    m = Path(m)
    sf = m / "src-feiten"
    fout, info = [], {}
    if not (sf / "begin.txt").exists():
        return ["geen src-feiten/begin.txt (nog oude opbouw)"], info
    begin = (sf / "begin.txt").read_text(encoding="utf-8")
    slot = (sf / "slot.txt").read_text(encoding="utf-8") if (sf / "slot.txt").exists() else ""
    fb = blokken(m)
    totaal = woorden(begin) + woorden(slot) + sum(woorden(b["head"]) + woorden(b["body"]) for b in fb)
    info.update(feitjes=len(fb), woorden=totaal, begin=woorden(begin), slot=woorden(slot),
                onderwerpen=len({b["topic"] for b in fb}))
    # 1. vorm
    if not 80 <= len(fb) <= 100:
        fout.append(f"{len(fb)} feitjes (80-100 nodig)")
    if not 14000 <= totaal <= 21000:
        fout.append(f"{totaal} woorden (14.000-21.000 nodig)")
    if not 200 <= woorden(begin) <= 340:
        fout.append(f"begin {woorden(begin)} woorden (200-340 nodig)")
    if re.match(r"\s*(tonight|hello|welcome)", begin, re.I):
        fout.append("begin start met Tonight/Hello/Welcome")
    if not re.search(r"subscri", begin, re.I):
        fout.append("geen abonneer-zin in het begin")
    if not 90 <= woorden(slot) <= 200:
        fout.append(f"slot {woorden(slot)} woorden (90-200 nodig)")
    if not re.search(r"another .*(story|video).*screen", slot, re.I | re.S):
        fout.append('slot mist "another ... story ... on the screen"')
    if not slot.strip().endswith("Sleep well, and good night."):
        fout.append('slot eindigt niet op "Sleep well, and good night."')
    # 2. tijd
    jaar = jaar_van(m)
    info["jaar"] = jaar
    if jaar:
        stukken = [("begin", begin, ""), ("slot", slot, "")] + [(f"feitje {i + 1}", b["head"] + " " + b["body"], b["img"])
                                                               for i, b in enumerate(fb)]
        for naam, tekst, img in stukken:
            later = re.search(r"\b(today|nowadays|modern|museum|tourists?|visitors?|anniversary|centuries later)\b", tekst, re.I) \
                or any(int(j) > jaar + 15 for j in re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", tekst))
            if (later and naam.startswith("feitje")) or naam in ("begin", "slot"):   # begin/slot praten tegen de luisteraar van nu
                continue
            for w, vanaf in MODERN.items():
                if jaar >= vanaf - 5:
                    continue
                if img and tijdwoord_in(w, img, ontkenning_telt=False):          # in beeld: echt fout
                    fout.append(f"{naam} (beeld): '{w}' past niet bij {jaar}")
                elif tijdwoord_in(w, tekst):                                      # in de tekst: vaak een vergelijking
                    info.setdefault("let_op", []).append(f"{naam}: '{w}' in de tekst (vergelijking of fout?)")
    # 3. onderwerp (lokaal model)
    if met_model and fb:
        import llm
        onderwerp = (re.search(r"^onderwerp (.+)$", (m / "planning.txt").read_text(encoding="utf-8"), re.M) or [None, m.name])[1]
        topics = sorted({b["topic"] for b in fb if b["topic"]})
        r = llm.json_vraag(f"Video topic: {onderwerp}.\nChapter titles: {topics}\nWhich chapter titles are clearly NOT about "
                           "this topic (its place, time, people, daily life, events, or what remains of it today)?\n"
                           'JSON: {"off_topic": ["...", ...]}', temp=0.0, max_tokens=300)
        def echt_ernaast(tekst):
            """Tweede, ruime vraag: alleen afkeuren als het op GEEN enkele manier met het onderwerp te maken heeft
            (test 9 nov: Kennedy en de Newmans werden bij 'Life in Dallas, November 1963' eerst onterecht afgekeurd)."""
            q = llm.json_vraag(f"Video topic: {onderwerp}.\nText: {tekst}\n\nIs this text connected to the topic in ANY way: "
                               "the same place, the same period, people who lived there or visited, events that happened "
                               "there or affected it, how it was remembered later, or its everyday life? Answer false only "
                               "if it is clearly about something else (another country, another war, another era).\n"
                               'JSON: {"connected": true or false}', temp=0.0, max_tokens=40)
            return isinstance(q, dict) and q.get("connected") is False
        for t in r.get("off_topic", []) if isinstance(r, dict) else []:
            if t in topics:
                koppen = " / ".join(b["head"] for b in fb if b["topic"] == t)[:900]
                if echt_ernaast(f"Chapter '{t}' with these opening sentences: {koppen}"):
                    fout.append(f"hoofdstuk '{t}' gaat niet over het onderwerp")
        weg = []
        for i in range(0, len(fb), 10):
            groep = fb[i:i + 10]
            lijst = "\n".join(f"{i + k + 1}: {b['head']} {b['body'][:300]}" for k, b in enumerate(groep))
            r = llm.json_vraag(f"Video topic: {onderwerp}.\nNumbered paragraphs:\n{lijst}\n\nWhich paragraph numbers are "
                               "clearly NOT about this topic (another country, another war, another century, a company, "
                               "modern events unrelated to the place)? Be strict but fair.\n"
                               'JSON: {"off_topic": [numbers]}', temp=0.0, max_tokens=200)
            weg += [n for n in (r.get("off_topic", []) if isinstance(r, dict) else []) if isinstance(n, int)]
        # woorden die niet bij de tijd passen in de tekst: het model beslist of het een vergelijking is of een fout
        for lo in list(info.get("let_op", [])):
            n = re.match(r"feitje (\d+)", lo)
            tekst = (fb[int(n.group(1)) - 1]["head"] + " " + fb[int(n.group(1)) - 1]["body"]) if n else \
                (begin if lo.startswith("begin") else slot)
            w = re.search(r"'([^']+)'", lo).group(1)
            r = llm.json_vraag(f"Text from a calm history video set in {jaar if jaar > 0 else str(-jaar) + ' BC'}:\n{tekst}\n\n"
                               f"Is the word '{w}' used for something that really appears in that time (an error), or only "
                               "as a comparison, or about a later time? "
                               'JSON: {"error": true or false}', temp=0.0, max_tokens=60)
            if isinstance(r, dict) and r.get("error") is True:
                fout.append(lo.replace("(vergelijking of fout?)", "(fout volgens het model)"))
        for n in sorted(set(weg)):
            if 0 < n <= len(fb) and echt_ernaast(fb[n - 1]["head"] + " " + fb[n - 1]["body"][:600]):
                fout.append(f"feitje {n} gaat niet over het onderwerp: {fb[n - 1]['head'][:70]}")
        fout = [f for f in fout if f]
        try:
            requests = __import__("requests")
            requests.post("http://127.0.0.1:11434/api/generate", json={"model": llm.MODEL, "keep_alive": 0}, timeout=30)
        except Exception:
            pass
    # 4. afwisseling
    r = subprocess.run([sys.executable, str(HIER / "check_afwisseling.py"), str(m)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if "AFWISSELING GOED" not in r.stdout:
        fout.append("afwisseling: " + "; ".join(r.stdout.strip().splitlines()[:2])[:160])
    return fout, info


if __name__ == "__main__":
    m = Path(sys.argv[1])
    fout, info = controleer(m, met_model="--zonder-model" not in sys.argv)
    (m / "scriptcheck.json").write_text(json.dumps({"fouten": fout, "info": info}, indent=1, ensure_ascii=False), encoding="utf-8")
    for f in fout:
        print("  -", f)
    print(f"{m.name}: {info}")
    print("SCRIPT GOED" if not fout else f"SCRIPT FOUT ({len(fout)} punten)")
    sys.exit(1 if fout else 0)
