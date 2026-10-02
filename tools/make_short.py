"""Maak verticale YouTube Shorts / TikToks (1080x1920) uit een stukje van een sleep documentary.

Het beeld is de 16:9-afbeelding die het hele scherm vult en langzaam van links naar rechts
(of andersom) schuift, met zachte overgangen en drijvende mist zoals in de lange video.
Grote ondertitels per zin (Pillow; de ffmpeg-build heeft geen drawtext), 432 Hz-muziek
op -13 dB (zelfde als de lange video). Met --eindtekst komt er in de laatste 3 seconden "Full sleep documentary on
the channel" (standaard uit: de eigenaar wil het simpel houden).

Gebruik:
  python3 tools/make_short.py stories/pompeii --van 509 --tot 516 --naam 1-wolk
  python3 tools/make_short.py stories/pompeii --lijst shorts.tsv [--alleen 1-wolk]
--van/--tot zijn zinsnummers (kolom # in tijdlijn-pauzes.tsv), allebei inclusief.
shorts.tsv (in de verhaalmap) heeft de kolommen naam, van, tot en weetje (plus eventueel meer).
Een weetje (--weetje) komt bovenin als "DID YOU KNOW?" + één zin die in het stukje verteld wordt.

Gesproken begin ("Did you know? ..."): zet de tekst in <map>/shorts-intro/<naam>.txt en laat
hem inspreken (kost een fractie van een cent bij xAI, dus eerst akkoord vragen):
  python3 tools/xai_voiceover.py <map>/shorts-intro/<naam>.txt --proxy-auth \
      -o <map>/shorts-intro/<naam>.mp3
Bestaan shorts-intro/<naam>.txt en .mp3 (klein, wel in git), dan begint de Short daarmee (met ondertitels) en
volgt daarna het stukje uit de lange video.

Nodig: eerst `python3 tools/add_pauses.py stories/<verhaal>` (maakt video/stem-met-pauzes.wav,
tijdlijn-pauzes.tsv en afbeeldingen-tijden-pauzes.tsv) en <map>/afbeeldingen/NNN.jpg.
Uitvoer: <map>/video/shorts/<naam>.mp4
"""
import argparse, csv, re, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from make_video import make_fog  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 25
XFADE = 1.5          # seconden overgang tussen afbeeldingen
PAN_SPEED = 28       # pixels per seconde dat het beeld opschuift
FOG_SPEED = 36       # pixels per seconde (mist, op 1920 hoog)
FOG_OPACITY = 0.4
LEAD = 0.4           # stilte voor de eerste zin
OUTRO = 3.0          # laatste seconden: verwijzing naar de lange video (--eindtekst)
INTRO_GAP = 0.8      # stilte tussen het gesproken begin en het verhaal
TAIL = 0.8           # zonder eindtekst: zoveel rust na de laatste zin
OUTRO_GAP = 0.6      # stilte tussen de laatste zin en de eindtekst
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SUB_FONT = FONT_DIR / "DejaVuSerif-Bold.ttf"
OUTRO_FONT = FONT_DIR / "DejaVuSerif.ttf"
LABEL_FONT = FONT_DIR / "DejaVuSans-Bold.ttf"
FACT_SIZE, FACT_Y = 56, 250                   # FACT_Y = bovenkant van het weetje-blok
LABEL_COLOR = (242, 204, 128, 255)            # warm goud
SUB_SIZE, SUB_MAX_W, SUB_Y = 68, 920, 1330   # SUB_Y = midden van het ondertitelblok
OUTRO_TEXT = "Full sleep documentary\non the channel"


def sec(x):
    h, m, s = x.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=font) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def text_layer(text, font_path, size, stroke, lines=None, fill=(255, 255, 255, 255)):
    """Witte tekst met donkere rand en zachte schaduw, als RGBA-plaatje (W breed)."""
    font = ImageFont.truetype(str(font_path), size)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines = lines or wrap(probe, text, font, SUB_MAX_W)
    lh = int(size * 1.28)
    h = lh * len(lines) + 2 * stroke + 40
    shadow = Image.new("L", (W, h), 0)
    sd, img = ImageDraw.Draw(shadow), Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        y = 20 + stroke + i * lh
        sd.text((W / 2, y + 4), line, font=font, anchor="ma", fill=200,
                stroke_width=stroke + 6, stroke_fill=200)
        d.text((W / 2, y), line, font=font, anchor="ma", fill=fill,
               stroke_width=stroke, stroke_fill=(18, 14, 12, 255))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    out.putalpha(shadow.point(lambda v: int(v * 0.55)))
    out = Image.alpha_composite(out, img)
    a = np.asarray(out).astype(np.float32) / 255
    return a[..., :3], a[..., 3:]


