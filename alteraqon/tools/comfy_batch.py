"""Beelden of clips in één keer laten maken door je eigen ComfyUI (gratis, op je pc).

Eenmalig in ComfyUI (Workflow > Browse Templates), laat het template één keer met de hand draaien en sla het op
via Workflow > Export (API):
  - beelden: template "Z-Image Turbo" (tekst naar beeld)            -> zimage_api.json
  - clips:   template "Wan 2.2 5B Video Generation" + een startbeeld -> wan_i2v_api.json

Gebruik (ComfyUI moet draaien):
  python comfy_batch.py zimage_api.json   <videomap>   # leest prompts.txt     -> <videomap>/afbeeldingen/NAAM.png
  python comfy_batch.py wan_i2v_api.json  <videomap>   # leest comfy-clips.txt -> <videomap>/clips/NAAM.mp4
                                                        #   (startbeeld = afbeeldingen/NAAM.png, anders .jpg)
  Optioneel daarachter alleen bepaalde namen: ... <videomap> L05 L20   en --short voor staande beelden (Shorts)
Het script ziet zelf aan de workflow (wel/geen Load Image) of het beelden of clips maakt.
Bestaande bestanden worden overgeslagen, dus opnieuw starten kan altijd. Alleen standaard-Python nodig.
"""
import json, os, sys, time, urllib.parse, urllib.request, uuid

SERVER = "http://127.0.0.1:8188"
IMG_W, IMG_H = 1280, 720                              # beelden: lange video 16:9; Short: 1088, 1920 (of 768, 1344 + opschalen)
VID_W, VID_H, FRAMES, FPS = 1024, 576, 121, 24        # clips: 121 frames / 24 fps = 5 s (Wan 2.2 5B, 8 GB-kaart)
NEGATIVE_VID = ("morphing, warping, distortion, melting, deformed, extra limbs, extra fingers, new objects, text, logo, "
                "watermark, flicker, blurry, fast motion, jump cut, rainbow")
NEGATIVE_IMG = "text, logo, watermark, cartoon, illustration, deformed, extra fingers, blurry, low quality"

def api(path, data=None, headers=None):
    req = urllib.request.Request(SERVER + path, data=data, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        return r.read()

def upload(img):
    b = uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{os.path.basename(img)}\"\r\n"
            f"Content-Type: image/jpeg\r\n\r\n").encode() + open(img, "rb").read() + \
           f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
    return json.loads(api("/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={b}"}))["name"]

def fill(wf, video, image, prompt, name):
    wf = json.loads(json.dumps(wf))
    w, h = (VID_W, VID_H) if video else (IMG_W, IMG_H)
    pos = neg = None
    for n in wf.values():
        i = n["inputs"]
        if pos is None and "positive" in i and "negative" in i and isinstance(i["positive"], list):
            pos, neg = i["positive"][0], i["negative"][0]   # sampler: welke tekst positief is en welke negatief
        if "width" in i and "height" in i and ("batch_size" in i or "start_image" in i):   # latent-/I2V-knooppunt
            for k, v in (("width", w), ("height", h), ("length", FRAMES)):
                if k in i and not isinstance(i[k], list): i[k] = v
    for nid, n in wf.items():
        c, i = n["class_type"], n["inputs"]
        if c == "LoadImage": i["image"] = image
        elif c == "CLIPTextEncode" and nid == pos: i["text"] = prompt
        elif c == "CLIPTextEncode" and nid == neg: i["text"] = NEGATIVE_VID if video else NEGATIVE_IMG
        elif "fps" in i and not isinstance(i["fps"], list): i["fps"] = FPS
        if "filename_prefix" in i: i["filename_prefix"] = f"alteraqon/{name}"
        for k in ("seed", "noise_seed"):
            if k in i and not isinstance(i[k], list): i[k] = int.from_bytes(os.urandom(6), "big")
    if pos is None: sys.exit("Geen positieve prompt gevonden: is dit een API-export (Workflow > Export (API))?")
    return wf

def wait_and_download(pid, out, exts):
    while True:
        h = json.loads(api(f"/history/{pid}")).get(pid)
        if h and h.get("status", {}).get("completed"):
            for node in h["outputs"].values():
                for items in node.values():
                    for f in items if isinstance(items, list) else []:
                        if isinstance(f, dict) and f.get("filename", "").lower().endswith(exts):
                            q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
                            open(out, "wb").write(api(f"/view?{q}")); return True
            return False
        if h and h.get("status", {}).get("status_str") == "error": return False
        time.sleep(3)

args = [a for a in sys.argv[1:] if a != "--short"]
if "--short" in sys.argv: IMG_W, IMG_H = 1088, 1920
wf_base, folder, only = json.load(open(args[0])), args[1], set(args[2:])
video = any(n["class_type"] == "LoadImage" for n in wf_base.values())
src, outdir, ext = ("comfy-clips.txt", "clips", ".mp4") if video else ("prompts.txt", "afbeeldingen", ".png")
os.makedirs(f"{folder}/{outdir}", exist_ok=True)
print("Modus:", "clips (Wan)" if video else "beelden", "|", src, "->", outdir)
for line in open(f"{folder}/{src}", encoding="utf-8"):
    if "|" not in line or line.startswith("#"): continue
    name, prompt = line.strip().split("|", 1)
    if only and name not in only: continue
    out = f"{folder}/{outdir}/{name}{ext}"
    if os.path.exists(out): print(name, "bestaat al"); continue
    t = time.time()
    start = f"{folder}/afbeeldingen/{name}.png"
    image = upload(start if os.path.exists(start) else start[:-4] + ".jpg") if video else None
    wf = fill(wf_base, video, image, prompt, name)
    pid = json.loads(api("/prompt", json.dumps({"prompt": wf, "client_id": "alteraqon"}).encode(),
                         {"Content-Type": "application/json"}))["prompt_id"]
    exts = (".mp4", ".webm") if video else (".png", ".jpg", ".jpeg", ".webp")
    print(name, "klaar" if wait_and_download(pid, out, exts) else "MISLUKT (zie ComfyUI-venster)", f"({time.time()-t:.0f} s)")
