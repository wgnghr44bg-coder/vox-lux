"""Scriptgenerator zonder Claude (eigenaar 8 nov 2026: "iets bouwen dat net zo goed is maar dan zonder Claude", "hij
moet het nu eigenlijk al stand alone kunnen doen"). Lokaal model via Ollama (tools/scriptgen/llm.py), feiten alleen uit
bronnen (Wikipedia + bij ombouwen het oude script), precies het recept van stories/PROMPT-SCRIPT-PC.md en OPBOUW.md,
met dezelfde harde controles. Pas als alles goed is: commit + push. Anders melding in stories/ROUTINE-LOG.md.

  python tools/scriptgen/generator.py                 # kiest zelf: eerst oudste oude script ombouwen, anders nieuw
  python tools/scriptgen/generator.py --map stories/gettysburg-1863 --test   # één map, niet pushen (proef)
"""
import argparse, datetime, json, random, re, shutil, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parent.parent
STORIES = REPO / "stories"
sys.path.insert(0, str(HIER))
import llm, bronnen

OPENINGEN = ["scène", "mythe", "persoon", "voorwerp", "raadsel"]
TITELSOORTEN = {"life-really-like": "What Was Life Really Like ...?", "how-survive": "How Did People ... / How Did ... Survive ...?",
                "what-actually": "What Did ... Actually ...?", "why": "Why Did ...?", "what-happened": "What Happened to ... After ...?"}
OPENING_EN = {"scène": "a scene in the second person ('Imagine ...') that drops the listener into the place and time",
              "mythe": "a popular myth or picture people have, then a gentle hint that the truth was quieter and different",
              "persoon": "one real person at one real moment, told quietly",
              "voorwerp": "one ordinary object from that time, described closely",
              "raadsel": "a small real puzzle or contradiction from the story that makes the listener curious"}
SYSTEEM = (
    "You write calm history scripts for a YouTube sleep channel called Sleep Archives. The narrator is a calm older "
    "British man. Style: simple, warm, spoken English, like telling a friend a story by the fire. Short sentences of "
    "8 to 15 words, at most two commas. Common words. Few names and dates in a row. Nothing frightening or gory. "
    "Now and then speak to the listener ('you'), and now and then a gentle question. Where it fits, contrast the "
    "popular myth with what really happened, using 'Yet ...' or 'That does not mean ...'. End paragraphs on a quiet, "
    "still thought. Never invent facts: use ONLY facts that appear in the source text you are given. "
    "No lists, no headings, no markdown, no emojis.")


def log(tekst):
    regel = f"- {datetime.datetime.now():%Y-%m-%d %H:%M} scriptgenerator (lokaal): {tekst}\n"
    print(regel, end="", flush=True)
    with open(STORIES / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
        f.write(regel)


def lees_planning(m):
    p = m / "planning.txt"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    g = lambda k: (re.search(rf"^{k}\s+(.+)$", t, re.M) or [None, ""])[1].strip()
    d = re.search(r"^datum\s+\S+\s+(\d{4}-\d{2}-\d{2})", t, re.M)
    return {"tekst": t, "status": g("status"), "datum": d.group(1) if d else "", "onderwerp": g("onderwerp"),
            "opening": g("opening").split()[0] if g("opening") else "", "titelsoort": g("titelsoort").split()[0] if g("titelsoort") else "",
            "soort": g("soort").split()[0] if g("soort") else "", "reserve": "reserve" in g("datum")}


def kies_map():
    grens = (datetime.date.today() + datetime.timedelta(days=2)).isoformat()
    kandidaten = []
    for m in STORIES.iterdir():
        if not m.is_dir():
            continue
        p = lees_planning(m)
        if (p["status"].startswith("script-klaar") and "nieuwe opbouw" not in p["status"]) or p["status"].startswith("in-wording"):
            if p["datum"] and p["datum"] >= grens:
                kandidaten.append((0, p["datum"], m))
            elif p["reserve"]:
                kandidaten.append((1, m.name, m))
    return sorted(kandidaten)[0][2] if kandidaten else None


def vorige_video(m, datum):
    rij = sorted((p["datum"], a, p) for a in STORIES.iterdir() if a.is_dir() and a != m
                 for p in [lees_planning(a)] if p["datum"] and p["datum"] < (datum or "9999"))
    return rij[-1][2] if rij else {"opening": "", "titelsoort": ""}


def oud_script(m):
    """Het originele script (door Claude geschreven): eerst src/*.txt (oude opbouw); script-cues.txt alleen als er nog
    geen src-feiten zijn (anders is script-cues al de nieuwe, mogelijk afgekeurde, versie)."""
    delen = [p for p in sorted((m / "src").glob("*.txt")) if p.stat().st_size > 2000 and p.name != "beelden.tsv"]
    if delen:
        return re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]|^--$", " ", "\n\n".join(p.read_text(encoding="utf-8") for p in delen), flags=re.M)
    p = m / "script-cues.txt"
    if p.exists() and p.stat().st_size > 2000 and not (m / "src-feiten").exists():
        return re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]|^--$", " ", p.read_text(encoding="utf-8"), flags=re.M)
    return ""


