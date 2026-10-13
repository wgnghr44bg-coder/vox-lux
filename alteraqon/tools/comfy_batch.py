"""Clips maken met Wan 2.2 (image-to-video) in je eigen ComfyUI, in één keer voor een hele lijst.

Eenmalig in ComfyUI: open het ingebouwde template "Wan 2.2 5B Video Generation" (Workflow > Browse Templates > Video;
voor de 14B: "Wan 2.2 14B Image to Video"), zet er een startbeeld in,
controleer dat het één keer werkt, en sla het op via Workflow > Export (API) als `wan_i2v_api.json`.

Gebruik (ComfyUI moet draaien):
  python comfy_batch.py wan_i2v_api.json <videomap>
  bv. python comfy_batch.py wan_i2v_api.json alteraqon/2026-10-13-donut-earth
Leest <videomap>/comfy-clips.txt ("NAAM|prompt"), neemt <videomap>/afbeeldingen/NAAM.jpg als startbeeld
en zet de clip in <videomap>/clips/NAAM.mp4. Bestaande clips worden overgeslagen (dus opnieuw starten kan altijd).
Alleen de standaardbibliotheek van Python nodig.
"""
import json, os, sys, time, urllib.parse, urllib.request, uuid

SERVER = "http://127.0.0.1:8188"
WIDTH, HEIGHT, FRAMES, FPS = 1280, 704, 121, 24     # 121 frames / 24 fps = 5 s (Wan 2.2 5B). Voor de 14B: 1280, 720, 81, 16
NEGATIVE = ("morphing, warping, distortion, melting, deformed, extra limbs, extra fingers, new objects, text, logo, "
            "watermark, flicker, blurry, fast motion, jump cut, rainbow")

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

def fill(wf, image, prompt, name):
    wf = json.loads(json.dumps(wf))
    pos = neg = None
    for n in wf.values():
        i = n["inputs"]
        if pos is None and "positive" in i and "negative" in i and isinstance(i["positive"], list):
            pos, neg = i["positive"][0], i["negative"][0]   # sampler/I2V-knooppunt: welke tekst positief is en welke negatief
        if "start_image" in i or n["class_type"] in ("WanImageToVideo", "Wan22ImageToVideoLatent"):
            for k, v in (("width", WIDTH), ("height", HEIGHT), ("length", FRAMES)):
                if k in i and not isinstance(i[k], list): i[k] = v
    for nid, n in wf.items():
        c, i = n["class_type"], n["inputs"]
        if c == "LoadImage": i["image"] = image
        elif c == "CLIPTextEncode" and nid == pos: i["text"] = prompt
        elif c == "CLIPTextEncode" and nid == neg: i["text"] = NEGATIVE
        elif "fps" in i and not isinstance(i["fps"], list): i["fps"] = FPS
        if "filename_prefix" in i: i["filename_prefix"] = f"alteraqon/{name}"
        if "noise_seed" in i: i["noise_seed"] = int.from_bytes(os.urandom(6), "big")
        if "seed" in i and not isinstance(i["seed"], list): i["seed"] = int.from_bytes(os.urandom(6), "big")
    if pos is None: sys.exit("Geen positieve/negatieve prompt gevonden: is dit de API-export van het Wan 2.2-template?")
    return wf

def wait_and_download(pid, out):
    while True:
        h = json.loads(api(f"/history/{pid}")).get(pid)
        if h and h.get("status", {}).get("completed"):
            for node in h["outputs"].values():
                for items in node.values():
                    for f in items if isinstance(items, list) else []:
                        if isinstance(f, dict) and f.get("filename", "").endswith((".mp4", ".webm")):
                            q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
                            open(out, "wb").write(api(f"/view?{q}")); return True
            return False
        if h and h.get("status", {}).get("status_str") == "error": return False
        time.sleep(5)

wf_base, folder = json.load(open(sys.argv[1])), sys.argv[2]
os.makedirs(f"{folder}/clips", exist_ok=True)
for line in open(f"{folder}/comfy-clips.txt", encoding="utf-8"):
    if "|" not in line or line.startswith("#"): continue
    name, prompt = line.strip().split("|", 1)
    out = f"{folder}/clips/{name}.mp4"
    if os.path.exists(out): print(name, "bestaat al"); continue
    t = time.time()
    wf = fill(wf_base, upload(f"{folder}/afbeeldingen/{name}.jpg"), prompt, name)
    pid = json.loads(api("/prompt", json.dumps({"prompt": wf, "client_id": "alteraqon"}).encode(),
                         {"Content-Type": "application/json"}))["prompt_id"]
    print(name, "klaar" if wait_and_download(pid, out) else "MISLUKT (zie ComfyUI-venster)", f"({time.time()-t:.0f} s)")
