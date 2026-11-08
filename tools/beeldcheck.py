"""Dubbele beeldcontrole zonder Claude (eigenaar 8 nov 2026: "ja maar dan extra controle op verkeerde beelden").

Elk beeld moet door TWEE verschillende lokale modellen worden goedgekeurd:
  1. Qwen2.5-VL (Ollama, qwen2.5vl:7b) beantwoordt vaste vragen: dingen die er toen niet waren, tekst/letters,
     vervormde mensen of handen, en past het beeld bij de beschrijving.
  2. CLIP (openai/clip-vit-large-patch14) geeft scores op "modern", "tekst" en "vervormd" t.o.v. een gewone historische
     foto; drempels afgesteld op de afgekeurde beelden van Tombstone en Egypte (tools/beeldcheck_ijk.py).
Afgekeurd = opnieuw maken met ComfyUI (andere seed); na 2 mislukte pogingen herschrijft het tekstmodel de
beeldbeschrijving (wat er wél is) en probeert opnieuw; na 4 pogingen stopt het (melding, niets online).

  python tools/beeldcheck.py stories/<map>              # controleren en zo nodig opnieuw maken
  python tools/beeldcheck.py stories/<map> --alleen-kijken
Uitslag: <map>/beeldcheck.json en overzichtsvellen <map>/beeldcheck-vel-N.jpg; laatste regel BEELDEN GOED / BEELDEN FOUT.
"""
import base64, io, json, re, subprocess, sys, time
from pathlib import Path

import requests

HIER = Path(__file__).resolve().parent
OLLAMA = "http://127.0.0.1:11434/api/chat"
VLM = "qwen2.5vl:7b"
DREMPELS = json.loads((HIER / "beeldcheck_drempels.json").read_text(encoding="utf-8")) \
    if (HIER / "beeldcheck_drempels.json").exists() else {"modern": 0.0, "tekst": 0.0, "vervormd": 0.0}

MODERN = ["a car", "a truck", "a motorcycle", "electric power lines and poles", "an electric street lamp",
          "a modern house with glass windows", "a modern concrete building", "a ceiling fan", "a plastic chair",
          "a road sign", "an asphalt road with markings", "a smartphone", "modern clothes, jeans and t-shirt"]
TEKST = ["a picture with text and letters written on it", "a sign with words", "a watermark"]
VERVORMD = ["a person with a deformed face", "a hand with extra fingers", "a distorted body with extra limbs",
            "a strange melted object"]


def jaar(map_):
    t = (Path(map_) / "planning.txt").read_text(encoding="utf-8") if (Path(map_) / "planning.txt").exists() else ""
    bc = re.search(r"\b(\d{1,4}) ?(BC|v\.? ?Chr)", t)
    if bc:                                                   # eerst "1323 BC" (anders leest hij 1323 als jaartal na Christus)
        return -int(bc.group(1))
    j = re.findall(r"\b(1[0-9]{3})\b", t)
    return int(j[0]) if j else 1900


# ---------- 1. Qwen2.5-VL ----------
def vlm(pad, wat_er_moet_zijn, tijd):
    b64 = base64.b64encode(Path(pad).read_bytes()).decode()
    vraag = (f"This image is for a calm history video set in {tijd}. It should show: {wat_er_moet_zijn}\n"
             "Look carefully at the whole image, also the background and the edges. Answer in JSON:\n"
             '{"anachronisms": ["things that did not exist in that time, e.g. cars, power lines, electric lamps, modern '
             'buildings, plastic, modern clothes, signs"], "text_or_letters": true/false, '
             '"deformed": "describe deformed faces, hands with wrong number of fingers, extra limbs, melted objects, or empty", '
             '"matches_description": true/false, "frightening": true/false}')
    for _ in range(3):
        try:
            r = requests.post(OLLAMA, json={"model": VLM, "stream": False, "format": "json", "options": {"temperature": 0},
                                            "messages": [{"role": "user", "content": vraag, "images": [b64]}]}, timeout=600)
            a = json.loads(r.json()["message"]["content"])
            fout = []
            ana = [x for x in a.get("anachronisms", []) if isinstance(x, str) and x.strip() and "none" not in x.lower()]
            ana = [x for x in ana if bevestig(b64, x, tijd)]       # tweede, gerichte vraag: is het er echt?
            if ana:
                fout.append("niet uit die tijd: " + ", ".join(x[:80] for x in ana))
            if a.get("text_or_letters") is True and bevestig(b64, "readable text, letters or words written in the image", tijd):
                fout.append("tekst/letters")
            d = a.get("deformed", "")
            d = "" if d is False or d is None else str(d).strip()
            if d and d.lower().rstrip(".") not in ("", "none", "no", "empty", "n/a", "nothing", "false", "no deformities",
                                                   "none observed", "no deformities observed"):
                fout.append("vervormd: " + d[:80])
            if a.get("matches_description") is False and fout:    # alleen samen met een echte fout
                fout.append("past niet bij de beschrijving")
            if a.get("frightening") is True:
                fout.append("eng")
            return fout
        except Exception as e:
            print("  VLM opnieuw:", e, flush=True)
            time.sleep(10)
    return ["VLM gaf geen antwoord"]


