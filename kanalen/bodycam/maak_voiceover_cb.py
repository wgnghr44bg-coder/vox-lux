"""Bodycam-verteller met Chatterbox (VASTE STEM, eigenaar 17 nov 2026: "Nummer 3" = ontworpen Amerikaanse man,
natuurlijker dan OmniVoice). Zelfde uitvoer als maak_voiceover.py: <map>/stem/blokNN.wav + stem/blokken.json.

Werkwijze (eigenaar: "te robot achtig", "gelach", "te snel"):
- elke alinea in ÉÉN keer ingesproken (natuurlijke zinsmelodie), lange alinea's in stukken van ± 2-3 zinnen;
- Whisper controleert woord voor woord; anders opnieuw (andere seed), tot 6x;
- alles vóór het eerste en ná het laatste woord eraf (geen lachjes/adem/"huh");
- adempauze op elke zinsgrens (0,55 s) en kort bij komma's (0,15 s), op het stilste punt geknipt: rustiger zonder de
  stem zelf te veranderen.
Regels die met '#' of '[' beginnen worden niet uitgesproken. Uitspraak: kanalen/bodycam/uitspraak.json.

  C:/Users/rane/chatterbox-venv/Scripts/python.exe kanalen/bodycam/maak_voiceover_cb.py kanalen/bodycam/videos/<map>
      [--alleen 1,3] [--seed-extra 1]
"""
import difflib, json, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf, torch, librosa

HIER = Path(__file__).resolve().parent
STEM = Path("C:/Users/rane/vox-lux-stemmen/ontwerp-us-man-laag-3/ref-rustig.wav")   # eigenaar 17 nov: "ik wil toch stem 5"
EXAGGERATION, CFG = 0.5, 0.3   # tempo komt uit de rustige referentie (ref-rustig.wav = ref op 0,85x)
PAUZE = {".": 0.75, "?": 0.75, "!": 0.75}   # geen kommapauzes meer: knippen midden in een klank gaf "stotteren"
UITSPRAAK = json.loads((HIER / "uitspraak.json").read_text(encoding="utf-8"))

map_ = Path(sys.argv[1])
ALLEEN = {int(x) for x in sys.argv[sys.argv.index("--alleen") + 1].split(",")} if "--alleen" in sys.argv else None
EXTRA = int(sys.argv[sys.argv.index("--seed-extra") + 1]) if "--seed-extra" in sys.argv else 0

from chatterbox.tts import ChatterboxTTS
from transformers import pipeline
model = ChatterboxTTS.from_pretrained(device="cuda")
SR = model.sr
ASR = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
GETAL = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty",
         "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "first", "second",
         "third", "fourth", "fifth", "and", "a"}


def woorden(t):
    w = re.findall(r"[a-z']+", t.lower().replace("-", " "))
    return [x for x in w if x not in GETAL and not (len(x) <= 4 and re.fullmatch(r"(?:th|st|nd|rd|s)", x))]


def voor_stem(z):
    for woord, klank in UITSPRAAK.items():
        z = re.sub(r"(?<![A-Za-z])" + re.escape(woord) + r"(?![A-Za-z])", klank, z)
    return z


def hoor(a):
    x = librosa.resample(a, orig_sr=SR, target_sr=16000)
    x = np.concatenate([np.zeros(8000, np.float32), x, np.zeros(8000, np.float32)])
    r = ASR({"raw": x, "sampling_rate": 16000}, generate_kwargs={"language": "en"}, return_timestamps="word")
    return r["text"].strip(), [c for c in r["chunks"] if c["text"].strip()]


