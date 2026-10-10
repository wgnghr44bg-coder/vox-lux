"""Afbeeldingen maken met xAI (grok-imagine-image, 9:16) uit <videomap>/prompts.txt.

Gebruik: python3 alteraqon/tools/make_images.py alteraqon/<datum>-<slug>
prompts.txt: één regel per beeld, "NAAM|prompt". Bestaande afbeeldingen worden overgeslagen
(dus nooit dubbel betalen). Eén voor één, want xAI staat max. 6 verzoeken per seconde toe.
Kosten: ca. $0,02 per afbeelding.
"""
import base64, os, sys, time, requests
os.chdir(sys.argv[1]); os.makedirs("afbeeldingen", exist_ok=True)
for line in open("prompts.txt"):
    if "|" not in line: continue
    name, prompt = line.strip().split("|", 1)
    out = f"afbeeldingen/{name}.jpg"
    if os.path.exists(out): continue
    for attempt in range(4):
        r = requests.post("https://api.x.ai/v1/images/generations", timeout=300, json={
            "model": "grok-imagine-image", "prompt": prompt, "n": 1,
            "aspect_ratio": "9:16", "response_format": "b64_json"})
        if r.ok:
            open(out, "wb").write(base64.b64decode(r.json()["data"][0]["b64_json"])); print(name, "ok"); break
        print(name, r.status_code, r.text[:150]); time.sleep(2 ** (attempt + 1))