def ramp(t, a, b, fade):
    """0..1: fadet in vanaf a en uit tot b."""
    return float(np.clip(min(t - a, b - t) / fade, 0, 1))


class Pan:
    """Een 16:9-afbeelding, schermvullend (1920 hoog), die langzaam opzij schuift."""

    def __init__(self, path, t_in, t_out, direction):
        img = Image.open(path).convert("RGB")
        scale = H / img.height
        self.img = img.resize((max(W, round(img.width * scale)), H), Image.LANCZOS)
        span = self.img.width - W
        travel = min(span, PAN_SPEED * (t_out - t_in))
        x0 = (span - travel) / 2
        self.x_from, self.x_to = (x0, x0 + travel) if direction > 0 else (x0 + travel, x0)
        self.t_in, self.t_out = t_in, t_out

    def frame(self, t):
        p = np.clip((t - self.t_in) / max(self.t_out - self.t_in, 1e-6), 0, 1)
        p = p * p * (3 - 2 * p) * 0.3 + p * 0.7   # heel licht afgeronde start en eind
        x = self.x_from + (self.x_to - self.x_from) * p
        f = self.img.transform((W, H), Image.AFFINE, (1, 0, x, 0, 1, 0), Image.BILINEAR)
        return np.asarray(f).astype(np.float32) / 255


ENV_RATE = 100      # omhullende van de stem: 100 waarden per seconde
CHUNK_WORDS = 9     # ondertitels in stukjes van hooguit zoveel woorden
# knip liefst vóór deze woorden, en nooit direct na een lidwoord of voorzetsel
SPLIT_BEFORE = {"and", "but", "or", "in", "on", "at", "with", "of", "to", "from", "for", "into", "who",
                "which", "that", "as", "when", "while", "because", "so", "then", "where", "until", "had", "was",
                "above", "below", "over", "under", "across", "through", "after", "before", "behind", "toward", "towards"}
NO_END = {"the", "a", "an", "of", "in", "on", "at", "to", "for", "from", "with", "into", "and", "his", "her", "their", "its", "my"}


