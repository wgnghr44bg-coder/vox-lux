"""Thumbnail stijl v3 (eigenaar 13 nov 2026, na Babylon: "denk dat de thumbnail zoals hier wel effect heeft, pas ze ook
maar toe voor de andere video's"). Zoals de grote slaapkanalen: een jonge vrouw uit die tijd rechts die de kijker
vriendelijk aankijkt en iets uit het verhaal vasthoudt, links scherp een scène uit het verhaal, warm licht; linksboven het vaste maanlogo "SLEEP ARCHIVES" en daaronder 1-2 regels
in grote dikke letters (wit + goudgeel), de linkerkant iets donkerder.

Beelden via ComfyUI (gratis, lokaal), elk 3 kandidaten; het beeldmodel keurt (niet uit die tijd, vervormd, letters)
en geeft een cijfer, de beste wint. Alleen als de videokaart vrij is (keten in de montage, die draait op de processor).

  python tools/thumbnail_v3.py --alle            # alles uit stories/thumbnails-v3.json (wacht op vrije videokaart)
  python tools/thumbnail_v3.py --alle --nu       # niet wachten
  python tools/thumbnail_v3.py --opmaak beeld.png uit.jpg "BABYLON" "600 BC"
In de keten: routine_lokaal.thumbnail() gebruikt <map>/thumbnail-v3.jpg en maakt hem anders met maak_voor_map().
"""
import datetime as dt, json, re, shutil, subprocess, sys, time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
sys.path.insert(0, str(HIER))
W, H = 1280, 720
F = "C:/Windows/Fonts/"
WIT, GOUD = (255, 255, 255), (255, 196, 70)
GPU_WERK = ["engine_stem.py", "check_stem_tekst.py", "prep_engine.sh", "herstel_zinnen.py", "beeldcheck.py",
            "comfy_batch.py", "b1_check.py", "engine_muziek.py"]


# Eigenaar 13 nov: "kijk gewoon hoe de grote kanalen ze hebben en hoe het personage is afgebeeld". Bij Sleepy Old World
# (269K) en Sleepy Quiet Historian (114K) steeds hetzelfde: een jonge vrouw uit die tijd rechts, van het middel omhoog,
# in rijke kleren van toen, kijkt de kijker vriendelijk aan en houdt iets uit het verhaal vast (brood, kruik, mand);
# links scherp het verhaal zelf (slapend gezin bij het vuur, huisje in de sneeuw met spelende kinderen); warm vuur- of
# kaarslicht tegen koele nacht of sneeuw. Soms een knipoog of vinger op de lippen ("geheimen"). Drie varianten van de
# blik; het beeldmodel kiest de sterkste.
BLIK = {
    "a": "a warm gentle smile, looking straight at the viewer",
    "b": "a soft smile with slightly raised eyebrows, as if about to share something surprising, looking at the viewer",
    "c": "one finger raised to her lips as if sharing a secret, a knowing smile at the viewer",
}


def prompt(persoon, achtergrond, licht="a small warm oil lamp", k="a", moment="", voorwerp=""):
    vast = f", holding {voorwerp}" if voorwerp else ""
    scene = f"{achtergrond}, {moment}" if moment else achtergrond
    return (f"A warm cinematic photorealistic scene. On the right third of the frame stands {persoon}, shown from the "
            f"waist up in rich detailed period clothing{vast}, {BLIK[k]}, her face softly lit by {licht}. On the left and "
            f"behind her, sharp and detailed, {scene}. Cosy warm firelight and candlelight against a cool blue evening, "
            "high detail, inviting and calm, not scary, no text, no letters")