def woorden(t):
    return len(t.split())


def zinnen_ok(t):
    z = [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s]
    return z and sum(woorden(s) for s in z) / len(z) <= 17 and max(s.count(",") for s in z) <= 3


# ---------- 1. feiten verzamelen ----------
def feiten_uit_bronnen(onderwerp, stukjes, max_per_stuk=10):
    feiten = []
    for s in stukjes:
        try:
            r = llm.json_vraag(
                f"Topic of the video: {onderwerp}.\nSource text:\n{s['tekst']}\n\n"
                f"List up to {max_per_stuk} calm, surprising or touching facts from this source that fit a sleep video about "
                "the topic: everyday life, objects, places, ordinary people, small details. Skip battles in detail, gore and "
                "long lists of numbers. Each fact one short sentence, strictly as stated in the source.\n"
                'JSON: [{"fact": "..."}]', SYSTEEM, temp=0.3)
            for f in r if isinstance(r, list) else []:
                if isinstance(f, dict) and f.get("fact"):
                    feiten.append({"id": len(feiten), "fact": f["fact"].strip(), "stuk": s["id"]})
        except Exception as e:
            print("  stuk overgeslagen:", e, flush=True)
    return feiten


def youtube_dubbel(feiten, stukjes):
    """Een feit uit een YouTube-transcriptie telt alleen als een tweede (niet-YouTube) bron het bevestigt; het feitje
    wordt dan geschreven vanuit die tweede bron. Zo komen verzonnen feiten van AI-kanalen er niet in."""
    yt = {s["id"] for s in stukjes if s.get("youtube")}
    anders = [s for s in stukjes if not s.get("youtube")]
    if not yt:
        return feiten
    woord = lambda t: set(w for w in re.findall(r"[a-z]{4,}", t.lower()))
    uit = []
    for f in feiten:
        if f["stuk"] not in yt:
            uit.append(f)
            continue
        fw = woord(f["fact"])
        kandidaat = sorted(anders, key=lambda s: -len(fw & woord(s["tekst"])))[:3]
        for s in kandidaat:
            r = llm.json_vraag(f"Fact: {f['fact']}\nSource text:\n{s['tekst'][:3500]}\n\nDoes the source text clearly support "
                               'this fact? JSON: {"supported": true or false}', temp=0.0, max_tokens=30)
            if isinstance(r, dict) and r.get("supported") is True:
                uit.append({**f, "stuk": s["id"], "via_youtube": True})
                break
    print(f"  YouTube-feiten: {sum(1 for f in feiten if f['stuk'] in yt)} gevonden, "
          f"{sum(1 for f in uit if f.get('via_youtube'))} bevestigd door een tweede bron", flush=True)
    return [{**f, "id": i} for i, f in enumerate(uit)]


