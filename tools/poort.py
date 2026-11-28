"""Poort (eigenaar 28 nov 2026: "dit moet elke keer goed gaan ik heb dit nu al paar keer gezegd").
Een Market Doodle-short mag pas naar de eigenaar of online als ALLE wachters in de map op 0 staan en er niets ontbreekt:
  TEKSTWACHTER.md   genoemd = gezien, spreker, gevoel, DOEN
  MOMENTWACHTER.md  wat gezegd wordt gebeurt OP DAT MOMENT in beeld (opens, rips, sits down, nobody notices ...)
  FIGUURWACHTER.md  poppetjes heel en zichtbaar (geen lijf weg achter een tafel), gebaren/handen binnen beeld
  SCENEWACHTER.md   ondergrond / maat
  TEMPOWACHTER.md   stemtempo per zin
  render.log        SHORTREGELS: alles goed, GELUIDCHECK: elk geluid hoort bij iets in beeld, LAYOUT: alles past
  momenten.jpg      beelden op de precieze spreekmomenten (zelf nakijken), TEKSTCONTROLE.jpg
  luidheid          -15,5 .. -12,5 LUFS, true peak <= -0,9 dB
  python tools/poort.py <map> [video.mp4]   -> "POORT: OPEN" of een lijst met wat er mis is (exit 1)
"""
import re, subprocess, sys
from pathlib import Path

def poort(map_, video=None):
    m = Path(map_); fout = []
    for naam in ("TEKSTWACHTER.md", "MOMENTWACHTER.md", "FIGUURWACHTER.md", "SCENEWACHTER.md", "TEMPOWACHTER.md"):
        p = m / naam
        if not p.exists(): fout.append(f"{naam} ontbreekt (wachter niet gedraaid)"); continue
        r = re.search(r"\*\*(\d+) fout", p.read_text(encoding="utf-8"))
        if not r: fout.append(f"{naam}: geen uitslag gevonden")
        elif int(r.group(1)): fout.append(f"{naam}: {r.group(1)} fouten")
    log = (m / "render.log").read_text(encoding="utf-8", errors="replace") if (m / "render.log").exists() else ""
    for eis in ("SHORTREGELS: alles goed", "GELUIDCHECK: elk geluid hoort bij iets in beeld", "LAYOUT: alles past"):
        if eis not in log: fout.append(f"render.log: '{eis}' ontbreekt")
    for b in ("momenten.jpg", "TEKSTCONTROLE.jpg"):
        if not (m / b).exists(): fout.append(f"{b} ontbreekt (spreekmomenten / controleblad niet gemaakt)")
    if video:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, errors="replace").stderr
        I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
        if not I: fout.append("luidheid niet te meten")
        else:
            li, pk = float(I[-1]), float(P[-1]) if P else 0.0
            if not (-15.5 <= li <= -12.5 and pk <= -0.9): fout.append(f"luidheid {li:.1f} LUFS / piek {pk:.1f} dB (moet -15,5..-12,5 en <= -0,9)")
    return fout

if __name__ == "__main__":
    f = poort(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print("POORT: OPEN" if not f else "POORT: DICHT\n" + "\n".join("- " + x for x in f)); sys.exit(1 if f else 0)
