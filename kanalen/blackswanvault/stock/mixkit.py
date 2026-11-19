"""Mixkit-stockvideo (gratis licentie, geen vermelding verplicht; we zetten 'Video: Mixkit' in beeld).
  python stock/mixkit.py zoek "<term>" [n]        -> lijst id + titel (+ voorbeeldplaat in stock/voorbeeld/<term>.jpg)
  python stock/mixkit.py haal <id> <videomap>     -> <videomap>/echt/video/mk-<id>.mp4 (1920x1080, 25 fps, zonder geluid)
"""
import re, subprocess, sys, urllib.request, pathlib
H = pathlib.Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0 (BlackSwanVault research)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
def zoek(term, n=8):
    slug = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
    h = get(f"https://mixkit.co/free-stock-video/{slug}/").decode("utf-8", "ignore")
    uit = []
    for pad in dict.fromkeys(re.findall(r'href="/free-stock-video/([a-z0-9-]+)-(\d+)/"', h)):
        uit.append((pad[1], pad[0].replace("-", " ")))
    uit = uit[:n]; vb = H / "voorbeeld"; vb.mkdir(exist_ok=True); tegels = []
    for i, t in uit:
        u = f"https://assets.mixkit.co/videos/{i}/{i}-360.mp4"
        p = vb / f"{i}.jpg"
        if not p.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2", "-i", u, "-frames:v", "1", "-vf", "scale=480:270:force_original_aspect_ratio=increase,crop=480:270,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='" + i + "':x=8:y=8:fontsize=28:fontcolor=yellow:box=1:boxcolor=black", str(p)])
        if p.exists(): tegels.append(str(p))
        print(i, t)
    if tegels:
        args = sum([["-i", x] for x in tegels], []); k = len(tegels); cols = 4
        while len(tegels) % cols: tegels.append(tegels[-1]); args += ["-i", tegels[-1]]
        f = "".join(f"[{j}]" for j in range(len(tegels))) + f"xstack=inputs={len(tegels)}:layout=" + "|".join(f"{(j%cols)*480}_{(j//cols)*270}" for j in range(len(tegels)))
        subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", f, "-frames:v", "1", str(vb / (slug + ".jpg"))])
        print("plaat", vb / (slug + ".jpg"))
def haal(i, map_):
    uit = pathlib.Path(map_) / "echt" / "video" / f"mk-{i}.mp4"; uit.parent.mkdir(parents=True, exist_ok=True)
    for q in ("1080", "720"):
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"https://assets.mixkit.co/videos/{i}/{i}-{q}.mp4", "-an", "-vf",
                            "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25", "-c:v", "libx264", "-crf", "18", "-preset", "fast", str(uit)])
        if r.returncode == 0 and uit.exists(): print("klaar", uit, q); return
    print("MISLUKT", i)
if __name__ == "__main__":
    if sys.argv[1] == "zoek": zoek(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    else: haal(sys.argv[2], sys.argv[3])
