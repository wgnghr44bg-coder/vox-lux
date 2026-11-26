"""Kokoro-stemmen (gratis, Apache-2.0, mag op kanalen met inkomsten) voor bijfiguren (eigenaar 26 nov 2026: "de stemmen lijken veel op
elkaar ... je mag andere stemmen downloaden als ze maar echt lijken").
  <kokoro-venv>/python tools/kokoro_zeg.py opdracht.json
opdracht.json = [{"stem": "am_michael", "tekst": "...", "uit": "pad.wav", "speed": 1.0}, ...]  -> wav's op 24 kHz mono.
Stemmen: af_* / am_* (Amerikaans vrouw/man), bf_* / bm_* (Brits)."""
import json, sys
import numpy as np, soundfile as sf
from kokoro import KPipeline
taken = json.load(open(sys.argv[1], encoding="utf-8"))
pijp = {}
for tk in taken:
    lang = "b" if tk["stem"][0] == "b" else "a"
    if lang not in pijp: pijp[lang] = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    stukken = [np.asarray(a, dtype=np.float32) for _, _, a in pijp[lang](tk["tekst"], voice=tk["stem"], speed=tk.get("speed", 1.0))]
    sf.write(tk["uit"], np.concatenate(stukken), 24000); print("ok", tk["stem"], tk["uit"], flush=True)
