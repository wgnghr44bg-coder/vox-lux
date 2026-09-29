"""Maak afbeeldingen met xAI (Grok Imagine) uit afbeeldingen-prompts.md.

Gebruik: python3 tools/xai_images.py stories/pompeii 1 11 25   (of: all)
Slaat op als <map>/afbeeldingen/001.jpg enz.; bestaande bestanden worden overgeslagen.
"""
import json, re, sys, time, urllib.request, base64
from pathlib import Path

MODEL = "grok-imagine-image"

def prompts(story):
    text = (story / "afbeeldingen-prompts.md").read_text()
    return {int(n): p.strip() for n, p in re.findall(r"^## (\d{3}).*?```\n(.*?)```", text, re.S | re.M)}

def generate(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "n": 1,
                       "aspect_ratio": "16:9", "response_format": "b64_json"}).encode()
    req = urllib.request.Request("https://api.x.ai/v1/images/generations", body,
                                 {"Content-Type": "application/json"})
    for attempt in range(4):
        try:
            return base64.b64decode(json.load(urllib.request.urlopen(req, timeout=180))["data"][0]["b64_json"])
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code < 500 and e.code != 429:
                raise SystemExit(f"HTTP {e.code}: {msg}")
            print("  opnieuw proberen:", e.code, msg)
        time.sleep(2 ** (attempt + 1))
    raise SystemExit("mislukt na 4 pogingen")

def main():
    story = Path(sys.argv[1])
    ps = prompts(story)
    nums = sorted(ps) if sys.argv[2:] == ["all"] else [int(a) for a in sys.argv[2:]]
    out = story / "afbeeldingen"
    out.mkdir(exist_ok=True)
    for n in nums:
        f = out / f"{n:03d}.jpg"
        if f.exists():
            continue
        print(f"{n:03d} ...", flush=True)
        f.write_bytes(generate(ps[n]))

if __name__ == "__main__":
    main()
