"""Stem lokaal maken op de pc van de eigenaar (gratis): Chatterbox met bm_george als voorbeeldstem, "rustig".
Maakt voice.mp3 + voice-times.tsv in hetzelfde formaat als make_voice.py (stem start op 0,8 s).

Vaste stem (eigenaar 13 okt 2026): chatterbox_als_bm_george_rustig (exaggeration 0.4, cfg 0.5),
voorbeeld = alteraqon/2026-10-13-donut-earth/stemtest/kokoro_bm_george.mp3.

Gebruik (stem-env actief, zie voice_test_local.py; vanuit de map vox-lux):
  python alteraqon/tools/make_voice_local.py alteraqon/<datum>-<slug> [cachemap] --pause-ms 350 --long-pause-ms 800 --sentence-pause-ms 250
(cachemap buiten de repo: na een scriptwijziging worden alleen gewijzigde zinnen opnieuw gemaakt;
 een zin opnieuw laten maken = zijn .wav in de cachemap weggooien, of een andere --seed)
Leest script-cues.txt ({img:Sxx} op een eigen regel, elke zin eindigt op [pause] of [long pause]).
--dry-run toont alleen de zinnen en pauzes (geen model nodig).
"""
import argparse, csv, hashlib, importlib.util, os, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD = 0.8
REF = HERE.parent / "2026-10-13-donut-earth" / "stemtest" / "kokoro_bm_george.mp3"

# Zinnen splitsen, stiltes, trimmen en samenvoegen precies zoals bij de xAI-stem (tools/xai_voiceover.py)
spec = importlib.util.spec_from_file_location("xv", HERE.parent.parent / "tools" / "xai_voiceover.py")
xv = sys.modules["xv"] = importlib.util.module_from_spec(spec); spec.loader.exec_module(xv)

ap = argparse.ArgumentParser()
ap.add_argument("map"); ap.add_argument("cache", nargs="?")
ap.add_argument("--pause-ms", type=int, default=350); ap.add_argument("--long-pause-ms", type=int, default=800)
ap.add_argument("--sentence-pause-ms", type=int, default=250)
ap.add_argument("--ref", default=str(REF), help="voorbeeldstem (wav/mp3)")
ap.add_argument("--exaggeration", type=float, default=0.4); ap.add_argument("--cfg", type=float, default=0.5)
ap.add_argument("--speed", type=float, default=1.0, help="tempo achteraf (ffmpeg atempo, 0.8-1.2)")
ap.add_argument("--seed", type=int, default=1); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()

xv.PAUSE_MS, xv.LONG_PAUSE_MS, xv.SENTENCE_PAUSE_MS = a.pause_ms, a.long_pause_ms, a.sentence_pause_ms
folder = Path(a.map).resolve()
text = (folder / "script-cues.txt").read_text(encoding="utf-8")
pieces = [p for p in xv.split_script(text) if xv.TAG_RE.sub("", p.text).strip()]
for i, p in enumerate(pieces, 1):
    print(f"  {i:>3}. {p.cue or '':4} {p.text[:70]!r}" + (f"  + {p.silence_after_ms} ms" if p.silence_after_ms else ""))
if a.dry_run:
    sys.exit(0)

ffmpeg = xv.find_ffmpeg()
tmp = tempfile.TemporaryDirectory()
cache = Path(a.cache).resolve() if a.cache else Path(tmp.name)
cache.mkdir(parents=True, exist_ok=True)
settings = f"chatterbox|{Path(a.ref).name}|{a.exaggeration}|{a.cfg}|{a.speed}|{a.seed}"
path = lambda p: cache / (hashlib.sha1(f"{settings}|{p.text}".encode()).hexdigest()[:16] + ".wav")
todo = [p for p in pieces if not path(p).exists()]
print(f"{len(pieces)} zinnen, {len(pieces) - len(todo)} uit de cache, {len(todo)} nieuw")

if todo:
    import torch, torchaudio as ta
    from chatterbox.tts import ChatterboxTTS
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = ChatterboxTTS.from_pretrained(device=dev)
    ref = cache / "ref.wav"                       # mp3 -> wav, zodat elke Chatterbox-versie hem leest
    subprocess.run([ffmpeg, "-v", "error", "-y", "-i", a.ref, "-ac", "1", str(ref)], check=True)
    for n, p in enumerate(todo, 1):
        torch.manual_seed(a.seed)
        say = " ".join(xv.TAG_RE.sub(" ", p.text).split())
        wav = model.generate(say, audio_prompt_path=str(ref), exaggeration=a.exaggeration, cfg_weight=a.cfg)
        raw = path(p).with_suffix(".raw.wav")
        ta.save(str(raw), wav.cpu(), model.sr)
        if a.speed != 1.0:
            subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(raw), "-af", f"atempo={a.speed}", str(path(p))], check=True)
            raw.unlink()
        else:
            raw.rename(path(p))
        print(f"  {n}/{len(todo)} klaar: {say[:60]}", flush=True)

durations = xv.join_with_silence(ffmpeg, [(path(p), p.silence_after_ms) for p in pieces],
                                 folder / "voice.mp3", trim=True, workdir=cache)
t = 0.0
with open(folder / "voice-times-raw.tsv", "w", encoding="utf-8") as raw, open(folder / "voice-times.tsv", "w", encoding="utf-8") as f:
    raw.write("#\tstart\tend\timage\ttext\n"); f.write("#\tstart\tend\timage\ttext\n")
    for i, (p, d) in enumerate(zip(pieces, durations), 1):
        txt = " ".join(xv.TAG_RE.sub("", p.text).split())
        raw.write(f"{i}\t{xv.fmt_time(t)}\t{xv.fmt_time(t + d)}\t{p.cue}\t{txt}\n")
        f.write(f"{i}\t{t + LEAD:.2f}\t{t + d + LEAD:.2f}\t{p.cue}\t{txt}\n")
        t += d + p.silence_after_ms / 1000
print(f"voice.mp3 + voice-times.tsv: {len(pieces)} regels, stem eindigt op {t - pieces[-1].silence_after_ms / 1000 + LEAD:.1f} s")
