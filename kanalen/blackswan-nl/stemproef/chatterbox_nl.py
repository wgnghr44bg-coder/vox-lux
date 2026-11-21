"""21 nov: zelfde proeftekst met Chatterbox Multilingual (taal nl) en de stem van de eigenaar als voorbeeld. Vergelijken met OmniVoice op klemtoon."""
import re, sys, torch, numpy as np, soundfile as sf
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
src = open("proef1min.py", encoding="utf-8").read()
ZINNEN = re.search(r'ZINNEN = """(.*?)"""', src, re.S).group(1).splitlines()
m = ChatterboxMultilingualTTS.from_pretrained(device="cuda")
REF = r"C:/Users/rane/vox-lux-stemmen/richard/ref.wav"
for naam, exag, cfgw in [("cb-nieuw", 0.5, 0.5)]:
    delen = []
    for i, z in enumerate(ZINNEN):
        torch.manual_seed(1 + i)
        w = m.generate(z, language_id="nl", audio_prompt_path=REF, exaggeration=exag, cfg_weight=cfgw)
        a = w.squeeze().cpu().numpy().astype(np.float32)
        delen += [a, np.zeros(int(m.sr * (0.4 if z.endswith("?") else 0.25)), dtype=np.float32)]
    uit = np.concatenate(delen)
    sf.write(rf"C:/Users/rane/vox-lux-stemmen/richard/proef-{naam}.wav", uit, m.sr)
    print(naam, round(len(uit) / m.sr, 1), "s", flush=True)
