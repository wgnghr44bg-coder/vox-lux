"""Beelden-wachter (eigenaar 16 nov 2026: "laat dit een les zijn dat de afbeeldingen goed moeten zijn" en "graag hierop
extra controle wachter zetten", na een kijker die schreef dat ons Mayflower-schip er nauwelijks op leek).

Kijkt per video naar twee dingen die de gewone beeldcontrole (tools/beeldcheck.py) niet ziet:
  1. bekende dingen zonder kenmerken: een schip, gebouw, voertuig of "the <Naam>" in de beeldbeschrijvingen waarvoor
     stories/<map>/kenmerken.txt geen beschrijving heeft -> de beeldmaker weet dan niet hoe het er echt uitzag;
  2. dubbele beelden: twee (bijna) dezelfde beelden, bv. omdat een afgekeurd beeld door het beeld ervoor is vervangen
     (Dallas 16 nov: 066 was een kopie van 065).

  python tools/beelden_wachter.py                 # alle video's van de komende 21 dagen (seintjes in ROUTINE-LOG)
  python tools/beelden_wachter.py stories/<map>   # één video, zonder log
De keten (routine_lokaal.maak_video) draait hem na de beelden: te veel dubbele beelden = eerst opnieuw maken.
De bewaker draait hem elk uur, zodat ontbrekende kenmerken dagen van tevoren in het logboek staan.
"""
import datetime as dt, re, sys
from pathlib import Path

from PIL import Image

HIER = Path(__file__).resolve().parent
STORIES = HIER.parent / "stories"
VOORUIT = 21
DUBBEL_MAX = 2                                         # meer dubbele paren dan dit: de keten maakt ze eerst opnieuw

# soorten bekende dingen waarvan de vorm per tijd sterk verschilt (geen muren of torens in het algemeen: te vaag)
BEKEND = (r"\b(ship|steamship|liner|battleship|warship|sloop|frigate|galleon|carrack|longship|airship|zeppelin|"
          r"locomotive|steam train|biplane|limousine|cathedral|pyramid|ziggurat|lighthouse|colosseum|basilica)s?\b")
# namen: schepen (USS/HMS/RMS/SS Naam, the Mayflower) en bouwwerken ("the Ishtar Gate", "the White House"), geen landstreken
NAAM = (r"\b(?:USS|HMS|RMS|SS)\s+[A-Z][\w'’-]+"
        r"|\b(?:[A-Z][\w'’-]+\s){1,3}(?:Gate|House|Palace|Temple|Tower|Bridge|Cathedral|Abbey|Office|Depository|Revenge|Castle)\b"
        r"|\b(?:Mayflower|Titanic|Hindenburg|Lusitania|Bounty|Endeavour|Arizona)\b")
STIJL = r",? ?A (?:calm, warmly lit )?scene (?:from|in|on|at) |\. Cinematic"     # vaste stijlzinnen tellen niet mee


def kenmerken(m):
    k = m / "kenmerken.txt"
    if not k.exists():
        return []
    return [r.split("|", 1)[0].strip().lower() for r in k.read_text(encoding="utf-8").splitlines()
            if "|" in r and not r.startswith("#")]


def prompts(m):
    p = m / "prompts.txt"
    if not p.exists():
        return {}
    return {r.split("|", 1)[0]: r.split("|", 1)[1] for r in p.read_text(encoding="utf-8").splitlines()
            if "|" in r and not r.startswith("#")}


def ontbrekend(m):
    """{ding: [beeldnummers]} voor bekende dingen in de beschrijvingen zonder regel in kenmerken.txt."""
    km, uit = kenmerken(m), {}
    for n, p in prompts(m).items():
        kern = re.split(STIJL, p)[0]
        dingen = {x.lower() for x in re.findall(BEKEND, kern, re.I)}
        dingen |= {re.sub(r"^(?:The|A|An|In|On|At)\s+", "", x).strip() for x in re.findall(NAAM, kern)}
        for d in dingen:
            if not any(k in d.lower() or d.lower() in k for k in km):
                uit.setdefault(d, []).append(n)
    return {d: n for d, n in uit.items() if len(n) >= 2 or d[:1].isupper()}   # losse "tower" in één beeld: niet zeuren


def dhash(p, n=8):
    im = Image.open(p).convert("L").resize((n + 1, n), Image.LANCZOS)
    px = list(im.tobytes())
    return sum(1 << i for i, (a, b) in enumerate((px[r * (n + 1) + c], px[r * (n + 1) + c + 1])
                                                    for r in range(n) for c in range(n)) if a > b)


