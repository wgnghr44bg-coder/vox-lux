"""Een bestaand script naar de nieuwe toon brengen (eigenaar 11 nov 2026), zonder feiten of beelden te veranderen.
Mechanisch: spreektaal (samentrekkingen). Met de hand per video (een JSON met aanpassingen):
  {"bridge": {"<TOPIC-titel>": "<nieuwe BRIDGE>"},
   "voor": {"<begin van een HEAD>": "<zin(nen) na de eerste zin van die BODY>"},
   "slot": {"<begin van een HEAD>": "<zin(nen) vóór de laatste zin van die BODY>"},
   "vervang": [["<oude tekst>", "<nieuwe tekst>"], ...]}
IMG- en TOPIC-regels blijven precies gelijk.
Gebruik: python tools/toon_bijwerken.py stories/<map> <aanpassingen.json>
"""
import json, re, sys
from pathlib import Path

SAMEN = [(r"\bdo not\b", "don't"), (r"\bDo not\b", "Don't"), (r"\bdoes not\b", "doesn't"), (r"\bdid not\b", "didn't"),
         (r"\bwas not\b", "wasn't"), (r"\bwere not\b", "weren't"), (r"\bis not\b", "isn't"), (r"\bare not\b", "aren't"),
         (r"\bcould not\b", "couldn't"), (r"\bwould not\b", "wouldn't"), (r"\bshould not\b", "shouldn't"),
         (r"\bhad not\b", "hadn't"), (r"\bhave not\b", "haven't"), (r"\bcannot\b", "can't"),
         (r"\bIt is\b", "It's"), (r"\bit is\b", "it's"), (r"\bThat is\b", "That's"), (r"\bthat is\b", "that's"),
         (r"\bThere is\b", "There's"), (r"\bthere is\b", "there's"), (r"\bWhat is\b", "What's"),
         (r"\byou would\b", "you'd"), (r"\bYou would\b", "You'd"), (r"\byou will\b", "you'll"), (r"\bYou will\b", "You'll"),
         (r"\byou are\b", "you're"), (r"\bYou are\b", "You're"), (r"\bthey would\b", "they'd"), (r"\bThey would\b", "They'd"),
         (r"\bwe will\b", "we'll"), (r"\bWe will\b", "We'll"), (r"\bwe are\b", "we're"), (r"\bWe are\b", "We're"),
         (r"\bLet us\b", "Let's"), (r"\blet us\b", "let's"), (r"\bhe would\b", "he'd"), (r"\bHe would\b", "He'd")]


def spreektaal(t):
    for a, b in SAMEN:
        t = re.sub(a, b, t)
    return t


def zinnen(t):
    return re.split(r"(?<=[.!?])\s+", t.strip())


m, aanp = Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
sf = m / "src-feiten"
gebruikt = set()
for p in sorted(sf.glob("deel*.txt")) + [sf / "begin.txt", sf / "slot.txt"]:
    regels = p.read_text(encoding="utf-8").splitlines()
    topic, kop = "", ""
    for i, r in enumerate(regels):
        if r.startswith("TOPIC:"):
            topic = r[6:].strip()
        elif r.startswith("BRIDGE:"):
            if topic in aanp.get("bridge", {}):
                regels[i] = "BRIDGE: " + aanp["bridge"][topic]
                gebruikt.add("bridge:" + topic)
            else:
                regels[i] = spreektaal(r)
        elif r.startswith("HEAD:"):
            kop = r[5:].strip()
            regels[i] = "HEAD: " + spreektaal(kop)
        elif r.startswith("BODY:"):
            z = zinnen(r[5:])
            for k, v in aanp.get("voor", {}).items():
                if kop.startswith(k):
                    z = z[:1] + zinnen(v) + z[1:]
                    gebruikt.add("voor:" + k)
            for k, v in aanp.get("slot", {}).items():
                if kop.startswith(k):
                    z = z[:-1] + zinnen(v) + z[-1:]
                    gebruikt.add("slot:" + k)
            regels[i] = "BODY: " + spreektaal(" ".join(z))
        elif not r.startswith(("IMG:", "===")) and r.strip() and p.name in ("begin.txt", "slot.txt"):
            regels[i] = spreektaal(r)
    t = "\n".join(regels) + "\n"
    for a, b in aanp.get("vervang", []):
        if a in t:
            t = t.replace(a, b)
            gebruikt.add("vervang:" + a[:30])
    p.write_text(t, encoding="utf-8")
alles = {f"{s}:{k}" for s in ("bridge", "voor", "slot") for k in aanp.get(s, {})} | {"vervang:" + a[:30] for a, _ in aanp.get("vervang", [])}
mist = sorted(alles - gebruikt)
print("niet gevonden:", mist if mist else "niets")
