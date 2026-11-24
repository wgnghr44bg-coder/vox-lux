"""Beeldwachter (eigenaar 24 nov 2026: "er wordt soms iets gezegd zoals kijken op telefoon en dan gebeurt dat niet in beeld;
daar moet een wachter op komen die controleert dat er op beeld gedaan wordt wat er gezegd wordt").

Per vertellerzin uit zinnen.json (dialoog alleen met --alles) ([start, eind, tekst, scène, spreker]) pakt hij 3 beelden uit de video (begin, midden, eind van de zin),
zet ze naast elkaar en laat het gratis beeldmodel op de pc (Ollama, qwen2.5vl:7b) eerst opschrijven wat je moet ZIEN (max 3 concrete dingen) en
kijkt dan per ding of het in beeld is.
Uitslag: <map>/BEELDWACHTER.md (alleen de zinnen die NIET kloppen, met wat er mist) + beeldwachter.json + per fout een plaatje
in <map>/beeldwachter/. Kost niets. Eerst ComfyUI-geheugen vrijmaken (één zware taak tegelijk).

  python tools/beeldwachter.py <video.mp4> <zinnen.json> [--van 0 --tot 999]
"""
import argparse, base64, io, json, subprocess, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5vl:7b"          # kijkt naar de beelden
DENKER = "qwen3:14b"            # haalt uit de zin wat je moet zien (slimmer met taal)
LIJST = """A narrator describes a scene in an animated cartoon video. Sentence:
"{tekst}"

Which concrete things does THIS sentence say are happening or present right now, so a viewer should SEE them?
Rules:
- Use ONLY things literally written in the sentence. Never add objects or places that are not in the sentence.
- Only physical objects, places and visible actions of characters (for example: "a character looks at a phone", "a horse eats flowers").
- Skip negations and absent things ("nobody else does", "not even the teacher", "not the bus driver").
- Skip things a drawing cannot show or that are only talk: money in an account, being rich, wanting, caring, knowing, ordering/buying (unless the object itself is there), time of day, days, feelings, thoughts, sounds, prices, features you cannot see.
- At most 3 items, each one short sentence. Empty list if nothing concrete.
Answer ONLY with JSON: {{"zien": ["...", "..."]}}"""

CHECK = """Three frames of an animated cartoon video are shown left to right (start, middle, end of one sentence). Ignore the
subtitles at the bottom and name tags. Check each statement: is it clearly visible in at least one of the frames?
{lijst}
Answer ONLY with JSON: {{"uitslag": [{{"nr": 1, "zichtbaar": true or false, "zie": "what you actually see instead, short"}}, ...]}}"""

def beeld(video, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t):.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=640:-1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")

def ollama(prompt, img=None, model=MODEL):
    msg = {"role": "user", "content": prompt}
    if img is not None:
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=85); msg["images"] = [base64.b64encode(buf.getvalue()).decode()]
    body = {"model": model, "stream": False, "format": "json", "think": False, "options": {"temperature": 0}, "messages": [msg]}
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    antw = json.load(urllib.request.urlopen(req, timeout=300))["message"]["content"]
    try: return json.loads(antw)
    except ValueError: return {}

def wat_zien(tekst):
    """Stap 1 (tekstmodel): wat moet je zien."""
    return [z for z in ollama(LIJST.format(tekst=tekst), model=DENKER).get("zien", []) if isinstance(z, str) and z.strip()][:3]

def vraag(img, zien):
    """Stap 2 (beeldmodel): per punt kijken of het in beeld is."""
    if not zien: return {"ok": True, "mist": "", "zie": "", "zien": []}
    r = ollama(CHECK.format(lijst=chr(10).join(f"{k + 1}. {z}" for k, z in enumerate(zien))), img).get("uitslag", [])
    mist = [(zien[u.get("nr", 0) - 1], u.get("zie", "")) for u in r if not u.get("zichtbaar", True) and 0 < u.get("nr", 0) <= len(zien)]
    return {"ok": not mist, "mist": "; ".join(m for m, _ in mist), "zie": "; ".join(z for _, z in mist), "zien": zien}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video", type=Path); ap.add_argument("zinnen", type=Path)
    ap.add_argument("--van", type=int, default=0); ap.add_argument("--tot", type=int, default=9999); ap.add_argument("--alles", action="store_true", help="ook dialoog")
    a = ap.parse_args()
    Z = json.load(open(a.zinnen, encoding="utf-8")); map_ = a.video.parent; uitmap = map_ / "beeldwachter"; uitmap.mkdir(exist_ok=True)
    uit, fout = [], []
    doe = [i for i, z in enumerate(Z) if a.van <= i <= a.tot and (z[4] == "N" or a.alles)]
    ZIEN = {i: wat_zien(Z[i][2]) for i in doe}               # eerst alle zinnen met het tekstmodel (één keer laden)
    for i in doe: print(f"{i:3d} moet zien: {ZIEN[i]}", flush=True)
    for i, (s, e, tekst, sc, sp, *_) in enumerate(Z):
        if not a.van <= i <= a.tot: continue
        if sp != "N" and not a.alles: continue       # dialoog beschrijft meestal niets wat je moet zien; verteller wel
        ims = [beeld(a.video, s + 0.3), beeld(a.video, (s + e) / 2), beeld(a.video, e - 0.1)]
        pl = Image.new("RGB", (640 * 3 + 20, ims[0].height), "white")
        for k, im in enumerate(ims): pl.paste(im, (k * 650, 0))
        r = vraag(pl, ZIEN[i]); r.update(zin=i, t=round(s, 1), tekst=tekst); uit.append(r)
        print(f"{i:3d} {'OK  ' if r.get('ok') else 'FOUT'} {tekst[:60]}" + ("" if r.get("ok") else f"  -> mist: {r.get('mist')}"), flush=True)
        if not r.get("ok"):
            d = ImageDraw.Draw(pl); f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
            d.rectangle((0, 0, pl.width, 34), fill=(200, 40, 40)); d.text((8, 4), f"zin {i}: {tekst[:120]}", font=f, fill="white")
            pl.save(uitmap / f"zin-{i:03d}.jpg", quality=80); fout.append(r)
    (map_ / "beeldwachter.json").write_text(json.dumps(uit, indent=1, ensure_ascii=False), encoding="utf-8")
    regels = [f"# Beeldwachter: {a.video.name}", "", f"{len(uit)} zinnen bekeken, **{len(fout)} kloppen niet** met het beeld.", ""]
    for r in fout:
        m, s_ = divmod(r["t"], 60)
        regels += [f"- **zin {r['zin']}** ({int(m)}:{s_:04.1f}) \"{r['tekst']}\"", f"  - mist: {r.get('mist')}", f"  - ziet: {r.get('zie')}"]
    (map_ / "BEELDWACHTER.md").write_text("\n".join(regels) + "\n", encoding="utf-8")
    print(f"KLAAR: {len(fout)} van {len(uit)} zinnen kloppen niet -> {map_ / 'BEELDWACHTER.md'}")

if __name__ == "__main__":
    main()