def opzet(onderwerp, feiten, n_onderwerpen):
    lijst = "\n".join(f"{f['id']}: {f['fact']}" for f in feiten)
    r = llm.json_vraag(
        f"Video topic: {onderwerp}.\nNumbered facts:\n{lijst}\n\n"
        f"Plan the video as one calm journey in {n_onderwerpen} chapters, in a logical order (usually time order: "
        "the world before, daily life, the main events told gently, what came after, what remains today). "
        "Each chapter gets a short title (2-6 words) and 7 to 9 fact numbers. Use every fact at most once; choose the "
        "most interesting and varied ones. Total about 90 facts.\n"
        'JSON: [{"title": "...", "facts": [3, 17, ...]}]', SYSTEEM, temp=0.4, max_tokens=3000, ctx=16384)
    uit, gebruikt = [], set()
    for h in r:
        ids = [i for i in h.get("facts", []) if isinstance(i, int) and 0 <= i < len(feiten) and i not in gebruikt]
        gebruikt.update(ids)
        if ids:
            uit.append({"title": h.get("title", "").strip()[:60], "facts": ids})
    return uit


# ---------- 2. schrijven ----------
VOORBEELD = None


def voorbeeld():
    global VOORBEELD
    if VOORBEELD is None:
        t = (STORIES / "egypte-toetanchamon" / "src-feiten" / "deel1.txt").read_text(encoding="utf-8")
        VOORBEELD = "\n===\n".join(t.split("\n===\n")[1:3])
    return VOORBEELD


def schrijf_feitje(onderwerp, feit, bron, eerdere_koppen):
    for poging in range(4):
        r = llm.json_vraag(
            f"Video topic: {onderwerp}.\nThe fact to tell: {feit}\nSource text (use only facts from here):\n{bron}\n\n"
            f"Two examples of the exact style and length:\n{voorbeeld()}\n\n"
            "Write ONE fact section like the examples:\n"
            "- head: one sentence (10-22 words) that already surprises or touches, about this fact.\n"
            "- body: 160-220 words, one paragraph. What it was, how it worked, a small human detail, a nuance with "
            "'Yet' or 'That does not mean', and a quiet closing thought. Short sentences.\n"
            "- slug: 3-5 lowercase words joined by hyphens, describing the picture.\n"
            "- image: one sentence describing a calm, realistic picture of this moment (who, where, what light). Describe "
            "only what is there; never write what is absent.\n"
            f"Do not start the head like these earlier heads: {eerdere_koppen[-6:]}\n"
            'JSON: {"slug": "...", "image": "...", "head": "...", "body": "..."}',
            SYSTEEM, temp=0.75 if poging < 2 else 0.6, max_tokens=900)
        body = " ".join(str(r.get("body", "")).split())
        if 150 <= woorden(body) <= 240 and r.get("head") and r.get("slug") and r.get("image") and zinnen_ok(body):
            return {k: " ".join(str(r[k]).split()) for k in ("slug", "image", "head")} | {"body": body}
    return None


def feitencheck(blok, bron):
    """Laat het model zinnen zoeken die niet in de bron staan; die worden herschreven of geschrapt."""
    r = llm.json_vraag(
        f"Source text:\n{bron}\n\nScript paragraph:\n{blok['head']} {blok['body']}\n\n"
        "Which sentences in the script paragraph state a fact (name, number, date, event, claim) that is NOT supported "
        "by the source text? Calm general sentences without facts are fine.\n"
        'JSON: {"unsupported": ["exact sentence", ...]}', SYSTEEM, temp=0.1, max_tokens=800)
    fout = [s for s in r.get("unsupported", []) if isinstance(s, str) and s.strip()]
    if not fout:
        return blok
    nieuw = llm.json_vraag(
        f"Source text:\n{bron}\n\nParagraph:\n{blok['body']}\n\nThese sentences are not supported by the source: {fout}\n"
        "Rewrite the paragraph without those claims, keeping the same calm style and 160-220 words. Use only the source.\n"
        'JSON: {"head": "...", "body": "..."}', SYSTEEM, temp=0.4, max_tokens=900)
    body = " ".join(str(nieuw.get("body", "")).split())
    if 150 <= woorden(body) <= 240:
        blok["body"] = body
        if nieuw.get("head"):
            blok["head"] = " ".join(str(nieuw["head"]).split())
    return blok


