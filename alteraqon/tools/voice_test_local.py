"""Stemtest op je eigen pc (gratis): dezelfde zin in 6 Kokoro-stemmen + Chatterbox, om naast elkaar te beluisteren.

Installeren (eenmalig, in een APARTE map/omgeving zodat ComfyUI niet geraakt wordt), in PowerShell:
  python -m venv stem-env
  stem-env\\Scripts\\activate
  pip install kokoro soundfile
  pip install chatterbox-tts
  (Kokoro op Windows: installeer ook espeak-ng, https://github.com/espeak-ng/espeak-ng/releases -> .msi)

Gebruik (met stem-env actief, vanuit de map vox-lux):
  python alteraqon/tools/voice_test_local.py
-> map stemtest/ met o.a. kokoro_bm_george.wav, chatterbox_standaard.wav, chatterbox_als_bm_george_spannend.wav
De eerste keer worden de modellen gedownload (Kokoro ±0,3 GB, Chatterbox ±3 GB).
Beide mogen gebruikt worden op een kanaal met inkomsten (Kokoro: Apache 2.0, Chatterbox: MIT).
"""
import os, sys

TEXT = ("What if Earth was shaped like a donut, with a giant hole in the middle? "
        "You wake up in your city. The morning light looks strange. Then.")
KOKORO_VOICES = ["am_michael", "am_onyx", "am_fenrir", "bm_george", "bm_lewis", "bm_daniel"]   # am = Amerikaans, bm = Brits
CLONE_FROM = "bm_george"      # deze Kokoro-stem dient als voorbeeld voor Chatterbox
OUT = "stemtest"
os.makedirs(OUT, exist_ok=True)

# --- Kokoro: 6 vaste stemmen ---
try:
    import numpy as np, soundfile as sf
    from kokoro import KPipeline
    pipes = {}
    for v in KOKORO_VOICES:
        lang = v[0]                                   # 'a' = Amerikaans Engels, 'b' = Brits Engels
        pipes.setdefault(lang, KPipeline(lang_code=lang))
        audio = np.concatenate([a for _, _, a in pipes[lang](TEXT, voice=v, speed=1.0)])
        sf.write(f"{OUT}/kokoro_{v}.wav", audio, 24000); print("klaar:", f"{OUT}/kokoro_{v}.wav")
except ImportError as e:
    print("Kokoro overgeslagen (niet geïnstalleerd):", e)

# --- Chatterbox: standaardstem + Kokoro-stem nagedaan, rustig en spannend ---
try:
    import torch, torchaudio as ta
    from chatterbox.tts import ChatterboxTTS
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = ChatterboxTTS.from_pretrained(device=dev)
    ref = f"{OUT}/kokoro_{CLONE_FROM}.wav"
    runs = [("standaard", None, 0.5, 0.5)]
    if os.path.exists(ref):
        runs += [(f"als_{CLONE_FROM}_rustig", ref, 0.4, 0.5), (f"als_{CLONE_FROM}_spannend", ref, 0.8, 0.3)]
    for name, prompt, exag, cfg in runs:
        wav = model.generate(TEXT, audio_prompt_path=prompt, exaggeration=exag, cfg_weight=cfg)
        ta.save(f"{OUT}/chatterbox_{name}.wav", wav, model.sr); print("klaar:", f"{OUT}/chatterbox_{name}.wav")
except ImportError as e:
    print("Chatterbox overgeslagen (niet geïnstalleerd):", e)

print("\nBeluister de bestanden in", os.path.abspath(OUT), "en zeg welke je het beste vindt.")