def stuk(tekst, n, k):
    """Eén stuk tekst inspreken, controleren, staart eraf, pauzes op zinsgrenzen."""
    beste = None
    for poging in range(6):
        torch.manual_seed(1000 * EXTRA + 100 * n + 10 * k + poging)
        a = model.generate(voor_stem(tekst), audio_prompt_path=str(STEM), exaggeration=EXAGGERATION,
                           cfg_weight=CFG).squeeze(0).cpu().numpy().astype(np.float32)
        gehoord, ch = hoor(a)
        sc = difflib.SequenceMatcher(None, woorden(tekst), woorden(gehoord)).ratio()
        if ch and (beste is None or sc > beste[0]):
            beste = (sc, a, ch, gehoord)
        if sc >= 0.999:
            break
        print(f"  blok {n} stuk {k}: niet precies ({sc:.2f}): \"{gehoord}\" -> opnieuw", flush=True)
    sc, a, ch, gehoord = beste
    if sc < 0.999:
        print(f"LET OP blok {n} stuk {k}: beste {sc:.2f}: \"{gehoord}\"", flush=True)
    t0 = lambda c: c["timestamp"][0] - 0.5
    t1 = lambda c: (c["timestamp"][1] if c["timestamp"][1] is not None else c["timestamp"][0] + 0.4) - 0.5
    begin, eind = max(0.0, t0(ch[0]) - 0.08), min(len(a) / SR, t1(ch[-1]) + 0.2)
    # Zinsgrenzen uit het SCRIPT (Whisper zet bij woordtijden vaak geen punten): script-woorden koppelen aan de
    # Whisper-woorden en na elk script-woord dat een zin afsluit een pauze zetten.
    norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    sw = tekst.split()
    eindes = {i for i, w in enumerate(sw) if w[-1] in PAUZE and i < len(sw) - 1}
    koppel = {}
    for blok_ in difflib.SequenceMatcher(None, [norm(w) for w in sw], [norm(c["text"]) for c in ch]).get_matching_blocks():
        for d in range(blok_.size):
            koppel[blok_.a + d] = blok_.b + d
    delen, vorige = [], int(begin * SR)
    for si in sorted(eindes):
        if si not in koppel or koppel[si] + 1 >= len(ch):
            continue
        c, v = ch[koppel[si]], ch[koppel[si] + 1]
        # alleen invoegen op een zacht moment (30 ms onder -32 dB t.o.v. de piek) binnen 150 ms van de woordgrens;
        # nooit midden in een klank (eigenaar 17 nov: "hij stottert nog een beetje")
        i, w, kk = int((t1(c) + t0(v)) / 2 * SR), int(0.15 * SR), int(0.03 * SR)
        lo = max(vorige + kk, i - w)
        seg = a[lo:i + w]
        if len(seg) <= kk:
            continue
        env = np.sqrt(np.convolve(seg ** 2, np.ones(kk) / kk, "same"))
        j = int(np.argmin(env))
        if env[j] > np.abs(a).max() * 10 ** (-32 / 20):
            continue
        i = lo + j
        delen += [a[vorige:i], np.zeros(int(PAUZE[sw[si][-1]] * SR), np.float32)]
        vorige = i
    delen.append(a[vorige:int(eind * SR)])
    uit = np.concatenate(delen)
    n_f = int(0.015 * SR)
    uit[:n_f] *= np.linspace(0, 1, n_f)
    uit[-n_f:] *= np.linspace(1, 0, n_f)
    return uit


regels = [r for r in (map_ / "script.txt").read_text(encoding="utf-8").splitlines()
          if not r.startswith("#") and not r.startswith("[")]
alineas = [" ".join(a.split()) for a in re.split(r"\n\s*\n", "\n".join(regels)) if a.strip()]
uitmap = map_ / "stem"
uitmap.mkdir(exist_ok=True)
oud = {b["blok"]: b for b in json.loads((uitmap / "blokken.json").read_text(encoding="utf-8"))} if ALLEEN else {}
blokken = []
for n, alinea in enumerate(alineas, 1):
    if ALLEEN and n not in ALLEEN and n in oud:
        blokken.append(oud[n])
        continue
    zinnen = [z for z in re.split(r"(?<=[.!?])\s+", alinea) if z]
    groepen, g = [], []
    for z in zinnen:                      # stukken van hooguit ± 45 woorden (Chatterbox blijft dan stabiel)
        if g and len(" ".join(g + [z]).split()) > 45:
            groepen.append(" ".join(g))
            g = []
        g.append(z)
    groepen.append(" ".join(g))
    delen = []
    for k, tekst in enumerate(groepen, 1):
        delen += [stuk(tekst, n, k), np.zeros(int(0.55 * SR), np.float32)]
    stem = np.concatenate(delen[:-1])
    doel = uitmap / f"blok{n:02d}.wav"
    ruw = uitmap / f"ruw{n:02d}.wav"
    sf.write(ruw, stem, SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ruw), "-af", "highpass=f=70", "-ar", "48000", "-ac", "1",
                    str(doel)], check=True)
    ruw.unlink()
    duur = sf.info(doel).duration
    blokken.append({"blok": n, "bestand": doel.name, "duur": round(duur, 2), "tekst": alinea})
    print(f"blok {n:02d}: {duur:5.1f} s  {len(alinea.split()) / (duur / 60):.0f} w/min  {alinea[:60]}", flush=True)
(uitmap / "blokken.json").write_text(json.dumps(blokken, indent=1, ensure_ascii=False), encoding="utf-8")
tot = sum(b["duur"] for b in blokken)
print(f"klaar: {len(blokken)} blokken, {tot:.0f} s stem, {sum(len(b['tekst'].split()) for b in blokken) / (tot / 60):.0f} w/min")
