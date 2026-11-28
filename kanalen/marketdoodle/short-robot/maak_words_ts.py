"""words.ts voor de 3D-robotshort: Whisper-tijden (woorden.json) met de woorden uit het script (zinnen.json), zodat de
ondertitels precies het script tonen ("ten thousand" i.p.v. "10 ,000") en story.ts de kernwoorden vindt."""
import json
from pathlib import Path
H = Path(__file__).parent
W = json.load(open(H / "woorden.json", encoding="utf-8")); Z = json.load(open(H / "zinnen.json", encoding="utf-8"))
uit = []
for i, z in enumerate(Z):
    tok = [w for w in W if w[0] == i]; sw = z[2].split()
    if len(tok) == len(sw): uit += [[s, w[2], w[3], i] for s, w in zip(sw, tok)]
    else: print("zin", i, "telt anders:", len(sw), len(tok), [w[1] for w in tok]); uit += [[w[1], w[2], w[3], i] for w in tok]
s = "// woordtijden uit short-robot/woorden.json met de scriptwoorden (maak_words_ts.py): [woord, start, eind, zin]; zinnen: [start, eind, tekst, plek, spreker]\n"
s += "export const WORDS: [string, number, number, number][] = " + json.dumps(uit, ensure_ascii=False) + ";\n"
s += "export const ZINNEN: [number, number, string, string, string][] = " + json.dumps(Z, ensure_ascii=False) + ";\n"
(H.parent / "studio3d/cartoon3d/src/videos/robot/words.ts").write_text(s, encoding="utf-8")
print("woorden", len(uit))
