"""21 nov: proef van ± 1 min met de vaste NL-stem (richard-nl, 0.96, seed 1). Tekst: opening RAM-video (reserve1-ram), vertaald."""
import sys
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf
from voice import omnivoice_engine as ov
from voice.voice_config import VoiceConfig
import b1
inst = b1.standaard()
ZINNEN = """Wie dit jaar een computer wilde bouwen of uitbreiden, schrok waarschijnlijk van één onderdeel: het werkgeheugen.
Een populaire set van tweeëndertig gigabyte kost inmiddels zo'n vierhonderd tot vijfhonderd dollar.
Vorig jaar zomer betaalde je daar gemiddeld nog honderdvijftien dollar voor.
In ruim een jaar tijd is de prijs dus ongeveer verviervoudigd.
Hoe kan dat?
Kort gezegd: door kunstmatige intelligentie.
Geheugenmakers verkopen zoveel mogelijk chips aan datacenters voor AI, en voor gewone computers en telefoons blijft er te weinig over.
Dat zie je terug in de cijfers.
De omzet van de geheugenindustrie kwam in het derde kwartaal uit op zo'n tweehonderd miljard dollar, bijna vijf keer zoveel als een jaar eerder.
Toch leverden de fabrikanten maar zo'n vier procent meer geheugen.
Die extra omzet komt dus vrijwel helemaal uit hogere prijzen.
Ook voor Nederland is dat nieuws, want de belangrijkste machines om deze chips te maken, komen van ASML uit Veldhoven.
In deze video kijken we hoe het zover is gekomen, wie eraan verdient en wanneer de prijzen weer kunnen dalen.""".splitlines()
EXTRA = {}
cfg = VoiceConfig(voice="richard-nl", speed=1.1, seed=1, num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
delen = []
for i, z in enumerate(ZINNEN):
    a = ov.speak([z], cfg, seed=1 + i + EXTRA.get(i, 0))[0]
    delen += [a, np.zeros(int(ov.SR * (0.45 if z.endswith("?") else 0.28)), dtype=np.float32)]
uit = np.concatenate(delen)
sf.write(r"C:/Users/rane/vox-lux-stemmen/richard/proef-1min.wav", uit, ov.SR)
print("lengte", round(len(uit) / ov.SR, 1), "s")
