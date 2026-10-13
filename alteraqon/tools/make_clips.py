"""NIET MEER GEBRUIKEN (eigenaar 13 okt 2026): clips alleen nog via ComfyUI (Wan 2.2) met tools/comfy_batch.py.
Alleen na uitdrukkelijk ja van de eigenaar: ALTERAQON_XAI_CLIPS=1 python3 ...

Bewegende clips maken met xAI (image-to-video) uit <videomap>/clips.txt.

Gebruik: python3 alteraqon/tools/make_clips.py alteraqon/<datum>-<slug>
clips.txt: één regel per clip, "NAAM|beweging-prompt"; startbeeld is afbeeldingen/NAAM.png (ComfyUI) of NAAM.jpg,
resultaat afbeeldingen/NAAM.mp4 (zonder geluid). make_video.py gebruikt dan de clip i.p.v. de foto.
Bestaande clips worden overgeslagen (nooit dubbel betalen).
Model: grok-imagine-video-1.5-lite (goedkoopste; okt 2026 ca. $0,19 per clip van 6 s, 720p).
Downloaden kan alleen als vidgen.x.ai in de netwerkinstellingen van de omgeving is toegestaan.
"""
import base64, os, subprocess, sys, time, requests
if os.environ.get("ALTERAQON_XAI_CLIPS") != "1":
    sys.exit("Gestopt: xAI-clips zijn uitgezet door de eigenaar. Gebruik ComfyUI (Wan 2.2): alteraqon/tools/comfy_batch.py")
MODEL = "grok-imagine-video-1.5-lite"
os.chdir(sys.argv[1])
for line in open("clips.txt"):
    if "|" not in line: continue
    name, prompt = line.strip().split("|", 1)
    out = f"afbeeldingen/{name}.mp4"
    if os.path.exists(out): continue
    src = f"afbeeldingen/{name}.png" if os.path.exists(f"afbeeldingen/{name}.png") else f"afbeeldingen/{name}.jpg"
    img = f"data:image/{'png' if src.endswith('png') else 'jpeg'};base64," + base64.b64encode(open(src, "rb").read()).decode()
    r = requests.post("https://api.x.ai/v1/videos/generations", timeout=120, json={
        "model": MODEL, "prompt": prompt, "image": {"url": img}, "duration": 6, "aspect_ratio": "9:16", "resolution": "720p"})
    r.raise_for_status(); rid = r.json()["request_id"]
    for _ in range(120):
        d = requests.get(f"https://api.x.ai/v1/videos/{rid}", timeout=60).json()
        if d.get("status") not in ("pending", "processing", None): break
        time.sleep(8)
    if d.get("status") != "done":
        print(name, "mislukt:", str(d)[:200]); continue
    raw = requests.get(d["video"]["url"], timeout=300).content
    open(f"{out}.tmp.mp4", "wb").write(raw)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{out}.tmp.mp4", "-an", "-c:v", "copy", out], check=True)
    os.remove(f"{out}.tmp.mp4")
    print(name, "ok", f"${d.get('usage', {}).get('cost_in_usd_ticks', 0) / 1e10:.2f}")