# ---------- opmaak ----------
def opmaak(png, uit, regel1, regel2=""):
    im = Image.open(png).convert("RGB")
    w, h = im.size
    s = max(W / w, H / h)
    im = im.resize((int(w * s + 0.5), int(h * s + 0.5)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H))
    m = Image.linear_gradient("L").rotate(-90).resize((W, H)).point(lambda v: int(v * 0.45))   # links donkerder
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, m)
    d = ImageDraw.Draw(im)
    y, maat, plekken = 92, 150, []                     # onder het vaste kanaallogo
    for woord, kleur in [(regel1, WIT), (regel2, GOUD)]:
        if not woord:
            continue
        f = ImageFont.truetype(F + "impact.ttf", maat)
        while d.textlength(woord, font=f) > W * 0.52 and maat > 60:
            maat -= 4
            f = ImageFont.truetype(F + "impact.ttf", maat)
        plekken.append((woord, kleur, f, y))
        y += int(maat * 1.02)
    schaduw = Image.new("L", im.size, 0)
    ds = ImageDraw.Draw(schaduw)
    for woord, _, f, yy in plekken:
        ds.text((44, yy + 8), woord, font=f, fill=200)
    im.paste((0, 0, 0), mask=schaduw.filter(ImageFilter.GaussianBlur(10)))
    for woord, kleur, f, yy in plekken:
        d.text((40, yy), woord, font=f, fill=kleur, stroke_width=7, stroke_fill=(15, 10, 8))
    from make_thumbnail import moon_logo
    moon_logo(im, 34, 26)
    Path(uit).parent.mkdir(parents=True, exist_ok=True)
    im.save(uit, quality=92)
    return Path(uit)


# ---------- beelden ----------
def bezig(woorden):
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.CommandLine } | % { $_.CommandLine }"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    return [w for w in woorden if w in out]


def gpu_mb():
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    return int(r.stdout.strip() or 9999)


def wacht_op_videokaart():
    # alleen tijdens de lange montagestappen (uren op de processor); bij het uploaden kan de volgende video zo beginnen
    while bezig(GPU_WERK) or (bezig(["routine_lokaal.py"]) and not bezig(["make_video.py", "motion.py"])) \
            or gpu_mb() > 2500:
        time.sleep(120)


def jaar_van(regel2):
    m = re.search(r"(\d{1,4})\s*(BC|AD)?", regel2 or "")
    if not m:
        return 0
    return -int(m.group(1)) if m.group(2) == "BC" else int(m.group(1))


def kandidaten(werk, items):
    """items: [(naam, persoon, achtergrond, licht)] -> <werk>/afbeeldingen/<naam><a|b|c>.png, elk een andere blik."""
    from routine_lokaal import comfy_aan
    import beeldcheck as bc
    werk.mkdir(parents=True, exist_ok=True)
    (werk / "prompts.txt").write_text("".join(f"{n}{k}|{prompt(p, a, l, k, mo, vw)}\n" for n, p, a, l, mo, vw in items for k in "abc"), encoding="utf-8")
    bc.vlm_vrij()
    if not comfy_aan():
        raise RuntimeError("ComfyUI start niet")
    subprocess.run([sys.executable, str(HIER / "comfy" / "comfy_batch.py"), str(HIER / "comfy" / "zimage_api.json"), str(werk)],
                   cwd=REPO)
    bc.comfy_vrij()


def kies(werk, naam, item, uit):
    """Beste kandidaat die door de beeldcontrole komt, opgemaakt naar uit; None als geen enkele goed is."""
    import beeldcheck as bc
    from routine_lokaal import vlm_cijfer
    j = jaar_van(item["regel2"])
    tijd = f"{-j} BC" if j < 0 else f"the year {j}" if j else "the past"
    beste, score = None, -1
    for k in "abc":
        p = werk / "afbeeldingen" / f"{naam}{k}.png"
        if not p.exists():
            continue
        wat = f"{item['persoon']}, behind: {item['achtergrond']}"
        fout = bc.vlm(p, wat, tijd, wat, j) + bc.clip_fout(bc.clip_scores([p], j)[0])
        if fout:
            print(f"  {naam}{k}: afgekeurd ({'; '.join(fout)[:120]})", flush=True)
            continue
        kand = opmaak(p, werk / f"{naam}{k}.jpg", item["regel1"], item["regel2"])
        s = vlm_cijfer(kand)
        print(f"  {naam}{k}: cijfer {s}", flush=True)
        if s > score:
            beste, score = kand, s
    bc.vlm_vrij()
    if beste:
        shutil.copy(beste, uit)
        return Path(uit)
    return None


