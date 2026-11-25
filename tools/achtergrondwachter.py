"""Achtergrondwachter (eigenaar 25 nov 2026, winkel-achtergrond van de $1 Million-Short: cerealdozen met "Milk" erop -> "dit klopt
niet ... zorg dan dat je een pak melk ziet; als je pizza hebt zie je een pizzadoos, dat verschil moet je laten controleren").
Tekst op spullen MAG, maar moet passen bij het voorwerp waar hij op staat: "MILK" alleen op een melkpak, "PIZZA" op een pizzadoos.

Hoe (alles gratis op de pc):
  1. OCR (rapidocr-onnxruntime) vindt elk woord met zijn plek.
  2. Het woord wordt weggepoetst en het voorwerp eromheen wordt uitgeknipt; het beeldmodel (Ollama qwen2.5vl:7b) zegt wat het
     voorwerp is, ZONDER het woord te zien (anders gelooft het model gewoon de tekst - zo werd "Milk" op cerealdozen goedgekeurd).
  3. Het tekstmodel (qwen3:14b) beslist of het woord bij dat voorwerp past. Onleesbare nep-letters zijn ook fout.
Fout = achtergrond opnieuw maken (of de tekst wegschilderen).

  python tools/achtergrondwachter.py <map-met-png's> [naam ...]
Uitvoer: ACHTERGRONDWACHTER.md in de bovenliggende map en <map>/../achtergrondwachter/ (uitsneden). Exit 1 bij een fout.
"""
import base64, io, json, re, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw
from rapidocr_onnxruntime import RapidOCR

OLLAMA = "http://127.0.0.1:11434/api/chat"; OCR = RapidOCR()
WAT = """This is a cut-out from a cartoon picture. Judging ONLY by its shape, colors and the picture on it, what kind of object or
product package is in the middle? (e.g. "milk carton", "cereal box", "jam jar", "pizza box", "shop sign"). JSON: {"voorwerp": "..."}"""
PAST = """Words are printed on objects in a cartoon picture. For each numbered line you get the word and the object it is printed on
(the object was judged by its shape and picture only). Does the word make sense on that object (it names the product or is a normal
sign/label text for it)? "Milk" on a milk carton = yes; "Milk" on a cereal box = no; random letters = no.
{lijst}
JSON: {{"uitslag": [{{"nr": 1, "klopt": true or false, "waarom": "short"}}, ...]}}"""
def ollama(prompt, img=None, model="qwen2.5vl:7b"):
    msg = {"role": "user", "content": prompt}
    if img is not None:
        buf = io.BytesIO(); img.convert("RGB").save(buf, "JPEG", quality=90); msg["images"] = [base64.b64encode(buf.getvalue()).decode()]
    body = {"model": model, "stream": False, "format": "json", "think": False, "options": {"temperature": 0}, "messages": [msg]}
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try: return json.loads(json.load(urllib.request.urlopen(req, timeout=300))["message"]["content"])
    except (ValueError, KeyError): return {}

def controleer(pad, uitmap):
    im = Image.open(pad).convert("RGB"); W, H = im.size; fouten = []; gevonden = []
    res, _ = OCR(str(pad))
    for k, (box, woord, zeker) in enumerate(res or []):
        if zeker < 0.6: continue
        xs = [p[0] for p in box]; ys = [p[1] for p in box]; x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); w, h = x1 - x0, y1 - y0
        if not re.search(r"[A-Za-z]{2,}", woord): continue                  # losse cijfers/streepjes: geen woord
        stuk = im.copy(); d = ImageDraw.Draw(stuk)
        rand = [im.getpixel((min(W - 1, max(0, int(x))), min(H - 1, max(0, int(y))))) for x, y in ((x0 - 3, y0 - 3), (x1 + 3, y0 - 3), (x0 - 3, y1 + 3), (x1 + 3, y1 + 3))]
        kl = tuple(sorted(c[i] for c in rand)[len(rand) // 2] for i in range(3))
        d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill=kl)            # woord weg: het model moet het voorwerp zelf herkennen
        c = stuk.crop((max(0, int(x0 - w * 0.8)), max(0, int(y0 - h * 1.5)), min(W, int(x1 + w * 0.8)), min(H, int(y1 + h * 4.5))))
        c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS); c.save(uitmap / f"{pad.stem}-{k:02d}.jpg", quality=88)
        gevonden.append((woord, str(ollama(WAT, c).get("voorwerp", "?")), f"{pad.stem}-{k:02d}.jpg"))
    if gevonden:                                          # alles in één keer beoordelen (geen modelwissel per woord: pc heeft weinig geheugen)
        lijst = chr(10).join(f'{i + 1}. word "{w}" on: {v}' for i, (w, v, _) in enumerate(gevonden))
        uit = {u.get("nr"): u for u in ollama(PAST.format(lijst=lijst), model="qwen3:14b").get("uitslag", []) if isinstance(u, dict)}
        for i, (w, v, f) in enumerate(gevonden):
            u = uit.get(i + 1, {}); print(f"  {w!r} op {v!r} -> {'klopt' if u.get('klopt') else 'FOUT'} ({u.get('waarom', '')})", flush=True)
            if not u.get("klopt", False): fouten.append(f'"{w}" op {v} ({f})')
    return fouten

if __name__ == "__main__":
    map_ = Path(sys.argv[1]); namen = sys.argv[2:]
    uitmap = map_.parent / "achtergrondwachter"; uitmap.mkdir(exist_ok=True)
    for f in uitmap.glob("*.jpg"):
        if not namen or any(f.name.startswith(n + "-") for n in namen): f.unlink()
    pngs = [p for p in sorted(map_.glob("*.png")) if (not namen or p.stem in namen)]
    regels = ["# Achtergrondwachter", "", "Tekst mag alleen als hij bij het voorwerp past (MILK op een melkpak, PIZZA op een pizzadoos); nep-letters zijn fout.", ""]
    fout = 0
    for p in pngs:
        im = Image.open(p)
        if min(im.size) < 700: continue                  # losse voorwerpen (sprites) overslaan: alleen achtergronden
        print(p.name, flush=True); t = controleer(p, uitmap)
        regels.append(f"- **{'FOUT' if t else 'goed'}** {p.name}: {'; '.join(t) if t else 'tekst klopt (of geen tekst)'}"); fout += bool(t)
    regels.insert(3, f"**{fout} achtergronden met tekst die niet klopt.**\n")
    (map_.parent / "ACHTERGRONDWACHTER.md").write_text("\n".join(regels) + "\n", encoding="utf-8")
    print("ACHTERGRONDWACHTER:", fout, "met tekst die niet klopt"); sys.exit(1 if fout else 0)