def vermijden():
    """Zinnen uit begin/slot/bridges van alle bestaande video's: niet nog eens zo zeggen."""
    uit = []
    for m in STORIES.iterdir():
        for s in ("src-feiten", "src"):
            for n in ("begin.txt", "slot.txt"):
                p = m / s / n
                if p.exists():
                    uit += [z for z in re.split(r"(?<=[.!?])\s+", " ".join(p.read_text(encoding="utf-8").split())) if woorden(z) >= 6]
    return uit


def schrijf_begin(onderwerp, vraag_titel, opening, feiten_tekst, extra=""):
    return llm.vraag(
        f"Video topic: {onderwerp}. The big question of the video: {vraag_titel}\nSome facts from the video:\n{feiten_tekst}\n\n"
        "Write the opening of the video, about 250-300 words, in 5 short paragraphs separated by a blank line:\n"
        f"1. Start straight away with {OPENING_EN[opening]}. Never start with 'Tonight' or 'Hello' or 'Welcome'.\n"
        "2. The big question of the video, calmly, and one sentence about where we are going.\n"
        "3. A gentle invitation to subscribe, without any pressure, in your own new words.\n"
        "4. A question for the comments: where the listener is and what time it is there, in your own new words.\n"
        "5. Settle in: two or three short sentences to slow down and get comfortable.\n"
        f"Do NOT reuse or closely copy any of these sentences from earlier videos: {random.sample(vermijden(), min(25, len(vermijden())))}\n"
        f"{extra}\nOnly the text, no titles.", SYSTEEM, temp=0.85, max_tokens=900)


def schrijf_slot(onderwerp, slotbeeld, extra=""):
    return llm.vraag(
        f"Video topic: {onderwerp}. A calm closing picture to use: {slotbeeld}\n\n"
        "Write the ending of the video, 120-160 words, in 4-5 short paragraphs separated by a blank line:\n"
        "1. One sentence that our visit comes to an end.\n2. Let the closing picture slowly fade into night, short sentences.\n"
        "3. One sentence that contains the words 'another', 'story' and 'on the screen' (in that order), "
        "and one short gentle line about subscribing.\n4. One or two very short sentences to let go of the day.\n"
        "5. The very last line, exactly: Sleep well, and good night.\n"
        f"Do NOT reuse or closely copy any of these sentences: {random.sample(vermijden(), min(25, len(vermijden())))}\n"
        f"{extra}\nOnly the text.", SYSTEEM, temp=0.85, max_tokens=600)


def schrijf_bridge(vorige_titel, laatste_kop, nieuwe_titel, eerste_kop):
    return " ".join(llm.vraag(
        f"The previous chapter '{vorige_titel}' ended with: {laatste_kop}\nThe next chapter is '{nieuwe_titel}' and starts "
        f"with: {eerste_kop}\nWrite 1 or 2 short calm sentences that gently close the previous chapter and open the next. "
        "No names of chapters, no 'In this chapter'. Only the sentences.", SYSTEEM, temp=0.8, max_tokens=120).split())


