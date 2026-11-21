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
ZINNEN = """Wie dit jaar een computer wilde bouwen, merkte iets vreemds.
Het geheugen, het RAM, kostte ineens meer dan bijna alles in de kast.
Een populaire set van tweeëndertig gigabyte snel geheugen kost nu zo'n vierhonderd tot vijfhonderd dollar.
In de zomer van vorig jaar kostte zo'n set gemiddeld honderdvijftien dollar.
Dat is ongeveer vier keer zo veel, in iets meer dan een jaar.
Dus wat is er gebeurd?
Het korte antwoord is: kunstmatige intelligentie.
De bedrijven die geheugenchips maken, verkopen zo veel mogelijk aan datacenters voor AI.
En voor de rest van ons blijft er simpelweg te weinig over.
In het derde kwartaal haalde de hele geheugenindustrie zo'n tweehonderd miljard dollar binnen.
Dat is driehonderdnegenenzestig procent meer dan een jaar eerder.
Maar het aantal chips dat ze verkochten, groeide maar met ongeveer vier procent.
Bijna al dat extra geld kwam dus uit één ding: hogere prijzen.
En dat raakt ook Nederland.
Want de machines om die chips te maken, komen voor een groot deel uit Veldhoven, van ASML.
Laten we kijken hoe het zo ver kwam, wie eraan verdient, en wanneer het stopt.""".splitlines()
cfg = VoiceConfig(voice="richard-nl", speed=0.96, seed=1, num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
delen = []
for i, z in enumerate(ZINNEN):
    a = ov.speak([z], cfg, seed=1 + i)[0]
    delen += [a, np.zeros(int(ov.SR * (0.55 if z.endswith("?") else 0.35)), dtype=np.float32)]
uit = np.concatenate(delen)
sf.write(r"C:/Users/rane/vox-lux-stemmen/richard/proef-1min.wav", uit, ov.SR)
print("lengte", round(len(uit) / ov.SR, 1), "s")