def envelope(audio, start=0.0, dur=None):
    """Geluidssterkte van (een stuk van) een audiobestand, ENV_RATE waarden per seconde."""
    args = [FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}"]
    if dur:
        args += ["-t", f"{dur:.3f}"]
    pcm = subprocess.run([*args, "-i", str(audio), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.abs(np.frombuffer(pcm, dtype="<i2").astype(np.float32))
    n = len(x) // (8000 // ENV_RATE)
    return x[:n * (8000 // ENV_RATE)].reshape(n, -1).mean(1)


def gaps(env, s, e, min_len=0.12):
    """Stiltes (midden, lengte) binnen [s, e] seconden."""
    a, b = max(int(s * ENV_RATE), 0), min(int(e * ENV_RATE), len(env))
    seg = env[a:b]
    if len(seg) < 5:
        return []
    quiet = seg < 0.12 * np.percentile(seg, 90)
    out, k = [], 0
    while k < len(seg):
        if quiet[k]:
            m = k
            while m < len(seg) and quiet[m]:
                m += 1
            if k > 0 and m < len(seg) and (m - k) / ENV_RATE >= min_len:
                out.append(((a + (k + m) / 2) / ENV_RATE, (m - k) / ENV_RATE))
            k = m
        else:
            k += 1
    return out


def chunks(text):
    """Knip een zin in korte ondertitelstukjes: eerst bij komma's e.d., lange stukken in gelijke delen."""
    parts = [p.strip() for p in re.split(r"(?<=[,;:\u2014\u2013])\s+", text.strip()) if p.strip()]
    out = []
    for p in parts:
        w = p.split()
        n = max(1, -(-len(w) // CHUNK_WORDS))
        start = 0
        for c in range(n - 1, 0, -1):      # nog c knippen te gaan
            ideal = start + (len(w) - start) / (c + 1)
            best = min(range(start + 2, len(w) - 1), key=lambda k: abs(k - ideal)
                       + (0 if w[k].lower() in SPLIT_BEFORE else 1.5)
                       + (3 if w[k - 1].lower() in NO_END else 0), default=None)
            if best is None:
                break
            out.append(" ".join(w[start:best]))
            start = best
        out.append(" ".join(w[start:]))
    # geen losse stukjes van één woord: plak aan het vorige
    merged = []
    for c in out:
        if merged and len(c.split()) == 1 and len(merged[-1].split()) < CHUNK_WORDS + 2:
            merged[-1] += " " + c
        else:
            merged.append(c)
    return merged


def syllables(word):
    """Ruwe schatting van het aantal lettergrepen (voor de spreektijd van een woord)."""
    w = word.lower()
    digits = sum(ch.isdigit() for ch in w)
    groups = len(re.findall(r"[aeiouy]+", re.sub(r"[^a-z]", "", w)))
    if w.rstrip(".,;:!?'\u2019\u201d").endswith("e") and groups > 1:
        groups -= 1                      # stomme e (make, stone)
    return max(1, groups) + 0.6 * digits


def voiced_onset(env, t, before=0.3, after=0.5):
    """Moment waarop de stem rond t begint (de tijdlijn kan ± 0,2 s afwijken): het eerste
    luide stukje in [t - before, t + after] dat na minstens 0,1 s stilte komt."""
    a, b = max(int((t - before) * ENV_RATE), 0), min(int((t + after) * ENV_RATE), len(env))
    thr = 0.12 * np.percentile(env, 90)
    q = int(0.1 * ENV_RATE)
    for k in range(a, b):
        if env[k] > thr and (k < q or (env[k - q:k] <= thr).all()):
            return k / ENV_RATE
    return t


def align(env, s, e, pieces):
    """Tijden voor de ondertitelstukjes van één zin.
    De lettergrepen worden verdeeld over de tijd dat er echt gesproken wordt (stiltes tellen
    niet mee), zo komt elke grens op de juiste plek. Eindigt een stukje met een komma, dan
    valt de grens op de stilte die daar het best bij past; de nieuwe tekst verschijnt vlak
    voordat de stem weer begint."""
    s = voiced_onset(env, s)
    if len(pieces) == 1:
        return [(s, e, pieces[0])]
    a, b = int(s * ENV_RATE), max(int(e * ENV_RATE), int(s * ENV_RATE) + 1)
    seg = env[a:b]
    thr = 0.12 * np.percentile(seg, 90) if len(seg) > 4 else 0
    voiced = np.cumsum(seg > thr)
    total = max(voiced[-1], 1)
    syl = [sum(syllables(w) for w in p.split()) for p in pieces]
    frac = np.cumsum(syl)[:-1] / sum(syl)
    cand = gaps(env, s, e)
    cuts, last = [], s
    for k, f in enumerate(frac):
        # moment waarop dit deel van de spreektijd voorbij is
        idx = int(np.searchsorted(voiced, f * total))
        t = (a + min(idx, len(seg) - 1)) / ENV_RATE
        comma = pieces[k].rstrip()[-1:] in ",;:\u2014\u2013"
        best = None
        for m, ln in cand:
            if m <= last + 0.3:
                continue
            gi = int(m * ENV_RATE) - a
            gf = voiced[min(max(gi, 0), len(voiced) - 1)] / total
            if comma:
                # na een komma zegt de stem [pause]: dat is een lange stilte (>= 0,35 s)
                ok = ln >= 0.35 and abs(gf - f) < 0.25
                score = abs(gf - f)
            else:
                ok = abs(m - t) < 0.3 or (ln >= 0.25 and abs(m - t) < 0.6)
                score = abs(m - t) - 0.5 * ln
            if ok and (best is None or score < best[0]):
                best = (score, m, ln)
        if best is None and comma:          # geen lange stilte gevonden: dichtstbijzijnde kleine
            for m, ln in cand:
                if m > last + 0.3 and abs(m - t) < 0.4 and (best is None or abs(m - t) < best[0]):
                    best = (abs(m - t), m, ln)
        if best:
            c = max(best[1], best[1] + best[2] / 2 - 0.15)   # vlak voor de stem weer begint
        else:
            c = t - 0.05
        c = max(c, last + 0.3)
        cuts.append(c)
        last = c
    bounds = [s] + cuts + [e]
    return [(bounds[k], bounds[k + 1], p) for k, p in enumerate(pieces)]


# ---- woord-voor-woord uitlijnen (pocketsphinx, gratis en offline) ----
_DEC = None
STATS = {"exact": 0, "geschat": 0}   # hoeveel zinnen woord voor woord gelukt zijn
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _num_words(n):
    """Getal als Engelse woorden (jaartallen zoals ze uitgesproken worden)."""
    if n < 20:
        return [ONES[n]]
    if n < 100:
        return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    if 1100 <= n < 2000 or 2010 <= n < 2100:          # 1912 -> nineteen twelve
        hi, lo = divmod(n, 100)
        return _num_words(hi) + (["hundred"] if lo == 0 else ["oh", ONES[lo]] if lo < 10 else _num_words(lo))
    if n < 1000:
        h, r = divmod(n, 100)
        return [ONES[h], "hundred"] + (_num_words(r) if r else [])
    t, r = divmod(n, 1000)
    return _num_words(t) + ["thousand"] + (_num_words(r) if r else [])


def _decoder():
    global _DEC
    if _DEC is None:
        try:
            from pocketsphinx import Decoder
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pocketsphinx"], check=True)
            from pocketsphinx import Decoder
        _DEC = Decoder(samprate=16000, loglevel="FATAL")
    return _DEC


def word_starts(audio, s, e, text):
    """Begintijd (s, in het audiobestand) van elk woord van text (text.split()), gevonden door
    de tekst op de stem te leggen. Woorden die het woordenboek niet kent krijgen een tijd
    tussen hun buren in. None als het uitlijnen mislukt."""
    dec = _decoder()
    words = text.split()
    toks = []                       # per zichtbaar woord: de woorden zoals ze gesproken worden
    for w in words:
        parts = []
        for piece in re.split(r"[-\u2013\u2014/]", w.lower()):
            core = re.sub(r"[^a-z0-9']", "", piece.replace("\u2019", "'")).strip("'")
            if core.isdigit():
                parts += _num_words(int(core)) if int(core) < 10000 else []
            elif core:
                parts.append(core)
        toks.append([t for t in parts if dec.lookup_word(t)])
    flat = [t for ts in toks for t in ts]
    if not flat:
        return None
    pad = 0.3
    raw = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{max(s - pad, 0):.3f}",
                          "-t", f"{e - s + 2 * pad:.3f}", "-i", str(audio), "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    try:
        dec.set_align_text(" ".join(flat))
        dec.start_utt(); dec.process_raw(raw, full_utt=True); dec.end_utt()
        segs = [(re.sub(r"\(\d+\)$", "", g.word), g.start_frame / 100) for g in dec.seg()
                if g.word not in ("<s>", "</s>", "<sil>", "(NULL)", "[NOISE]")]
    except Exception:
        return None
    if len(segs) != len(flat):
        return None
    base, k, starts = max(s - pad, 0), 0, []
    for ts in toks:
        starts.append(base + segs[k][1] if ts else None)
        k += len(ts)
    # onbekende woorden: tussen de buren in
    known = [i for i, t in enumerate(starts) if t is not None]
    for i, t in enumerate(starts):
        if t is None:
            lo = max((j for j in known if j < i), default=None)
            hi = min((j for j in known if j > i), default=None)
            if lo is not None and hi is not None:
                starts[i] = starts[lo] + (starts[hi] - starts[lo]) * (i - lo) / (hi - lo)
            elif lo is not None:
                starts[i] = starts[lo] + 0.3 * (i - lo)
            elif hi is not None:
                starts[i] = max(s, starts[hi] - 0.3 * (hi - i))
    return starts


def timed_chunks_rel(audio, env, t0, s, e, text):
    """Zoals timed_chunks, maar env begint op t0 in het audiobestand; tijden relatief aan t0."""
    pieces = chunks(text)
    starts = word_starts(audio, s, e, text)
    STATS["exact" if starts is not None else "geschat"] += 1
    if starts is None:
        return align(env, s - t0, e - t0, pieces)
    res, w = [], 0
    marks = []
    for p in pieces:
        marks.append((starts[w] - t0, p))
        w += len(p.split())
    for k, (t, p) in enumerate(marks):
        nxt = marks[k + 1][0] if k + 1 < len(marks) else e - t0
        res.append((t, max(nxt, t + 0.3), p))
    return res


def timed_chunks(audio, env, s, e, text):
    """Ondertitelstukjes van één zin met hun tijden: woord voor woord uitgelijnd;
    lukt dat niet, dan de schatting op de stiltes (align)."""
    pieces = chunks(text)
    starts = word_starts(audio, s, e, text)
    if starts is None:
        return align(env, s, e, pieces)
    out, w = [], 0
    for p in pieces:
        out.append([starts[w], p])
        w += len(p.split())
    res = []
    for k, (t, p) in enumerate(out):
        nxt = out[k + 1][0] if k + 1 < len(out) else e
        res.append((t, max(nxt, t + 0.3), p))
    return res


def intro_parts(audio, text):
    """Lengte van het gesproken begin en de ondertitels. De [pause]-stukken ("Did you know?",
    de zin over het onderwerp, het weetje) vallen op de langste stiltes; lange stukken
    worden daarbinnen in kortere ondertitels geknipt."""
    env = envelope(audio)
    dur = len(env) / ENV_RATE
    pieces = [p.strip() for p in text.replace("[long pause]", "[pause]").split("[pause]") if p.strip()]
    # eerst: de hele tekst woord voor woord op de stem leggen
    starts = word_starts(audio, 0.0, dur, " ".join(pieces))
    if starts is not None:
        marks, w = [], 0
        for p in pieces:
            for c in chunks(p):
                marks.append((starts[w], c))
                w += len(c.split())
        subs = [(t, max(marks[k + 1][0] if k + 1 < len(marks) else dur, t + 0.3), c)
                for k, (t, c) in enumerate(marks)]
        return dur, subs
    g = sorted(gaps(env, 0, dur, 0.2), key=lambda x: -x[1])[:len(pieces) - 1]
    cuts = sorted(m for m, _ in g)
    if len(cuts) < len(pieces) - 1:     # te weinig stiltes gevonden: evenredig verdelen
        lens = np.array([len(p) for p in pieces], float)
        cuts = list(dur * np.cumsum(lens)[:-1] / lens.sum())
    # elk stuk begint waar de stem na de pauze weer begint
    starts = [voiced_onset(env, c, before=0.0, after=1.5) for c in cuts]
    bounds = [0.0] + starts + [dur]
    subs = []
    for k, p in enumerate(pieces):
        subs += timed_chunks(audio, env, bounds[k], bounds[k + 1], p)
    return dur, subs


def make_short(story, van, tot, naam, seed, weetje="", eindtekst=False):
    tl = {int(r[0]): r for r in (l.split("\t") for l in
          open(story / "tijdlijn-pauzes.tsv").read().splitlines()[1:] if l.strip())}
    sents = [(sec(tl[i][1]), sec(tl[i][2]), tl[i][4].strip()) for i in range(van, tot + 1)]
    t0 = sents[0][0] - LEAD
    intro_audio = story / "shorts-intro" / f"{naam}.mp3"
    intro_txt = story / "shorts-intro" / f"{naam}.txt"
    intro_subs, off = [], 0.0
    if intro_audio.exists() and intro_txt.exists():
        intro_len, intro_subs = intro_parts(intro_audio, intro_txt.read_text())
        off = LEAD + intro_len + INTRO_GAP
        intro_subs = [(a + LEAD, b + LEAD, txt) for a, b, txt in intro_subs]
    base = t0 - off   # tijd in de lange video die bij 0 s in de Short hoort
    speech_end = sents[-1][1] - base
    outro_at = speech_end + OUTRO_GAP
    total = outro_at + (OUTRO if eindtekst else TAIL)
    print(f"{naam}: zinnen {van}-{tot}, {total:.1f} s", flush=True)
    if not 40 <= total <= 62:
        print(f"  let op: {total:.1f} s valt buiten 45-60 s")

    # afbeeldingen die in dit stuk vallen (tijden relatief aan t0)
    imgs = list(csv.DictReader(open(story / "afbeeldingen-tijden-pauzes.tsv"), delimiter="\t"))
    pans = []
    for i, r in enumerate(imgs):
        s, e = float(r["start"]) - base, float(r["end"]) - base
        if e + XFADE <= 0 or s >= total:
            continue
        t_in, t_out = max(s, 0), min(e + XFADE, total)
        direction = 1 if (int(Path(r["file"]).stem) + len(pans)) % 2 else -1
        pans.append((max(s, 0), Pan(story / "afbeeldingen" / r["file"], t_in, t_out, direction)))

    # mist (zelfde textuur als de lange video), geschaald naar 1920 hoog
    fog_png = story / "video" / "mist.png"
    if not fog_png.exists():
        make_fog(fog_png)
    fog_img = Image.open(fog_png).convert("L")
    fog_img = fog_img.resize((round(fog_img.width * H / fog_img.height), H), Image.BILINEAR)
    fog = np.asarray(fog_img).astype(np.float32)[..., None] / 255 * np.array([1, 0.97, 0.92], np.float32)
    fog_period = 7680 * H / 1080

    # ondertitels: korte stukjes die op de stiltes in de stem wisselen
    env = envelope(story / "video" / "stem-met-pauzes.wav", t0, sents[-1][1] - t0 + 0.5)
    timed = list(intro_subs)
    stem = story / "video" / "stem-met-pauzes.wav"
    for s, e, text in sents:
        timed += [(a - base, b - base, c) for a, b, c in
                  ((a + t0, b + t0, c) for a, b, c in timed_chunks_rel(stem, env, t0, s, e, text))]
    subs = []
    for k, (s, e, text) in enumerate(timed):
        a = s - 0.05
        nxt = timed[k + 1][0] if k + 1 < len(timed) else outro_at + 0.15
        b = nxt - 0.05 if nxt - e < 0.25 else min(e + 0.4, nxt - 0.15)
        rgb, alpha = text_layer(text, SUB_FONT, SUB_SIZE, 6)
        subs.append((a, b, rgb, alpha, SUB_Y - rgb.shape[0] // 2))
    o_rgb, o_alpha = text_layer("", OUTRO_FONT, 62, 5, lines=OUTRO_TEXT.split("\n"))
    o_y = H // 2 - o_rgb.shape[0] // 2
    facts = []
    if weetje:
        l_rgb, l_alpha = text_layer("", LABEL_FONT, 44, 5, lines=["DID YOU KNOW?"], fill=LABEL_COLOR)
        f_rgb, f_alpha = text_layer(weetje, SUB_FONT, FACT_SIZE, 6)
        facts = [(l_rgb, l_alpha, FACT_Y), (f_rgb, f_alpha, FACT_Y + l_rgb.shape[0] - 30)]

    # audio: stem-stuk + muziek
    out_dir = story / "video" / "shorts"
    out_dir.mkdir(parents=True, exist_ok=True)
    music = out_dir / f"{naam}-muziek.wav"
    subprocess.run([sys.executable, str(Path(__file__).parent / "ambient_432.py"), str(music),
                    "--duur", f"{total + 2:.1f}", "--seed", str(seed)], check=True)
    voice_len = speech_end - off + 0.3
    final = out_dir / f"{naam}.mp4"
    graph = (f"[1:a]atrim=start={t0:.3f}:duration={voice_len:.3f},asetpts=PTS-STARTPTS,"
             f"afade=t=in:d=0.05,afade=t=out:st={voice_len - 0.3:.3f}:d=0.3,"
             f"aformat=sample_rates=44100:channel_layouts=stereo,"
             f"adelay={off * 1000:.0f}:all=1,apad[v];"
             f"[2:a]volume=-13dB[m];")
    extra = []
    if intro_subs:
        extra = ["-i", str(intro_audio)]
        graph += (f"[3:a]aformat=sample_rates=44100:channel_layouts=stereo,"
                  f"adelay={LEAD * 1000:.0f}:all=1,apad[i];[v][i]amix=inputs=2:normalize=0[v2];")
    graph += (f"[{'v2' if intro_subs else 'v'}][m]amix=inputs=2:duration=shortest:normalize=0,"
              f"alimiter=limit=0.9,afade=t=out:st={total - 1.5:.3f}:d=1.5[a]")
    enc = subprocess.Popen(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", str(story / "video" / "stem-met-pauzes.wav"), "-i", str(music), *extra,
         "-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(final)],
        stdin=subprocess.PIPE)

    n_frames = int(round(total * FPS))
    for f in range(n_frames):
        t = f / FPS
        # beeld: nieuwste afbeelding fadet over de vorige heen
        active = [(s, p) for s, p in pans if p.t_in <= t < p.t_out + 1e-6] or [pans[-1]]
        frame = active[0][1].frame(t)
        for s, p in active[1:]:
            w = np.clip((t - s) / XFADE, 0, 1) if s > 0 else 1.0
            frame = frame * (1 - w) + p.frame(t) * w if w < 1 else p.frame(t)
        # mist (screen-blend)
        x = int(t * FOG_SPEED) % int(fog_period)
        fg = fog[:, x:x + W]
        frame = frame + ((1 - (1 - frame) * (1 - fg)) - frame) * FOG_OPACITY
        # eindtekst: beeld iets donkerder, tekst fadet in
        if eindtekst and t >= outro_at:
            k = ramp(t, outro_at, total + 10, 0.8)
            frame *= 1 - 0.35 * k
            region = frame[o_y:o_y + o_rgb.shape[0]]
            region += (o_rgb - region) * o_alpha * k
        # weetje bovenin, tot de eindtekst
        if facts:
            k = ramp(t, 0.2, outro_at if eindtekst else total + 10, 0.6)
            for rgb, alpha, y in facts:
                region = frame[y:y + rgb.shape[0]]
                region += (rgb - region) * alpha * k
        # ondertitels
        for a, b, rgb, alpha, y in subs:
            if a <= t <= b:
                k = ramp(t, a, b, 0.08)
                region = frame[y:y + rgb.shape[0]]
                region += (rgb - region) * alpha * k
        if t < 0.3:
            frame *= t / 0.3
        enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if f % (FPS * 10) == 0:
            print(f"  {t:.0f}/{total:.0f} s", flush=True)
    enc.stdin.close()
    if enc.wait():
        sys.exit("ffmpeg gaf een fout")
    music.unlink()
    print(f"klaar: {final} ({final.stat().st_size / 1e6:.1f} MB)")
    n = STATS["exact"] + STATS["geschat"]
    print(f"ondertitels: {STATS['exact']} van {n} zinnen woord voor woord gelijk met de stem"
          + ("" if not STATS["geschat"] else f" ({STATS['geschat']} geschat op de stiltes)"))
    STATS.update(exact=0, geschat=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    ap.add_argument("--van", type=int)
    ap.add_argument("--tot", type=int)
    ap.add_argument("--naam")
    ap.add_argument("--weetje", default="", help='zin bovenin onder "DID YOU KNOW?"')
    ap.add_argument("--lijst", help="tsv in de verhaalmap met kolommen naam, van, tot")
    ap.add_argument("--alleen", help="alleen deze naam uit de lijst")
    ap.add_argument("--eindtekst", action="store_true", help='"Full sleep documentary on the channel" aan het eind')
    ap.add_argument("--seed", type=int, default=7, help="muziek-zaadje")
    a = ap.parse_args()
    if a.lijst:
        rows = list(csv.DictReader(open(a.story / a.lijst), delimiter="\t"))
        for r in rows:
            if not a.alleen or r["naam"] == a.alleen:
                make_short(a.story, int(r["van"]), int(r["tot"]), r["naam"], a.seed,
                           r.get("weetje") or "", a.eindtekst)
    elif a.van and a.tot:
        make_short(a.story, a.van, a.tot, a.naam or f"short-{a.van}", a.seed, a.weetje, a.eindtekst)
    else:
        ap.error("geef --van en --tot, of --lijst")


if __name__ == "__main__":
    main()
