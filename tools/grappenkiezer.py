"""Grappenkiezer (eigenaar 25 nov 2026: "je kan ook het paard naar de camera laten kijken met een vraagteken boven zijn hoofd als
hij de deurmat eet, zulke dingen moet je erbij doen en het moet vanzelf gaan, ook met uitdrukking van gezichten").

Het gratis taalmodel op de pc (Ollama qwen3:14b) leest het script en kiest per regel:
  - "gezicht": hoe de mensen in beeld kijken (blij / schrik / verdriet / verward / ongemakkelijk / neutraal),
  - "teken": een stripteken boven iemands hoofd op het grappige moment ("?", "!", "!?", "zweet" = zweetdruppel, "..." ),
    met "wie" (you/dad/mom/sis/paard/... of "allemaal") en het "woord" waarop het verschijnt,
  - "camera": true als het personage/dier (wie) even recht in de camera kijkt (droge grap, zoals in sitcoms).
Uitvoer: <map>/grappen.json  ->  de renderer gebruikt dit vanzelf (handmatige lijsten in de renderer gaan voor).
Het model is een EERSTE VOORSTEL: Claude loopt grappen.json altijd na (wie is echt in beeld? niet op elke regel een teken;
dieren die iets geks doen -> camera) en verbetert het. Eigenaar 25 nov: GEEN striptekens tonen (teken leeg laten), daarna pas renderen. Max. ongeveer 1 teken per 3 regels.

  python tools/grappenkiezer.py <map-met-script.txt>
"""
import json, sys, urllib.request
from pathlib import Path

VRAAG = """You direct a funny 2D cartoon (What If story, family: you, dad, mom, sis; animals may appear: horse = "paard").
For EACH numbered line below decide:
- "gezicht": the facial expression of the family members on screen at that moment: one of blij, schrik, verdriet, verward, ongemakkelijk, neutraal.
- "teken": a comic symbol above someone's head at the funniest moment, or "" if nothing fits: "?" (confused/absurd), "!" (shock),
  "!?" (shocked disbelief), "zweet" (awkward/embarrassed sweat drop), "..." (speechless). Use them for real comedic beats only,
  not on every line (about 1 in 3 lines).
- "wie": who gets the symbol (you, dad, mom, sis, paard, or allemaal).
- "woord": the exact word from the line where the symbol should pop up.
- "camera": true if "wie" should look straight into the camera for a dry joke (an animal doing something absurd, an awkward silence), else false.
Examples: "He eats the doormat." -> wie paard, teken "?", woord "doormat", camera true. "Fifty dollars? For milk?" -> wie mom,
teken "!?", woord "milk". "That's not even the worst part." (then silence) -> wie allemaal, teken "zweet", woord "part".
Good news ("You're rich") -> gezicht blij, no symbol. The symbol goes to the person/animal the line is ABOUT.
Lines:
{regels}
Answer ONLY JSON: {{"regels": [{{"nr": 0, "gezicht": "...", "teken": "...", "wie": "...", "woord": "...", "camera": false}}, ...]}}"""

def main():
    m = Path(sys.argv[1]); regels = []
    for r in (m / "script.txt").read_text(encoding="utf-8").splitlines():
        if r.strip() and not r.startswith("#") and not r.startswith("STILTE|"): regels.append(r.split("|", 2))
    lijst = "\n".join(f"{i}. [{sp}] {z}" for i, (sp, sc, z) in enumerate(regels))
    body = {"model": "qwen3:14b", "stream": False, "format": "json", "think": False, "options": {"temperature": 0.2},
            "messages": [{"role": "user", "content": VRAAG.format(regels=lijst)}]}
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"})
    uit = json.loads(json.load(urllib.request.urlopen(req, timeout=900))["message"]["content"]).get("regels", [])
    goed = {}
    for u in uit:
        if not isinstance(u, dict) or not isinstance(u.get("nr"), int) or not 0 <= u["nr"] < len(regels): continue
        z = regels[u["nr"]][2]
        if u.get("woord") and u["woord"].lower().strip(".,!?\"") not in z.lower(): u["woord"] = ""   # woord moet echt in de zin staan
        goed[u["nr"]] = {k: u.get(k) for k in ("gezicht", "teken", "wie", "woord", "camera")}
    (m / "grappen.json").write_text(json.dumps(goed, ensure_ascii=False, indent=1), encoding="utf-8")
    for i, g in sorted(goed.items()): print(i, regels[i][2][:50], "->", g)

if __name__ == "__main__":
    main()
