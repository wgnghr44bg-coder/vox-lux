#!/usr/bin/env python3
"""VIDEO PRE-PUBLICATION QC CHECKER (eigenaar, okt 2026; volledige lijst: stories/QC-CHECKLIST.md).

Strenge controle van een lange video vóór de upload. Meet alles wat technisch te meten is en
schrijft het rapport in het afgesproken formaat. Wat niet automatisch kan (beeldkwaliteit van
de AI-beelden, historische juistheid, spelling van de teksten in beeld, kijkervaring) moet de
sessie ZELF beoordelen: bekijk de overzichtsplaten die dit script maakt (alle afbeeldingen,
beelden uit de eindvideo) en de lijst met teksten, en geef het oordeel mee:
    --beelden "ok" | "fout: <tijd> <wat>"     (2.4 beeldkwaliteit + 6 historisch: kleding, gebouwen, techniek)
    --teksten "ok" | "fout: ..."              (3.2 spelling, namen, datums in titels/kaartjes/kaart)
    --historisch "ok" | "fout: ..."           (6 jaartallen/namen/plaatsen in verhaal en beeld)
    --kijker "ok" | "fout: ..."               (9 kijkervaring)
Zonder een van deze oordelen is de uitslag ⚠️ NOT VERIFIED (dus niet uploaden).

Gebruik:
    python3 tools/qc_video.py stories/<map> video/<naam>-motion.mp4 \\
        --titel "<titel>" --thumbnail stories/<map>/thumbnail-v2.jpg --beschrijving desc.txt \\
        [--muziek-db -20] [--beelden ok --teksten ok --historisch ok --kijker ok]
Exitcode 0 alleen bij ✅ APPROVED. Rapport ook in video/QC-RAPPORT.txt.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

FF = imageio_ffmpeg.get_ffmpeg_exe()
OK, FOUT, NV = "✅", "❌", "⚠️"
DUUR = {"hoofdstuk": 7.0, "datum": 8.0, "kaart": 16.0, "tijdlijn": 9.0, "citaat": 12.0}
PLACEHOLDER = re.compile(r"\[(TITLE|DATE|IMAGE|INSERT|TODO|TBD|PLACEHOLDER|NAME)[^\]]*\]|\{img:|TODO|XXX|lorem ipsum", re.I)


def ts(t):
    t = max(0, int(t))
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def sec(x):
    h, m, s = x.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def pcm(args, sr):
    r = subprocess.run([FF, "-v", "error", *args, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, "<i2").astype(np.float32)


class QC:
    def __init__(self):
        self.res, self.errors = {}, []

    def set(self, key, status, *errs):
        """errs: (tijd, categorie, probleem, ernst, actie)"""
        if self.res.get(key) in (FOUT,):
            status = FOUT if status != FOUT else status
        self.res[key] = status if self.res.get(key) != FOUT else FOUT
        self.errors += list(errs)


def segmenten(e, drempel):
    s = e > drempel
    out, k = [], 0
    while k < len(s):
        if s[k]:
            m = k
            while m < len(s) and s[m]:
                m += 1
            out.append((k, m))
            k = m
        else:
            k += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    ap.add_argument("video")
    ap.add_argument("--titel", required=True)
    ap.add_argument("--thumbnail", type=Path, required=True)
    ap.add_argument("--beschrijving", type=Path, required=True)
    ap.add_argument("--muziek-db", type=float, default=-20)
    for k in ("beelden", "teksten", "historisch", "kijker"):
        ap.add_argument(f"--{k}")
    a = ap.parse_args()
    st = a.story
    f = Path(a.video) if Path(a.video).exists() else st / a.video
    stem, muziek = st / "video" / "stem-met-pauzes.wav", st / "video" / "muziek432.wav"
    qc = QC()
    out_dir = st / "video" / "qc"
    out_dir.mkdir(exist_ok=True)

    # ---------- technisch ----------
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)],
                                   capture_output=True, text=True).stdout or "{}")
    vs = [s for s in pr.get("streams", []) if s["codec_type"] == "video"]
    au = [s for s in pr.get("streams", []) if s["codec_type"] == "audio"]
    dur = float(pr.get("format", {}).get("duration", 0))
    tech = []
    if not vs or (vs[0]["width"], vs[0]["height"]) != (1920, 1080):
        tech.append("resolutie is geen 1920x1080 (16:9)")
    if vs and vs[0].get("r_frame_rate") not in ("25/1", "30/1"):
        tech.append(f"framerate {vs[0].get('r_frame_rate')}")
    if not au:
        tech.append("geen geluidsspoor")
    qc.set("tech", FOUT if tech else OK, *[(0, "TECHNICAL", t, "CRITICAL", "Opnieuw renderen.") for t in tech])

    # ---------- 1. geluid ----------
    sr = 16000
    x = pcm(["-i", str(stem)], sr)
    hop = sr // 100
    n = len(x) // hop
    e = np.abs(x[:n * hop]).reshape(n, hop).mean(1)
    loud = np.percentile(e, 90)
    segs = segmenten(e, 0.03 * loud)
    blips = [segs[i][0] / 100 for i in range(1, len(segs) - 1)
             if segs[i][1] - segs[i][0] <= 20 and segs[i][0] - segs[i - 1][1] >= 35 and segs[i + 1][0] - segs[i][1] >= 35]
    if len(blips) > 2:
        qc.set("continuity", FOUT, *[(t, "AUDIO", "Los kort geluidje tussen twee stiltes: stem blijft hangen / pauze midden in een woord.",
                                      "HIGH", "add_pauses.py opnieuw (pauzes in echte stiltes) en opnieuw renderen.") for t in blips])
    else:
        qc.set("continuity", OK)
    # onnatuurlijke gaten in de stem (behalve begin en eind)
    gaps = [(segs[i][1] / 100, (segs[i + 1][0] - segs[i][1]) / 100) for i in range(len(segs) - 1)
            if (segs[i + 1][0] - segs[i][1]) / 100 > 6.0]
    qc.set("pauses", FOUT if gaps or len(blips) > 2 else OK,
           *[(t, "AUDIO", f"Onnatuurlijk lange stilte van {g:.1f} s in de vertelling.", "MEDIUM", "Pauzes nakijken.") for t, g in gaps])

    # artefacten: decodeerfouten en vervorming
    art = []
    for p in (stem, f):
        err = subprocess.run([FF, "-v", "error", "-i", str(p), "-f", "null", "-"], capture_output=True, text=True).stderr.strip()
        if err:
            art.append((0, "AUDIO", f"Decodeerfouten in {p.name}: {err.splitlines()[0]}", "CRITICAL", "Stem in één stuk opnieuw maken."))
        y = pcm(["-i", str(p)], 22050)
        c = np.where(np.abs(y) >= 32000)[0]
        if len(c) > 10:
            art.append((c[0] / 22050, "AUDIO", f"Vervorming/clipping in {p.name} ({len(c)} samples).", "HIGH", "Volume omlaag en opnieuw renderen."))
    # plotselinge volumesprongen in de stem (per seconde, alleen tijdens spraak)
    sec_rms = np.sqrt((x[:len(x) // sr * sr].reshape(-1, sr) ** 2).mean(1))
    spraak = sec_rms > 0.1 * np.percentile(sec_rms, 90)
    med = np.median(sec_rms[spraak])
    for i in np.where(spraak & (sec_rms > 3.5 * med))[0][:10]:
        art.append((i, "AUDIO", "Plotselinge volumepiek in de stem.", "MEDIUM", "Stuk nakijken/opnieuw maken."))
    qc.set("artifacts", FOUT if art else OK, *art)

    # stotteren: geluid van de video tegen de bron
    got = pcm(["-i", str(f)], 8000)
    ref_args = ["-i", str(stem)]
    if muziek.exists():
        ref_args = ["-i", str(stem), "-i", str(muziek), "-filter_complex",
                    f"[1]volume={a.muziek_db}dB[m];[0][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9"]
    ref = pcm(ref_args, 8000)
    best = max(range(-400, 400), key=lambda k: float(np.dot(got[8000 + k:248000 + k], ref[8000:248000])))
    got = got[best:] if best >= 0 else np.concatenate([np.zeros(-best, np.float32), got])
    m_ = min(len(got), len(ref))
    bad = []
    for i in range(0, m_ - 4000, 4000):
        u, v = got[i:i + 4000], ref[i:i + 4000]
        if np.sqrt((v ** 2).mean()) < 300:
            continue
        cc = float(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9))
        if cc < 0.8:
            bad.append(i / 8000)
    qc.set("stutter", FOUT if bad else OK, *[(t, "AUDIO", "Geluid van de video wijkt af van de bron (hapering, herhaling of gat).",
                                              "HIGH", "Video opnieuw renderen.") for t in bad[:20]])

    # stemconsistentie per 5 minuten: volume, klankkleur, spreektempo
    blok = 300
    rms5, cen5 = [], []
    for i in range(0, len(x) // sr - blok, blok):
        b = x[i * sr:(i + blok) * sr]
        s1 = sec_rms[i:i + blok] > 0.1 * np.percentile(sec_rms, 90)
        b2 = b.reshape(-1, sr)[s1]
        if len(b2) < 30:
            continue
        rms5.append(20 * np.log10(np.sqrt((b2 ** 2).mean()) + 1))
        X = np.abs(np.fft.rfft(b2[:60].ravel()))
        fr = np.fft.rfftfreq(len(b2[:60].ravel()), 1 / sr)
        cen5.append(float((X * fr).sum() / (X.sum() + 1e-9)))
    cons = []
    if rms5 and max(rms5) - min(rms5) > 4:
        i = int(np.argmax(np.abs(np.array(rms5) - np.median(rms5))))
        cons.append((i * blok, "AUDIO", f"Stemvolume wijkt {max(rms5) - min(rms5):.1f} dB af tussen delen.", "MEDIUM", "Nakijken."))
    if cen5 and (max(cen5) - min(cen5)) / np.median(cen5) > 0.25:
        i = int(np.argmax(np.abs(np.array(cen5) - np.median(cen5))))
        cons.append((i * blok, "AUDIO", "Klankkleur van de stem verandert duidelijk (andere opname?).", "MEDIUM", "Nakijken."))
    rows = [l.split("\t") for l in (st / "tijdlijn-pauzes.tsv").read_text().splitlines()[1:] if l.strip()]
    tempo = {}
    for r in rows:
        d = sec(r[2]) - sec(r[1])
        if d > 1 and len(r[4].split()) >= 4:
            tempo.setdefault(int(sec(r[1]) // blok), []).append(len(r[4].split()) / d)
    tm = [np.median(v) for v in tempo.values() if len(v) > 10]
    if tm and (max(tm) - min(tm)) / np.median(tm) > 0.2:
        cons.append((0, "AUDIO", "Spreektempo verschilt meer dan 20% tussen delen.", "MEDIUM", "Nakijken."))
    qc.set("consistency", FOUT if cons else OK, *cons)

    # muziek: geen pieken, nooit boven de stem
    mus = []
    if muziek.exists():
        mm = pcm(["-i", str(muziek)], 8000)
        r1 = np.sqrt((mm[:len(mm) // 8000 * 8000].reshape(-1, 8000) ** 2).mean(1)) * 10 ** (a.muziek_db / 20)
        vr = np.median(sec_rms[spraak])
        # piek = muziek springt omhoog ÉN komt dan in de buurt van de stem (binnen ± 16 dB);
        # een zachte melodie die begint ver onder de stem is geen piek
        for i in np.where((r1[1:] > 2.5 * r1[:-1]) & (r1[1:] > 0.16 * vr))[0][:5]:
            mus.append((i + 1, "AUDIO", "Plotselinge piek in de achtergrondmuziek.", "MEDIUM", "Muziek opnieuw maken."))
        if np.percentile(r1, 99) > 0.5 * vr:
            mus.append((int(np.argmax(r1)), "AUDIO", "Muziek komt te dicht bij het stemvolume.", "MEDIUM", "Muziek zachter."))
        qc.set("music", FOUT if mus else OK, *mus)
    else:
        qc.set("music", NV)

    # ---------- 2. beeld ----------
    raw = subprocess.run([FF, "-v", "error", "-i", str(f), "-vf", "fps=2,scale=64:36,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 64 * 36).astype(np.float32)
    lum = fr.mean(1)
    d = np.abs(np.diff(fr, axis=0)).mean(1)
    vast, run = [], 0
    for i, v in enumerate(d):
        run = run + 1 if v < 0.05 else 0
        if run == 17:
            vast.append(i / 2)
    qc.set("frozen", FOUT if vast else OK, *[(t, "VIDEO", "Beeld staat langer dan 8 s stil.", "HIGH", "Beweging/clip nakijken.") for t in vast])
    zwart = [i / 2 for i in range(len(lum)) if lum[i] < 8 and 3 < i / 2 < dur - 20]
    zw = []
    for t in zwart:
        if not zw or t - zw[-1] > 2:
            zw.append(t)
    qc.set("black", FOUT if zw else OK, *[(t, "VIDEO", "Onverwacht zwart/leeg beeld.", "HIGH", "Clip/afbeelding nakijken.") for t in zw[:10]])
    flits = [i / 2 for i in range(1, len(lum) - 1) if abs(lum[i] - lum[i - 1]) > 35 and abs(lum[i + 1] - lum[i]) > 35]
    qc.set("transitions", FOUT if flits else OK, *[(t, "VIDEO", "Flits/flikkering (plotselinge helderheidssprong).", "MEDIUM", "Overgang nakijken.") for t in flits[:10]])

    # overzichtsplaten voor de eigen beoordeling
    imgs = sorted((st / "afbeeldingen").glob("*.jpg"))
    for k in range(0, len(imgs), 20):
        tiles = [Image.open(p).convert("RGB").resize((384, 216)) for p in imgs[k:k + 20]]
        sheet = Image.new("RGB", (384 * 5, 216 * ((len(tiles) + 4) // 5)))
        for j, t in enumerate(tiles):
            sheet.paste(t, (384 * (j % 5), 216 * (j // 5)))
        sheet.save(out_dir / f"afbeeldingen-{k // 20 + 1}.jpg", quality=85)
    plan = json.loads((st / "motion.json").read_text())
    momenten = [5] + [it["tijd"] + 2 for it in plan["items"]] + [dur - 8]
    for j, t in enumerate(momenten):
        subprocess.run([FF, "-v", "error", "-y", "-ss", f"{t:.1f}", "-i", str(f), "-frames:v", "1", "-vf", "scale=640:360",
                        str(out_dir / f"tekst-{j:02d}.png")])
    print(f"Bekijk zelf: {out_dir}/afbeeldingen-*.jpg (beeldkwaliteit, historisch) en tekst-*.png (teksten in beeld)")
    qc.set("image_quality", OK if a.beelden == "ok" else (FOUT if a.beelden else NV),
           *([(0, "VIDEO", a.beelden, "HIGH", "Afbeelding opnieuw maken.")] if a.beelden and a.beelden != "ok" else []))

    # ---------- 3. tekst ----------
    items = sorted(plan["items"], key=lambda i: i["tijd"])
    ov, eind = [], (9.0 + 1 if plan.get("intro") else 0)
    for it in items:
        if it["tijd"] < eind:
            ov.append((it["tijd"], "TEXT", f"{it['soort']} overlapt met het vorige onderdeel/de intro.", "HIGH", "Tijden in motion.json aanpassen."))
        eind = it["tijd"] + it.get("duur", DUUR[it["soort"]])
    qc.set("overlap", FOUT if ov else OK, *ov)
    teksten = []
    for it in items:
        for k in ("titel", "regel1", "regel2", "tekst", "bron"):
            if it.get(k):
                teksten.append((it["tijd"], it[k]))
        for p in it.get("plaatsen", []):
            teksten.append((it["tijd"], p["naam"]))
        for p in it.get("punten", []):
            teksten.append((it["tijd"], " — ".join(p)))
    teksten.append((0, plan.get("onderwerp", "")))
    print("Teksten in beeld (zelf nalezen op spelling, namen, datums):")
    for t, s in teksten:
        print(f"  {ts(t)}  {s}")
    ph = [(t, "TEXT", f"Placeholder-tekst: {s}", "CRITICAL", "Tekst invullen.") for t, s in teksten if PLACEHOLDER.search(s)]
    dub = [(t, "TEXT", f"Dubbel woord: {s}", "LOW", "Tekst verbeteren.") for t, s in teksten if re.search(r"\b(\w+) \1\b", s, re.I)]
    qc.set("placeholder", FOUT if ph else OK, *ph)
    qc.set("spelling", FOUT if dub else (OK if a.teksten == "ok" else (FOUT if a.teksten else NV)),
           *dub, *([(0, "TEXT", a.teksten, "MEDIUM", "Tekst verbeteren.")] if a.teksten and a.teksten != "ok" else []))
    kort = [(it["tijd"], "TEXT", f"{it['soort']} staat te kort in beeld.", "LOW", "Langer tonen.")
            for it in items if it.get("duur", DUUR[it["soort"]]) < 4]
    qc.set("readability", FOUT if kort else OK, *kort)   # posities/veilige marges liggen vast in motion.py

    # ---------- 4. timing ----------
    spoken = [r for r in rows if r[4].strip()]
    eerste = spoken[0][4]
    intro_ok = re.match(r"^Tonight we are going .+ years? back, to .+", eerste) and sec(spoken[0][1]) < 15
    qc.set("intro", OK if intro_ok else FOUT,
           *([] if intro_ok else [(sec(spoken[0][1]), "CONTENT", f"Begin klopt niet: '{eerste[:80]}'", "HIGH", "Eerste regel aanpassen.")]))
    slot = " ".join(r[4] for r in spoken[-8:]).lower()
    mist = [w for w, pat in (("vraag om te abonneren", r"subscrib"), ("verwijzing naar volgende video", r"another .*(story|video).*screen|next video"),
                             ("'Sleep well, and good night.'", r"sleep well, and good night")) if not re.search(pat, slot)]
    qc.set("ending", FOUT if mist else OK, *[(sec(spoken[-1][1]), "CONTENT", f"Einde mist: {w}", "HIGH", "Slot aanpassen.") for w in mist])
    laatste = sec(spoken[-1][2])
    dd = []
    if abs(len(got) / 8000 - len(ref) / 8000) > 2:
        dd.append((dur, "TIMING", f"Video {len(got) / 8000:.0f} s, geluid {len(ref) / 8000:.0f} s.", "HIGH", "Opnieuw renderen."))
    if dur - laatste > 25:
        dd.append((laatste, "TIMING", f"{dur - laatste:.0f} s stilte/beeld na het laatste woord.", "MEDIUM", "Einde inkorten."))
    qc.set("duration", FOUT if dd else OK, *dd)
    qc.set("historical", OK if a.historisch == "ok" else (FOUT if a.historisch else NV),
           *([(0, "CONTENT", a.historisch, "MEDIUM", "Verhaal/beeld verbeteren.")] if a.historisch and a.historisch != "ok" else []))

    # ---------- 7. metadata ----------
    tt = a.titel
    qc.set("title", OK if tt.endswith(" | History for Sleep") and tt.count("| History for Sleep") == 1 and len(tt) <= 100 else FOUT,
           *([] if tt.endswith(" | History for Sleep") else [(0, "YOUTUBE", f"Titel eindigt niet op '| History for Sleep': {tt}", "HIGH", "Titel aanpassen.")]))
    th = []
    if not a.thumbnail.exists():
        th.append((0, "YOUTUBE", "Thumbnail ontbreekt.", "CRITICAL", "Thumbnail maken."))
    else:
        im = Image.open(a.thumbnail)
        if a.thumbnail.stat().st_size > 2_000_000 or abs(im.width / im.height - 16 / 9) > 0.02 or im.width < 1280:
            th.append((0, "YOUTUBE", f"Thumbnail {im.width}x{im.height}, {a.thumbnail.stat().st_size // 1000} kB (moet 16:9, ≥1280 breed, <2 MB).", "HIGH", "Opnieuw opslaan."))
        im.convert("RGB").resize((640, 360)).save(out_dir / "thumbnail.jpg")
    qc.set("thumbnail", FOUT if th else OK, *th)
    desc = a.beschrijving.read_text() if a.beschrijving.exists() else ""
    de = []
    if len(desc) < 100:
        de.append((0, "YOUTUBE", "Beschrijving ontbreekt of is te kort.", "HIGH", "Beschrijving schrijven."))
    if PLACEHOLDER.search(desc):
        de.append((0, "YOUTUBE", "Placeholder-tekst in de beschrijving.", "CRITICAL", "Invullen."))
    qc.set("description", FOUT if de else OK, *de)
    hs = sorted(i["tijd"] for i in plan["items"] if i["soort"] == "hoofdstuk")
    ch = [sec(m) for m in re.findall(r"^(\d+:\d\d:\d\d) ", desc, re.M)]
    cherr = []
    if not ch or ch[0] != 0:
        cherr.append((0, "YOUTUBE", "Hoofdstukken ontbreken of beginnen niet op 0:00:00.", "HIGH", "Hoofdstukken toevoegen."))
    elif len(ch) != len(hs) or any(abs(c - h) > 3 for c, h in zip(ch[1:], hs[1:])):
        cherr.append((0, "YOUTUBE", "Hoofdstuktijden in de beschrijving passen niet bij de video.", "HIGH", "Tijden uit motion.json overnemen."))
    qc.set("chapters", FOUT if cherr else OK, *cherr)
    qc.set("viewer", OK if a.kijker == "ok" else (FOUT if a.kijker else NV),
           *([(0, "VIEWER", a.kijker, "MEDIUM", "Nakijken.")] if a.kijker and a.kijker != "ok" else []))

    # ---------- rapport ----------
    r = qc.res
    if any(v == FOUT for v in r.values()):
        status = "❌ REJECTED"
    elif any(v == NV for v in r.values()):
        status = "⚠️ NOT VERIFIED"
    else:
        status = "✅ APPROVED"
    L = ["VIDEO QC REPORT", "", f"Overall status: {status}", f"Video duration: {ts(dur)}", "",
         "🔊 Audio", f"* Voice continuity: {r['continuity']}", f"* Pauses: {r['pauses']}", f"* Audio artifacts: {r['artifacts']}",
         f"* Stuttering: {r['stutter']}", f"* Voice consistency: {r['consistency']}", f"* Music/background: {r['music']}", "",
         "🎥 Video", f"* Frozen frames: {r['frozen']}", f"* Black frames: {r['black']}", f"* Transitions: {r['transitions']}",
         f"* Image quality: {r['image_quality']}", "",
         "📝 Text", f"* Text overlap: {r['overlap']}", f"* Spelling: {r['spelling']}", f"* Readability: {r['readability']}",
         f"* Placeholder text: {r['placeholder']}", "",
         "📖 Content", f"* Introduction: {r['intro']}", f"* Ending: {r['ending']}", f"* Historical accuracy: {r['historical']}",
         f"* Audio/video duration: {r['duration']}", "",
         "📺 YouTube", f"* Title: {r['title']}", f"* Thumbnail: {r['thumbnail']}", f"* Description: {r['description']}",
         f"* Chapters: {r['chapters']}", f"* Technical settings: {r['tech']}", "",
         f"🧑 Viewer experience: {r['viewer']}", "",
         "Pas na de upload (in Studio, door de eigenaar): eindscherm, kaarten, ondertitels, copyright-meldingen.", ""]
    if qc.errors:
        L.append("ERRORS FOUND")
        for t, cat, prob, sev, act in qc.errors:
            L += ["", f"❌ {ts(t)} — {cat}", f"Problem: {prob}", f"Severity: {sev}", f"Required action: {act}"]
        L.append("")
    L.append("✅ VIDEO APPROVED — READY FOR UPLOAD" if status.startswith("✅") else
             "❌ VIDEO REJECTED — DO NOT UPLOAD" if status.startswith("❌") else "⚠️ NOT VERIFIED — DO NOT UPLOAD")
    rapport = "\n".join(L)
    (st / "video" / "QC-RAPPORT.txt").write_text(rapport)
    print(rapport)
    sys.exit(0 if status.startswith("✅") else 1)


if __name__ == "__main__":
    main()
