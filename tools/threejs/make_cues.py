"""Haalt de ondertitels uit een What-If pagina (SCENES[..].subtitles) en schrijft
<map>/cues.tsv + <map>/script-cues.txt voor make_voice_local.py en place_voice.py.

Gebruik (vanuit de map vox-lux):
  python tools/threejs/make_cues.py tools/threejs/never-stopped-raining.html tools/threejs/never-stopped-raining
"""
import os, re, sys

if len(sys.argv) != 3:
    sys.exit(__doc__)
html, folder = sys.argv[1], sys.argv[2]
src = open(html, encoding="utf-8").read()
start = src.find("const SCENES")
end = src.find("];", src.find("subtitles", start))
end = src.find("\nconst ", end) if src.find("\nconst ", end) > 0 else len(src)
block = src[start:end]
if start < 0:
    sys.exit("Geen 'const SCENES' gevonden in de pagina.")

cue_re = re.compile(r"""\[\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(['"])((?:\\.|(?!\3).)*)\3\s*\]""")
cues = []
for sub in re.finditer(r"subtitles\s*:\s*\[(.*?)\]\s*\}", block, re.S):
    for m in cue_re.finditer(sub.group(1)):
        text = re.sub(r"\\(.)", r"\1", m.group(4))
        cues.append((float(m.group(1)), float(m.group(2)), text))
cues.sort()
if not cues:
    sys.exit("Geen ondertitels gevonden (verwacht: subtitles: [[start, eind, 'tekst'], ...]).")

os.makedirs(folder, exist_ok=True)
with open(os.path.join(folder, "cues.tsv"), "w", encoding="utf-8") as f:
    f.write("#id\tstart\tend\ttext\n")
    for i, (a, b, t) in enumerate(cues, 1):
        f.write(f"c{i:02d}\t{a:g}\t{b:g}\t{t}\n")
with open(os.path.join(folder, "script-cues.txt"), "w", encoding="utf-8") as f:
    for i, (a, b, t) in enumerate(cues, 1):
        f.write(f"{{img:c{i:02d}}}\n{t}\n\n")
for i, (a, b, t) in enumerate(cues, 1):
    print(f"c{i:02d} {a:6.2f}-{b:6.2f}  {t}")
print(f"{len(cues)} ondertitels -> {folder}")
