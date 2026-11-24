"""Rariteitenwachter (eigenaar 24 nov 2026, na een zwevende roze schijf bij papa's kiespijn: "dit moet echt beter gecontroleerd
worden, graag extra controle of wachter op").

Lagen (gratis, op de pc):
 1. OVERZICHT (altijd): elke --stap seconden (standaard 2) een beeld; 12 per blad op leesbaar formaat (rariteiten/overzicht-NN.jpg).
    CLAUDE LOOPT ALLE BLADEN ZELF NA voordat de video naar de eigenaar gaat (getest 24 nov: dit vindt zwevende vormen,
    tekst buiten kaders, afgesneden hoofden; het kleine model niet).
 2. PIXELS (altijd): harde lijnen/tekst tegen de linker- of rechterrand (afgesneden) -> rood kader op het overzicht.
 3. MODEL (alleen met --model, Ollama qwen2.5vl:7b): extra hulpje; test 24 nov: zag normale blosjes als "zwevend" en miste
    een echte losse schijf, dus nooit als enige controle gebruiken.
Uitslag: <map>/RARITEITEN.md + <map>/rariteiten/ (plaatje per melding) + <map>/rariteiten/overzicht-N.jpg.

  python tools/rariteitenwachter.py <video.mp4> [--stap 3]
"""
import argparse, base64, io, json, subprocess, urllib.request
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5vl:7b"
VRAAG = """You are a strict quality checker for a 2D cartoon video (simple round-headed characters on flat illustrated backgrounds,
subtitles at the bottom, big caption words at the top). Look very carefully at this frame and report ONLY real visual mistakes:
- a shape or object that floats and is not attached to anything, or that covers a character's face/eyes/glasses
- an object drawn on top of a character where it should be behind (or the other way round), or a character standing inside an object
- a head, face, text or object cut off by the edge of the picture or by a frame (like a TV screen) in a way that looks wrong
- text that runs outside its box, overlaps other text, is unreadable, misspelled, or has strange letters
- half-erased or ghost-like shapes, smudges, duplicated objects, broken drawings
- anything a viewer would find confusing ("what is that round thing?")
Normal things are fine and must NOT be reported: cartoon style, flat colors, the small pink blush circles on every character's
cheeks (that is the design), round heads, glasses, subtitles at the bottom, big captions at the top (they float on purpose),
name tags, a character holding something, a price tag next to a product.
Only report something if you are sure it looks broken. Be specific: what it is and where (left/middle/right, top/bottom).
Answer ONLY with JSON: {"ok": true or false, "problemen": ["short description with where in the picture", ...]}"""

def beeld(video, t, breed=1280):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={breed}:-1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")

def vraag(img):
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=88)
    body = {"model": MODEL, "stream": False, "format": "json", "options": {"temperature": 0},
            "messages": [{"role": "user", "content": VRAAG, "images": [base64.b64encode(buf.getvalue()).decode()]}]}
    req = urllib.request.Request(OLLAMA, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try: return json.loads(json.load(urllib.request.urlopen(req, timeout=300))["message"]["content"])
    except Exception as e: return {"ok": True, "problemen": [], "fout": str(e)[:80]}

def rand(img):
    """Pixelcheck: harde tekst/lijnen die precies tegen de linker/rechter rand lopen (afgesneden). Geeft de kanten terug."""
    a = np.asarray(img.convert("L")).astype(int); kant = []
    for naam, kol in (("links", a[60:-160, :3]), ("rechts", a[60:-160, -3:])):
        donker = (kol < 40).mean()
        if donker > 0.06: kant.append(naam)
    return kant

def duur(video):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                                capture_output=True, text=True).stdout.strip())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video", type=Path); ap.add_argument("--stap", type=float, default=2.0); ap.add_argument("--model", action="store_true")
    a = ap.parse_args(); map_ = a.video.parent; uit = map_ / "rariteiten"; uit.mkdir(exist_ok=True)
    for f in uit.glob("*.jpg"): f.unlink()
    D = duur(a.video); ts = [round(t, 2) for t in np.arange(0.5, D - 0.3, a.stap)]
    meld, ims = [], []
    f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    for t in ts:
        im = beeld(a.video, t); r = vraag(im) if a.model else {"ok": True}; kant = rand(im)
        prob = [p for p in r.get("problemen", []) if isinstance(p, str) and p.strip()] if not r.get("ok", True) else []
        prob += [f"iets loopt tegen de {k}rand (afgesneden?)" for k in kant]
        klein = im.resize((640, 360)); d = ImageDraw.Draw(klein); d.text((6, 4), f"{int(t // 60)}:{t % 60:04.1f}", font=f, fill=(255, 0, 0))
        if prob:
            meld.append({"t": t, "problemen": prob}); d.rectangle((0, 0, 639, 359), outline=(255, 0, 0), width=6)
            im.save(uit / f"t{int(t * 10):05d}.jpg", quality=85)
        ims.append(klein)
        print(f"{int(t // 60)}:{t % 60:04.1f} {'OK' if not prob else 'LET OP: ' + ' | '.join(prob)}", flush=True)
    for v in range(0, len(ims), 12):                    # overzicht van ALLE beelden, 12 per blad (rood kader = melding)
        pl = Image.new("RGB", (640 * 3, 360 * 4), "black")
        for i, im in enumerate(ims[v:v + 12]): pl.paste(im, (640 * (i % 3), 360 * (i // 3)))
        pl.save(uit / f"overzicht-{v // 12:02d}.jpg", quality=82)
    regels = [f"# Rariteitenwachter: {a.video.name}", "", f"{len(ts)} beelden bekeken (elke {a.stap:g} s), **{len(meld)} met een melding**.",
              "VERPLICHT: Claude loopt zelf alle rariteiten/overzicht-*.jpg na (zwevende vormen, tekst buiten kaders, afgesneden dingen).", ""]
    for m in meld: regels.append(f"- **{int(m['t'] // 60)}:{m['t'] % 60:04.1f}** " + " | ".join(m["problemen"]))
    (map_ / "RARITEITEN.md").write_text("\n".join(regels) + "\n", encoding="utf-8")
    print(f"KLAAR: {len(meld)} meldingen van {len(ts)} beelden -> {map_ / 'RARITEITEN.md'}")

if __name__ == "__main__":
    main()
