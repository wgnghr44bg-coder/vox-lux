"""Hulp bij het ombouwen naar de opbouw van 12 nov 2026.
  python tools/ombouw_blokken.py lijst <map> [deelnr]      -> blokken met jij-vorm/vragen/ik/verwijzingen (slug, HEAD, BODY)
  python tools/ombouw_blokken.py vervang <map> <json>      -> {"<img-slug>": {"head": "...", "body": "..."}}, BRIDGE-regels weg
"""
import json, re, sys
from pathlib import Path

VLAG = re.compile(r"\byou(r|rs|rself|'d|'ll|'re|'ve)?\b|\?|\bI\b|\bimagine\b|\blet us\b|\blet's\b|\bwe will\b|"
                  r"\bwe'll\b|\bour story\b|\bremember\b|\bas we\b|\bwe need\b|\bfollow\b|\bcome with me\b", re.I)


def delen(m):
    return sorted((Path(m) / "src-feiten").glob("deel*.txt"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))


def lijst(m, nr=None):
    for p in delen(m):
        if nr and p.stem != f"deel{nr}":
            continue
        for b in re.split(r"\r?\n===\r?\n", p.read_text(encoding="utf-8")):
            im = re.search(r"^IMG:\s*(.+?)\s*\|", b, re.M)
            h = re.search(r"^HEAD:\s*(.+)$", b, re.M)
            bo = re.search(r"^BODY:\s*(.+)$", b, re.M | re.S)
            if not (im and h and bo):
                continue
            tekst = h.group(1) + " " + bo.group(1)
            if VLAG.search(tekst):
                gevonden = sorted({x.group(0).lower() for x in VLAG.finditer(tekst)})
                print(f"## {im.group(1)}  [{', '.join(gevonden)}]\nHEAD: {h.group(1).strip()}\nBODY: {' '.join(bo.group(1).split())}\n")


def vervang(m, js):
    nieuw = json.loads(Path(js).read_text(encoding="utf-8"))
    gedaan = set()
    for p in delen(m):
        uit = []
        for b in re.split(r"\r?\n===\r?\n", p.read_text(encoding="utf-8")):
            b = re.sub(r"^BRIDGE:.*(\n(?!===|IMG:|TOPIC:|HEAD:|BODY:).*)*", "", b, flags=re.M).strip("\n")
            im = re.search(r"^IMG:\s*(.+?)\s*\|", b, re.M)
            if im and im.group(1) in nieuw:
                n = nieuw[im.group(1)]
                if "head" in n:
                    b = re.sub(r"^HEAD:.*$", lambda _: "HEAD: " + n["head"], b, flags=re.M)
                if "body" in n:
                    b = re.sub(r"^BODY:[\s\S]*$", lambda _: "BODY: " + n["body"], b, flags=re.M)
                gedaan.add(im.group(1))
            uit.append(b)
        p.write_text("\n===\n".join(uit).rstrip("\n") + "\n", encoding="utf-8")
    mis = set(nieuw) - gedaan
    print(f"{len(gedaan)} blokken vervangen" + (f", NIET GEVONDEN: {sorted(mis)}" if mis else ""))


if sys.argv[1] == "lijst":
    lijst(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
else:
    vervang(sys.argv[2], sys.argv[3])
