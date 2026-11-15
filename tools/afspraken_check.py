"""Controle vóór elke nieuwe video: houdt de video zich aan alle vaste afspraken van de eigenaar? (eigenaar 14 nov 2026:
"zorg dat als je video's maakt straks dit niet vergeet, alles volgens wat we afgesproken hebben"). Zie stories/AFSPRAKEN.md.

  python tools/afspraken_check.py stories/<map>      -> AFSPRAKEN GOED / AFSPRAKEN FOUT (met de punten)

tools/routine_lokaal.py roept dit aan voordat er beelden, stem of montage gemaakt worden; bij FOUT stopt de keten.
"""
import json, re, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
sys.path.insert(0, str(HIER))


def controleer(m):
    m = Path(m)
    fout = []
    plan = (m / "planning.txt").read_text(encoding="utf-8", errors="replace") if (m / "planning.txt").exists() else ""

    # 1. geluid: vaste stem + achtergrond (open haard + B-effect) uit audio_engine/B1.json
    b1 = json.loads((REPO / "audio_engine" / "B1.json").read_text(encoding="utf-8"))
    ag = b1.get("achtergrond")
    if not ag:
        fout.append("B1.json heeft geen 'achtergrond' (open haard + B-effect)")
    else:
        for l in ag["lagen"]:
            if not (Path(ag["map"]).expanduser() / l["bestand"]).exists():
                fout.append(f"achtergrondgeluid ontbreekt: {Path(ag['map']).expanduser() / l['bestand']}")
    st = m / "stem.json"
    if st.exists() and "eigenaar_afwijking" not in st.read_text(encoding="utf-8"):
        fout.append("stories/<map>/stem.json wijkt af van B1 zonder 'eigenaar_afwijking'")

    # 2. titel: concreet, plaats/jaar, geen vraag, met '| History for Sleep'
    t = re.search(r"^titel\s+(.+?)\s*\|\s*History for Sleep", plan, re.M)
    if not t:
        fout.append("titel mist of eindigt niet op '| History for Sleep'")
    else:
        titel = t.group(1)
        if "?" in titel:
            fout.append(f"titel is een vraag: '{titel}' (afspraak: concreet, plaats/jaar)")
        if re.search(r"<N>|hours?\b", titel, re.I):
            fout.append(f"titel met uren of <N>: '{titel}'")

    # 3. script: opbouw Sleepy, abonneerzin pas na feitje 2
    sf = m / "src-feiten"
    if not (sf / "begin.txt").exists():
        fout.append("geen src-feiten/begin.txt (nog oude opbouw)")
    else:
        if re.search(r"subscri", (sf / "begin.txt").read_text(encoding="utf-8"), re.I):
            fout.append("abonneerzin staat in begin.txt (afspraak: in abonneer.txt, klinkt na feitje 2)")
        if not (sf / "abonneer.txt").exists():
            fout.append("geen src-feiten/abonneer.txt")
        else:                                               # 15 nov: per video anders verwoord, wel even lang (± 18 woorden)
            n = len((sf / "abonneer.txt").read_text(encoding="utf-8").split())
            if not 15 <= n <= 22:
                fout.append(f"abonneerzin {n} woorden (afspraak: 15-22, ongeveer even lang als bij Gettysburg)")
        import script_leesbaar
        tn = script_leesbaar.toon(m)
        if not tn or tn.get("toon") != "TOON GOED":
            fout.append(f"toon niet goed ({tn.get('toon') if tn else '?'})")

    # 4. thumbnail: kenmerkend beeld + mensen van toen (gekozen bestand, of een kenmerk-regel voor de maker)
    if not (m / "thumbnail-v3.jpg").exists() and not re.search(r"^thumbnail kenmerk:", plan, re.M):
        fout.append("geen thumbnail-v3.jpg en geen regel 'thumbnail kenmerk:' in planning.txt")
    return fout


if __name__ == "__main__":
    f = controleer(sys.argv[1])
    for x in f:
        print(" -", x)
    print("AFSPRAKEN FOUT" if f else "AFSPRAKEN GOED")
    sys.exit(1 if f else 0)