def dubbel(m):
    """Paren (bijna) dezelfde beelden: [(a, b)]."""
    beelden = sorted((m / "afbeeldingen").glob("[0-9]*.png"))
    h = [(p.stem, dhash(p)) for p in beelden]
    uit = []
    for i, (a, ha) in enumerate(h):
        for b, hb in h[i + 1:]:
            if bin(ha ^ hb).count("1") <= 3:
                uit.append((a, b))
    return uit


LIJKT = 0.94          # CLIP-gelijkenis; mediaan in een video ± 0.83, hetzelfde boerenerf in Crisis 0.95-0.96


def lijkend(m, drempel=LIJKT):
    """Paren beelden die op elkaar lijken (zelfde soort scène, zelfde opbouw), via CLIP. Eigenaar 16 nov 2026: "de beelden
    mogen niet op elkaar lijken, dat moet echt anders". Heeft torch nodig (OmniVoice-omgeving); zonder: alleen dubbel()."""
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
    except ImportError:
        return dubbel(m)
    ps = sorted((m / "afbeeldingen").glob("[0-9]*.png"))
    if len(ps) < 2:
        return []
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    mod = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").eval().to(dev)
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
    embs = []
    with torch.no_grad():
        for i in range(0, len(ps), 16):
            x = proc(images=[Image.open(p).convert("RGB") for p in ps[i:i + 16]], return_tensors="pt").to(dev)
            e = mod.get_image_features(**x)
            e = e if torch.is_tensor(e) else e.pooler_output
            embs.append(torch.nn.functional.normalize(e, dim=-1).cpu())
    del mod
    if dev == "cuda":
        torch.cuda.empty_cache()
    S = torch.cat(embs) @ torch.cat(embs).T
    return [(ps[i].stem, ps[j].stem) for i in range(len(ps)) for j in range(i + 1, len(ps)) if S[i, j] >= drempel]


def opnieuw_nodig(paren):
    """Welke beelden opnieuw: per groep lijkende beelden blijft het eerste staan, de rest krijgt een ander beeld."""
    houden, weg = set(), set()
    for a, b in sorted(paren):
        if a not in weg:
            houden.add(a)
            weg.add(b)
        elif b not in houden:
            weg.add(b)
    return sorted(weg - houden)


def rapport(m, paren=None):
    o = ontbrekend(m)
    d = paren if paren is not None else (dubbel(m) if (m / "afbeeldingen").exists() else [])
    regels = [f"{m.name}: geen kenmerken voor '{x}' (beeld {', '.join(n[:5])}{'…' if len(n) > 5 else ''})" for x, n in o.items()]
    if d:
        regels.append(f"{m.name}: {len(d)} dubbele beelden ({', '.join(a + '=' + b for a, b in d[:6])})")
    return o, d, regels


def log(t):
    with open(STORIES / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
        f.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} beelden-wachter: {t}\n")


def alle():
    vandaag = dt.date.today()
    oud = (STORIES / "ROUTINE-LOG.md").read_text(encoding="utf-8", errors="replace")
    for p in sorted(STORIES.glob("*/planning.txt")):
        t = p.read_text(encoding="utf-8", errors="replace")
        d = re.search(r"^datum\s+\S+\s+(\d{4}-\d{2}-\d{2})", t, re.M)
        if not d or "reserve" in d.group(0):
            continue
        if not vandaag <= dt.date.fromisoformat(d.group(1)) <= vandaag + dt.timedelta(days=VOORUIT):
            continue
        for r in rapport(p.parent)[2]:
            print("SEINTJE", r)
            if f"beelden-wachter: SEINTJE {r}" not in oud:
                log(f"SEINTJE {r}")


if __name__ == "__main__":
    if "--lijkend" in sys.argv:                            # voor de keten: in de OmniVoice-omgeving (torch)
        paren = lijkend(Path(sys.argv[sys.argv.index("--lijkend") + 1]))
        print("LIJKEND " + " ".join(f"{a}={b}" for a, b in paren))
        print("OPNIEUW " + ",".join(opnieuw_nodig(paren)))
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        for r in rapport(Path(sys.argv[1]))[2] or ["BEELDEN-WACHTER GOED"]:
            print(r)
    else:
        alle()