def bevestig(b64, ding, tijd):
    """Gerichte tweede vraag (minder onterechte afkeuringen, test 8 nov: 10/30 goede beelden onterecht afgekeurd)."""
    vraag = (f"Look very carefully at this image. Is there clearly and visibly {ding}? Only answer yes if you can point "
             f"to it. Note: things that really existed in {tijd} are fine. "
             'JSON: {"visible": true or false, "where": "..."}')
    try:
        r = requests.post(OLLAMA, json={"model": VLM, "stream": False, "format": "json", "options": {"temperature": 0},
                                        "messages": [{"role": "user", "content": vraag, "images": [b64]}]}, timeout=600)
        return json.loads(r.json()["message"]["content"]).get("visible") is True
    except Exception:
        return True                                          # bij twijfel: afkeuren (veilig)


# ---------- 2. CLIP ----------
_clip = None


def clip_scores(paden, tijd_jaar):
    global _clip
    import torch
    from PIL import Image
    from transformers import CLIPModel, CLIPProcessor
    if _clip is None:
        _clip = (CLIPModel.from_pretrained("openai/clip-vit-large-patch14").eval(),
                 CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14"))
    model, proc = _clip
    modern = [m for m in MODERN if not (tijd_jaar >= 1930 and m in ("a car", "a truck", "a motorcycle", "electric power lines and poles",
                                                                       "an electric street lamp", "a road sign"))]
    neutraal = ["a calm realistic historical photograph", "a painting-like realistic scene from the past"]
    labels = neutraal + modern + TEKST + VERVORMD
    import numpy as np
    det = np.load(HIER / "beeldcheck_clip.npz") if (HIER / "beeldcheck_clip.npz").exists() else None
    with torch.no_grad():
        uit = []
        for p in paden:
            inp = proc(text=labels, images=Image.open(p).convert("RGB"), return_tensors="pt", padding=True)
            o = model(**inp)
            s = o.logits_per_image.softmax(-1)[0].tolist()
            kans = None
            if det is not None:                              # geleerde detector (tools/beeldcheck_train.py)
                e = o.image_embeds[0].numpy()
                e = e / np.linalg.norm(e)
                kans = float(1 / (1 + np.exp(-(e @ det["w"] + float(det["b"])))))
            n = max(s[:2])
            g = lambda grp: max(s[labels.index(x)] for x in grp) - n
            uit.append({"modern": round(g(modern), 4), "tekst": round(g(TEKST), 4), "vervormd": round(g(VERVORMD), 4),
                        "afgekeurd_kans": None if kans is None else round(kans, 3),
                        "drempel": None if det is None else round(float(det["drempel"]), 3)})
    return uit


def clip_fout(sc):
    """Tweede controle: de geleerde detector (lijkt het beeld op eerder afgekeurde beelden?)."""
    if sc.get("afgekeurd_kans") is not None:
        return [f"CLIP-detector: lijkt op afgekeurde beelden ({sc['afgekeurd_kans']:.2f})"] if sc["afgekeurd_kans"] > sc["drempel"] else []
    return [f"CLIP {k} {sc[k]:+.2f}" for k in ("modern", "tekst", "vervormd") if sc[k] > DREMPELS[k]]


# ---------- 3. controleren en opnieuw maken ----------
def prompts(map_):
    uit = {}
    for l in (Path(map_) / "prompts.txt").read_text(encoding="utf-8").splitlines():
        if "|" in l and not l.startswith("#"):
            n, p = l.split("|", 1)
            uit[n.strip()] = p.strip()
    return uit


def stijl(map_):
    s = Path(map_) / "src-feiten" / "stijl.txt"
    return " ".join(s.read_text(encoding="utf-8").split()) if s.exists() else ""


def vlm_vrij():                                             # Ollama-model uit het videogeheugen (ComfyUI heeft het nodig)
    try:
        requests.post(OLLAMA.replace("/chat", "/generate"), json={"model": VLM, "keep_alive": 0}, timeout=60)
    except Exception:
        pass


def comfy_vrij():
    try:
        requests.post("http://127.0.0.1:8188/free", json={"unload_models": True, "free_memory": True}, timeout=60)
    except Exception:
        pass


def opnieuw_maken(map_, namen):
    vlm_vrij()
    subprocess.run([sys.executable, str(HIER / "comfy" / "comfy_batch.py"), str(HIER / "comfy" / "zimage_api.json"),
                    str(map_)] + namen, cwd=HIER.parent)
    comfy_vrij()


def herschrijf_prompt(map_, naam, oud, fouten):
    sys.path.insert(0, str(HIER / "scriptgen"))
    import llm
    st = stijl(map_)
    kern = oud.replace(st, "").strip().rstrip(",")
    nieuw = llm.vraag(f"An image generator keeps adding mistakes to this picture: {fouten}.\nPicture description: {kern}\n"
                      "Rewrite the description in one sentence so it clearly states what IS there instead (for example "
                      "'only horses, wagons and wooden buildings; open land in the distance', or 'an indoor scene, enclosed "
                      "by walls, a plain ceiling'). Never use the word 'no' or 'without'. Only the sentence.",
                      temp=0.4, max_tokens=120)
    regels = (Path(map_) / "prompts.txt").read_text(encoding="utf-8").splitlines()
    regels = [f"{naam}|{' '.join(nieuw.split())}, {st}" if r.startswith(naam + "|") else r for r in regels]
    (Path(map_) / "prompts.txt").write_text("\n".join(regels) + "\n", encoding="utf-8")


def vellen(map_, namen, fouten):
    from PIL import Image, ImageDraw
    beelden = sorted((Path(map_) / "afbeeldingen").glob("*.png"))
    for v in range(0, len(beelden), 12):
        vel = Image.new("RGB", (4 * 480, 3 * 290), "black")
        dr = ImageDraw.Draw(vel)
        for k, p in enumerate(beelden[v:v + 12]):
            im = Image.open(p).convert("RGB").resize((480, 270))
            x, y = (k % 4) * 480, (k // 4) * 290
            vel.paste(im, (x, y))
            dr.text((x + 5, y + 272), p.stem + (" FOUT" if p.stem in fouten else " ok"), fill="red" if p.stem in fouten else "white")
        vel.save(Path(map_) / f"beeldcheck-vel-{v // 12 + 1}.jpg", quality=80)


def controleer(map_, namen):
    pr, j = prompts(map_), jaar(map_)
    tijd = f"the year {j}" if j > 0 else f"{-j} BC"
    st = stijl(map_)
    paden = [Path(map_) / "afbeeldingen" / f"{n}.png" for n in namen]
    cs = clip_scores(paden, j)
    uit = {}
    for n, p, sc in zip(namen, paden, cs):
        kern = pr.get(n, "").replace(st, "").strip().rstrip(",")
        f = clip_fout(sc) + vlm(p, kern, tijd)
        uit[n] = {"fouten": f, "clip": sc}
        print(f"  {n}: {'GOED' if not f else 'FOUT ' + '; '.join(f)}", flush=True)
    return uit


if __name__ == "__main__":
    m = Path(sys.argv[1])
    alle = sorted(p.stem for p in (m / "afbeeldingen").glob("*.png"))
    comfy_vrij()
    uitslag = controleer(m, alle)
    if "--alleen-kijken" not in sys.argv:
        for poging in range(1, 5):
            fout = [n for n, u in uitslag.items() if u["fouten"]]
            if not fout:
                break
            print(f"poging {poging}: {len(fout)} beelden opnieuw maken", flush=True)
            if poging >= 3:
                pr = prompts(m)
                for n in fout:
                    herschrijf_prompt(m, n, pr[n], uitslag[n]["fouten"])
            for n in fout:
                (m / "afbeeldingen" / f"{n}.png").unlink(missing_ok=True)
            opnieuw_maken(m, fout)
            uitslag |= controleer(m, fout)
    vlm_vrij()
    fout = [n for n, u in uitslag.items() if u["fouten"]]
    (m / "beeldcheck.json").write_text(json.dumps(uitslag, indent=1, ensure_ascii=False), encoding="utf-8")
    vellen(m, alle, set(fout))
    print(f"BEELDEN {'GOED' if not fout else 'FOUT'}: {len(alle) - len(fout)}/{len(alle)} goedgekeurd"
          + (f", fout: {fout}" if fout else ""))
    sys.exit(1 if fout else 0)
