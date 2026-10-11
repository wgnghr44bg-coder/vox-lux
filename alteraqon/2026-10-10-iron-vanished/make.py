"""What if every piece of iron vanished: Lux-stem (voice.mp3, start op 0,8 s), tijdstempels, flits + klap.

Gebruik (vanuit deze map): python3 make.py <tmpdir>   -> <tmpdir>/iron-vanished.mp4
Beeld, tekst en eindmix komen uit alteraqon/tools/make_video.py (opbouw van de lightning-video);
de indeling per shot staat in shots.py.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "tools", "make_video.py")
os.makedirs(sys.argv[1], exist_ok=True)
subprocess.run([sys.executable, TOOL, HERE, sys.argv[1]], check=True)