# ---------- YouTube ----------
def zet_op_youtube(vid, jpg):
    import youtube_upload as yu
    h = {"Authorization": "Bearer " + yu.access_token()}
    v = requests.get("https://www.googleapis.com/youtube/v3/videos", params={"part": "snippet", "id": vid},
                     headers=h, timeout=60).json().get("items", [])
    if not v or v[0]["snippet"]["channelTitle"] != "Sleep Archives":
        return f"NIET gezet: {vid} niet gevonden of ander kanaal"
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set", params={"videoId": vid},
                      headers={**h, "Content-Type": "image/jpeg"}, data=Path(jpg).read_bytes(), timeout=120)
    return "op YouTube gezet" if r.status_code == 200 else f"NIET gezet ({r.status_code} {r.text[:120]})"


def huidige_video(m):
    """Video-id van een map, alleen als de video klaar is (niet als hij nog opnieuw gemaakt wordt)."""
    t = (STORIES / m / "planning.txt").read_text(encoding="utf-8", errors="replace")
    st = (re.search(r"^status\s+(.+)$", t, re.M) or [None, ""])[1]
    link = re.search(r"^link https://youtu\.be/([A-Za-z0-9_-]{11})", t, re.M)
    return link.group(1) if link and st.startswith("klaar") else ""


def log(t):
    with open(STORIES / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
        f.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} thumbnail-v3: {t}\n")


def alle(niet_wachten=False):
    lijst = json.loads((STORIES / "thumbnails-v3.json").read_text(encoding="utf-8"))["videos"]
    werk = Path.home() / "vox-lux-cache" / "thumb-v3"
    gedaan = (STORIES / "ROUTINE-LOG.md").read_text(encoding="utf-8", errors="replace")
    todo = [x for x in lijst if f"thumbnail-v3: {x['naam']}: nieuwe thumbnail" not in gedaan]
    if not todo:
        print("niets te doen")
        return
    if not niet_wachten:
        wacht_op_videokaart()
    kandidaten(werk, [(x["naam"], x["persoon"], x["achtergrond"], x.get("licht", "a small warm oil lamp"), x.get("moment", ""),
                       x.get("voorwerp", ""))
                      for x in todo])
    for x in todo:
        doel = (STORIES / x["map"] / "thumbnail-v3.jpg") if x.get("map") else (werk / f"{x['naam']}-v3.jpg")
        uit = kies(werk, x["naam"], x, doel)
        if not uit:
            log(f"{x['naam']}: geen goed beeld (alle 3 afgekeurd), oude thumbnail blijft")
            continue
        vid = x.get("id") or (huidige_video(x["map"]) if x.get("map") else "")
        uitslag = zet_op_youtube(vid, uit) if vid else "klaar voor de keten (video wordt nog gemaakt)"
        log(f"{x['naam']}: nieuwe thumbnail ({x['regel1']} {x['regel2']}) {uitslag}")
        print(x["naam"], uitslag, flush=True)


def maak_voor_map(m, regel1, regel2, persoon, achtergrond, licht="a small warm oil lamp", moment="", voorwerp=""):
    """Voor de keten: één thumbnail-v3 voor een nieuwe video."""
    werk = m / "thumb3"
    item = {"regel1": regel1, "regel2": regel2, "persoon": persoon, "achtergrond": achtergrond}
    kandidaten(werk, [("t", persoon, achtergrond, licht, moment, voorwerp)])
    return kies(werk, "t", item, m / "thumbnail-v3.jpg")


if __name__ == "__main__":
    if "--opmaak" in sys.argv:
        i = sys.argv.index("--opmaak")
        print(opmaak(*sys.argv[i + 1:i + 5]))
    elif "--alle" in sys.argv:
        alle("--nu" in sys.argv)
