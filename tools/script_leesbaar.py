"""Is een script makkelijk te volgen bij het inslapen? (eigenaar 10 nov 2026: "makkelijk Engels zodat het makkelijk te
begrijpen is en fijn om naar te luisteren als je wilt slapen")

Meet per script:
  - woorden per zin en komma's per zin (zoals voorheen; GOED = hooguit 20 woorden en 3 komma's per zin)
  - Flesch Reading Ease (0-100, hoger = makkelijker; 70+ = makkelijk Engels, 60-70 = gewoon, onder 60 = moeilijk)
  - schoolniveau (Flesch-Kincaid: aantal jaren school om het te volgen; 7 of lager = makkelijk)
  - lange zinnen (meer dan 25 woorden) en moeilijke woorden (3+ lettergrepen) in procenten
Oordeel: MAKKELIJK (Flesch >= 70 en niveau <= 7), GOED (Flesch >= 60, oude regel GOED), anders TE MOEILIJK.

Gebruik: python tools/script_leesbaar.py stories/<map> [stories/<map> ...] [--json]
"""
import json, re, sys
from pathlib import Path


def lettergrepen(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def meet(d):
    f = d / "script-cues.txt"
    t = f.read_text(encoding="utf-8") if f.exists() else "\n".join(x.read_text(encoding="utf-8") for x in sorted((d / "src").glob("[0-9]*.txt")))
    t = re.sub(r"\{[^}]*\}|\[[^\]]*\]", "", t)
    t = "\n".join(r for r in t.splitlines() if not re.match(r"\s*(IMG|TOPIC|#)", r))
    zinnen = [z for z in re.split(r"(?<=[.!?])\s+", t) if z.strip() and re.search(r"[A-Za-z]", z)]
    woorden = re.findall(r"[A-Za-z][A-Za-z'’-]*", t)
    if not zinnen or not woorden:
        return None
    lg = [lettergrepen(w) for w in woorden]
    wpz, spw = len(woorden) / len(zinnen), sum(lg) / len(woorden)
    flesch = 206.835 - 1.015 * wpz - 84.6 * spw
    niveau = 0.39 * wpz + 11.8 * spw - 15.59
    lang = sum(1 for z in zinnen if len(z.split()) > 25) / len(zinnen) * 100
    moeilijk = sum(1 for x in lg if x >= 3) / len(woorden) * 100
    k = t.count(",") / len(zinnen)
    oud_goed = wpz <= 20 and k <= 3.0
    oordeel = "MAKKELIJK" if flesch >= 70 and niveau <= 7 and oud_goed else "GOED" if flesch >= 60 and oud_goed else "TE MOEILIJK"
    return {"map": d.name, "woorden_per_zin": round(wpz, 1), "kommas_per_zin": round(k, 1), "flesch": round(flesch),
            "niveau": round(niveau, 1), "lange_zinnen_pct": round(lang, 1), "moeilijke_woorden_pct": round(moeilijk, 1),
            "oordeel": oordeel}


if __name__ == "__main__":
    uit = []
    for d in [Path(a) for a in sys.argv[1:] if not a.startswith("--")]:
        r = meet(d)
        if not r:
            continue
        uit.append(r)
        if "--json" not in sys.argv:
            # laatste woord GOED/MAKKELIJK blijft herkenbaar voor de generator en de routine
            print(f"{r['map']}: {r['woorden_per_zin']} woorden/zin, {r['kommas_per_zin']} komma's/zin, Flesch {r['flesch']}, "
                  f"niveau {r['niveau']}, lange zinnen {r['lange_zinnen_pct']}%, moeilijke woorden {r['moeilijke_woorden_pct']}% "
                  f"-> {r['oordeel']}" + (" (GOED)" if r["oordeel"] == "MAKKELIJK" else
                                          "" if r["oordeel"] == "GOED" else ", zinnen korter en eenvoudiger woorden"))
    if "--json" in sys.argv:
        print(json.dumps(uit, ensure_ascii=False))