# ---------- 3. alles samen ----------
def maak(m, test=False):
    p = lees_planning(m)
    onderwerp = p["onderwerp"] or m.name
    vorige = vorige_video(m, p["datum"])
    opening = random.choice([o for o in OPENINGEN if o != vorige["opening"]])
    titelsoort = random.choice([t for t in TITELSOORTEN if t != vorige["titelsoort"]])
    log(f"{m.name}: start ({onderwerp}; opening {opening}, titel {titelsoort})")

    oud = oud_script(m)                                     # ombouwen: alleen het oude script (geen vrij zoeken meer)
    teksten = bronnen.verzamel(m, onderwerp, llm, oud)
    stukjes = bronnen.stukken(teksten)
    if not oud:
        stukjes = bronnen.relevant(stukjes, onderwerp, llm)
    log(f"{m.name}: {len(teksten)} bronnen ({'oude script' if oud else ', '.join(sorted({t.split(':')[0].split(' ')[0] for t in teksten}))}), "
        f"{len(stukjes)} bruikbare stukken")
    feiten = feiten_uit_bronnen(onderwerp, stukjes)
    feiten = youtube_dubbel(feiten, stukjes)
    plan = opzet(onderwerp, feiten, random.choice([9, 10, 11, 12]))
    log(f"{m.name}: {len(feiten)} feiten gevonden, {len(plan)} onderwerpen")

    vraag_titel = ""
    for _ in range(5):
        vraag_titel = llm.vraag(f"Video topic: {onderwerp}. Write one YouTube title as a question in the form "
                                f"'{TITELSOORTEN[titelsoort]}', 45-65 characters, with the famous name or place in it, "
                                "no numbers of hours. Only the title, without quotes.", SYSTEEM, temp=0.7, max_tokens=40)
        vraag_titel = vraag_titel.strip().strip('"').split("|")[0].strip()
        if vraag_titel.endswith("?") and 30 <= len(vraag_titel) <= 70 and "hour" not in vraag_titel.lower():
            break

    sf = m / "src-feiten"
    sf.mkdir(exist_ok=True)
    stuk_tekst = {s["id"]: s["tekst"] for s in stukjes}
    blokken, koppen, slugs = [], [], set()
    for hi, h in enumerate(plan):
        hoofd = []
        for fid in h["facts"]:
            f = feiten[fid]
            b = schrijf_feitje(onderwerp, f["fact"], stuk_tekst[f["stuk"]], koppen)
            if not b:
                continue
            b = feitencheck(b, stuk_tekst[f["stuk"]])
            b["fact"] = f["fact"]
            slug = re.sub(r"[^a-z0-9-]", "", b["slug"].lower().replace(" ", "-"))[:50] or f"beeld-{fid}"
            while slug in slugs:
                slug += "-2"
            slugs.add(slug)
            b["slug"] = slug
            koppen.append(b["head"][:40])
            hoofd.append(b)
            print(f"  feitje {sum(len(x[1]) for x in blokken) + len(hoofd)}: {b['head'][:70]}", flush=True)
        if hoofd:
            blokken.append((h["title"], hoofd))
    n = sum(len(x[1]) for x in blokken)
    if n < 80:
        log(f"{m.name}: MISLUKT, maar {n} goede feitjes (minstens 80 nodig); niets gepusht")
        return False

    def schrijf_delen():
        for f in sf.glob("deel*.txt"):
            f.unlink()
        per_deel = -(-len(blokken) // 3)
        for d in range(3):
            uit = []
            for ti, (titel, hoofd) in enumerate(blokken[d * per_deel:(d + 1) * per_deel]):
                k = d * per_deel + ti
                topic = f"TOPIC: {titel}"
                if k > 0:
                    vt, vh = blokken[k - 1]
                    topic += "\nBRIDGE: " + schrijf_bridge(vt, vh[-1]["head"], titel, hoofd[0]["head"])
                uit.append(topic)
                uit += [f"IMG: {b['slug']} | {b['image']}\nHEAD: {b['head']}\nBODY: {b['body']}" for b in hoofd]
            if uit:
                (sf / f"deel{d + 1}.txt").write_text("\n===\n".join(uit) + "\n", encoding="utf-8")

    def schrijf_begin_slot(fout_zinnen=None):
        feiten_tekst = "\n".join(b["head"] for _, h in blokken[:3] for b in h[:2])
        slotbeeld = blokken[-1][1][-1]["image"]
        extra = f"Earlier attempt had problems; fix them and make every sentence clearly different: {fout_zinnen}" if fout_zinnen else ""
        for _ in range(4):
            begin = schrijf_begin(onderwerp, vraag_titel, opening, feiten_tekst, extra).strip()
            if 200 <= woorden(begin) <= 340 and re.search(r"subscri", begin, re.I) and not re.match(r"\s*(tonight|hello|welcome)", begin, re.I):
                break
            extra += " The opening must be 250-300 words in 5 paragraphs and invite to subscribe."
        (sf / "begin.txt").write_text(begin + "\n", encoding="utf-8")
        for _ in range(4):
            slot = schrijf_slot(onderwerp, slotbeeld, extra).strip()
            if not slot.endswith("Sleep well, and good night."):
                slot = slot.rstrip() + "\n\nSleep well, and good night."
            if 90 <= woorden(slot) <= 200 and re.search(r"another .*(story|video).*screen", slot, re.I | re.S):
                break
        (sf / "slot.txt").write_text(slot + "\n", encoding="utf-8")

    gebruikt = {b.get("fact") for _, h in blokken for b in h}
    reserve = [f for f in feiten if f["fact"] not in gebruikt]

    def extra_feitje():
        while reserve:
            f = reserve.pop(0)
            b = schrijf_feitje(onderwerp, f["fact"], stuk_tekst[f["stuk"]], koppen)
            if b:
                b = feitencheck(b, stuk_tekst[f["stuk"]])
                b["fact"] = f["fact"]
                b["slug"] = (re.sub(r"[^a-z0-9-]", "", b["slug"].lower().replace(" ", "-"))[:46] or "beeld") + f"-{len(slugs)}"
                slugs.add(b["slug"])
                return b
        return None

    stijl = llm.vraag(f"Video topic: {onderwerp}. Write ONE sentence (40-70 words) that describes the visual world of "
                      "this time and place for an image generator: era, place, building materials, clothing, landscape, "
                      "light. Describe only what is there; never use the word 'no'. Only the sentence.", SYSTEEM,
                      temp=0.4, max_tokens=150)
    stijl = " ".join(stijl.split()).rstrip(".") + (". Cinematic realistic photograph, wide 16:9 landscape, soft natural "
                                                   "light, gentle atmospheric haze, calm and peaceful mood, highly detailed, "
                                                   "no text, no letters, no logos")
    (sf / "stijl.txt").write_text(stijl + "\n", encoding="utf-8")
    shutil.copy(STORIES / "egypte-toetanchamon" / "bouw_script.py", m / "bouw_script.py")
    shutil.copy(HIER / "maak_motion_basis.py", m / "maak_motion.py")

    # kopieercontrole: niets letterlijk uit YouTube-transcripties
    yt_teksten = [t for k, t in teksten.items() if k.startswith("YouTube")]
    if yt_teksten:
        for _, hoofd in blokken:
            for b in hoofd:
                if bronnen.kopieer_overlap(b["head"] + " " + b["body"], yt_teksten):
                    r = llm.json_vraag(f"Rewrite this paragraph completely in your own words, same facts, same calm style, "
                                       f"160-220 words:\n{b['body']}\n" + 'JSON: {"body": "..."}', SYSTEEM, temp=0.8, max_tokens=900)
                    if isinstance(r, dict) and 150 <= woorden(str(r.get("body", ""))) <= 240:
                        b["body"] = " ".join(str(r["body"]).split())

    # herstellus met de scriptcontrole (tools/script_check.py), max 3 rondes
    sys.path.insert(0, str(REPO / "tools"))
    import script_check
    schrijf_delen()
    schrijf_begin_slot()
    for ronde in range(1, 4):
        bouw = subprocess.run([sys.executable, str(m / "bouw_script.py")], capture_output=True, text=True, encoding="utf-8")
        fout, info = script_check.controleer(m)
        log(f"{m.name}: scriptcontrole ronde {ronde}: {'GOED' if not fout else str(len(fout)) + ' punten'}")
        if not fout:
            break
        plat = [(ti, b) for ti, (_, h) in enumerate(blokken) for b in h]
        weg, begin_slot = set(), False
        for f in fout:
            mm = re.match(r"feitje (\d+)( \(beeld\))?", f)
            if mm and "niet over het onderwerp" in f:
                weg.add(int(mm.group(1)))
            elif mm and mm.group(2):                         # beeld met iets wat er toen niet was: positief herschrijven
                _, b = plat[int(mm.group(1)) - 1]
                b["image"] = " ".join(llm.vraag(f"Describe this calm picture again in one sentence, only things that existed in "
                                                f"the time of {onderwerp}; never use 'no' or 'without': {b['image']}",
                                                temp=0.4, max_tokens=80).split())
            elif mm:                                         # woord in de tekst dat volgens het model fout is
                weg.add(int(mm.group(1)))
            hm = re.match(r"hoofdstuk '(.+)' gaat niet", f)
            if hm:
                weg |= {i + 1 for i, (ti, b) in enumerate(plat) if blokken[ti][0] == hm.group(1)}
            if f.startswith(("begin", "slot", "geen abonneer", "afwisseling")):
                begin_slot = True
        for n in sorted(weg, reverse=True):                  # foute feitjes eruit, zo mogelijk vervangen
            ti, b = plat[n - 1]
            idx = blokken[ti][1].index(b)
            nieuw = extra_feitje()
            if nieuw:
                blokken[ti][1][idx] = nieuw
            else:
                blokken[ti][1].pop(idx)
        blokken[:] = [(t, h) for t, h in blokken if h]
        while sum(len(h) for _, h in blokken) < 82 and reserve:
            nieuw = extra_feitje()
            if nieuw:
                blokken[-1][1].append(nieuw)
        schrijf_delen()
        if begin_slot:
            schrijf_begin_slot([f for f in fout if f.startswith(("begin", "slot", "afwisseling", "geen"))])
    else:
        bouw = subprocess.run([sys.executable, str(m / "bouw_script.py")], capture_output=True, text=True, encoding="utf-8")
        fout, info = script_check.controleer(m)
        if fout:
            log(f"{m.name}: MISLUKT, scriptcontrole na 3 herstelrondes nog {len(fout)} punten: {fout[:3]}; niets gepusht")
            return False
    n = sum(len(h) for _, h in blokken)
    w = info.get("woorden", 0)
    print(bouw.stdout, bouw.stderr)
    lees = subprocess.run([sys.executable, str(REPO / "tools" / "script_leesbaar.py"), str(m)], capture_output=True,
                          text=True, encoding="utf-8").stdout
    if "GOED" not in lees:
        log(f"{m.name}: MISLUKT, leesbaarheid: {lees.strip()[-60:]}; niets gepusht")
        return False

    intro = llm.vraag(f"Video: {vraag_titel}\nChapters: {[t for t, _ in blokken]}\nWrite two short YouTube description "
                      "paragraphs (first 2 sentences, then 2-3 sentences) that invite people to drift off to this calm "
                      "history for sleep. Mention the main place and time. No hashtags, no emojis.", SYSTEEM, temp=0.6,
                      max_tokens=300)
    tags3 = llm.json_vraag(f"Give 3 short lowercase hashtags (without #, no spaces) for a sleep history video about "
                           f"{onderwerp}.\n" + 'JSON: ["...", "...", "..."]', SYSTEEM, temp=0.3)
    hashtags = ["sleepdocumentary", "historyforsleep", "sleepstory", "432hz", "boringhistory", "bedtimestory",
                "fallasleep", "relaxinghistory", "sleepsounds", "sleepmusic", "calmhistory", "historydocumentary"] + \
               [re.sub(r"[^a-z0-9]", "", str(t).lower()) for t in tags3][:3]
    (m / "youtube-beschrijving.txt").write_text(
        intro.strip() + "\n\nA calm, slow-paced history documentary for sleep and relaxation. No loud\nsounds, no jump "
        "scares, just a gentle voice, deep and warm 432 Hz music in\nthe background and softly changing images.\n\n"
        "Chapters\n" + "".join(f"0:00:00 {t}\n" for t, _ in blokken) + "\n" + " ".join("#" + h for h in hashtags) + "\n",
        encoding="utf-8")

    plan_t = p["tekst"]
    status = f"status   script-klaar (nieuwe opbouw, {datetime.date.today()}, scriptgenerator lokaal {llm.MODEL})"
    plan_t = re.sub(r"^status .*$", status, plan_t, flags=re.M) if re.search(r"^status", plan_t, re.M) else plan_t + status + "\n"
    plan_t = re.sub(r"^titel .*$", f"titel    {vraag_titel} | History for Sleep", plan_t, flags=re.M)
    plan_t = re.sub(r"^(opening|titelsoort) .*\n?", "", plan_t, flags=re.M).rstrip() + f"\nopening   {opening}\ntitelsoort {titelsoort}\n"
    (m / "planning.txt").write_text(plan_t, encoding="utf-8")
    log(f"{m.name}: KLAAR, {n} feitjes, {len(blokken)} onderwerpen, {w} woorden, titel '{vraag_titel}'")

    if not test:
        subprocess.run(["git", "add", str(m.relative_to(REPO)), "stories/ROUTINE-LOG.md"], cwd=REPO)
        subprocess.run(["git", "commit", "-q", "-m", f"{m.name}: omgebouwd naar de nieuwe opbouw (scriptgenerator lokaal)"], cwd=REPO)
        subprocess.run(["git", "pull", "-q", "--rebase", "--autostash"], cwd=REPO)
        subprocess.run(["git", "push", "-q", "origin", "main"], cwd=REPO)
    return True


MAANDEN = {"jan": 1, "feb": 2, "mrt": 3, "apr": 4, "mei": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}
SOORTEN = ["ramp", "oudheid", "middeleeuwen", "mysterie", "oorlog", "verlaten", "reis"]


def kies_nieuw():
    """Eerstvolgende datum uit de "Nieuwe planning" in ONDERWERPEN.md zonder map (niet "vrij"); maakt de map met planning."""
    tekst = (STORIES / "ONDERWERPEN.md").read_text(encoding="utf-8")
    deel = tekst.split("Nieuwe planning", 1)[1] if "Nieuwe planning" in tekst else tekst
    grens = datetime.date.today() + datetime.timedelta(days=2)
    jaar, vorige_maand = 2026, 0
    for regel in deel.splitlines():
        r = re.match(r"^- (ma|wo|za) (\d{1,2}) ([a-z]{3})\w*:\s*(.+)$", regel.strip())
        if not r:
            continue
        maand = MAANDEN.get(r[3])
        if not maand:
            continue
        if maand < vorige_maand:
            jaar += 1
        vorige_maand = maand
        datum = datetime.date(jaar, maand, int(r[2]))
        rest = r[4]
        if datum < grens or rest.lower().startswith("vrij") or "routine kiest" in rest:
            continue
        mapnaam = (re.search(r"map ([a-z0-9-]+)", rest) or [None, None])[1]
        onderwerp = re.split(r"\s+\(|\s+–\s+map", rest)[0].strip()
        if not mapnaam:
            mapnaam = re.sub(r"[^a-z0-9]+", "-", onderwerp.lower()).strip("-")[:40]
        m = STORIES / mapnaam
        if m.exists():
            continue
        m.mkdir()
        soort = llm.vraag(f"Topic: {onderwerp}. Choose the best playlist kind from {SOORTEN}. Answer with one word.",
                          temp=0.1, max_tokens=10).strip().lower()
        soort = soort if soort in SOORTEN else "mysterie"
        thumb = llm.vraag(f"Topic: {onderwerp}. Describe in one Dutch sentence the single most recognisable calm image "
                          "for a YouTube thumbnail (big subject on the right, evening light, no text).", temp=0.5, max_tokens=80)
        (m / "planning.txt").write_text(
            f"onderwerp {onderwerp}\nstatus   in-wording (scriptgenerator lokaal; de routine slaat dit over)\n"
            f"datum    {r[1]} {datum.isoformat()} 21:00 NL\ntitel    (volgt)\n"
            f"thumbnail amberregel \"{onderwerp.split(',')[0].upper()[:28]}\", beeld: {' '.join(thumb.split())}\n"
            f"soort    {soort}\n", encoding="utf-8")
        log(f"{mapnaam}: nieuw script voor {datum} ({onderwerp})")
        return m
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", type=Path)
    ap.add_argument("--test", action="store_true", help="niet committen of pushen")
    a = ap.parse_args()
    m = a.map.resolve() if a.map else (kies_map() or kies_nieuw())
    if not m:
        log("niets te doen: alles omgebouwd en geen open datum in de Nieuwe planning")
        sys.exit(0)
    sys.exit(0 if maak(m, a.test) else 1)
