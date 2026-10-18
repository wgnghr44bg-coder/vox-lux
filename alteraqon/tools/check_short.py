"""Alteraqon: vaste regels van de eigenaar controleren vóór het renderen.

Gebruik:  python alteraqon/tools/check_short.py alteraqon/<datum>-<slug>
make_video.py roept dit zelf aan voor video's vanaf 19 okt 2026 en weigert te renderen bij een FOUT.
Exitcode 0 = goed, 1 = fouten (met uitleg wat er aangepast moet worden).
"""
import importlib.util, json, re, sys
from pathlib import Path

BANNED_PROMPT = ["ruler", "measuring", "tape measure", "thermometer", "clock", "chart", "graph", "sign ", "signpost",
                 "billboard", "scale bar", "gauge", "display", "screen", "calendar", "label", "number"]
FILLER = ["right now", "right now."]
TIME_WORDS = r"(second|seconds|minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)"


def check(vid: Path) -> list:
    errs = []
    cues = (vid / "script-cues.txt").read_text(encoding="utf-8")
    spoken = re.sub(r"\{img:[^}]*\}|\[[a-z ]*\]", " ", cues)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", spoken) if s.strip()]

    if any(f in spoken.lower() for f in FILLER):
        errs.append('Script: "Right now." (opvulzin) mag niet – haal het weg.')
    for s in sentences:
        if re.fullmatch(rf"(one|two|three|four|five|six|seven|eight|nine|ten|twelve|a|an|millions of|thousands of)\s+{TIME_WORDS}\.?", s, re.I):
            errs.append(f'Script: tijdstap "{s}" moet met "After" beginnen ("After {s[0].lower()+s[1:]}").')
    if re.search(r"\d", spoken):
        errs.append("Script: getallen voluit schrijven (geen cijfers), anders spreekt Chatterbox ze verkeerd uit.")
    if "then." not in spoken.lower():
        errs.append('Script: "Then." ontbreekt.')
    if "here's the twist" not in spoken.lower():
        errs.append("Script: \"But here's the twist.\" ontbreekt.")
    words = len(spoken.split())
    if not 110 <= words <= 150:
        errs.append(f"Script: {words} woorden; houd het op ±120–135 (60–70 s).")

    for line in (vid / "prompts.txt").read_text(encoding="utf-8").splitlines():
        if "|" not in line:
            continue
        name, prompt = line.split("|", 1)
        low = re.sub(r"\bno [a-z]+", " ", prompt.lower())   # "no text, no labels" is juist goed
        hits = [b.strip() for b in BANNED_PROMPT if b in low]
        if hits:
            errs.append(f"Prompt {name}: bevat {', '.join(hits)} – geeft onleesbare cijfers/tekst; kies een ander beeld.")

    up = json.loads((vid / "upload.json").read_text(encoding="utf-8"))
    if not up.get("title", "").startswith("What if"):
        errs.append('upload.json: titel moet beginnen met "What if".')
    tags = re.findall(r"#\w+", up.get("description", ""))
    if len(tags) != 4 or "#shorts" not in tags:
        errs.append("upload.json: beschrijving moet eindigen op precies 4 hashtags, waaronder #shorts.")
    if "👇" not in up.get("description", ""):
        errs.append("upload.json: beschrijving mist de vraag aan de kijker met 👇.")
    if len(up.get("tags", [])) != 4:
        errs.append("upload.json: precies 4 tags.")

    spec = importlib.util.spec_from_file_location("shots", vid / "shots.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    for sh in m.SH:
        st = sh[4] if len(sh) > 4 else None
        if st and len(st[1]) > 13:
            errs.append(f'shots.py: groot getal "{st[1]}" is te lang (max 13 tekens).')
        if st and re.fullmatch(r"1\s*(SECOND|MINUTE|HOUR|DAY|WEEK|MONTH|YEAR)", st[1], re.I):
            errs.append(f'shots.py: tijdstempel "{st[1]}" moet "AFTER {st[1]}" zijn.')
    tsv = vid / "voice-times.tsv"
    if tsv.exists():
        rows = [r.split("\t") for r in tsv.read_text(encoding="utf-8").splitlines() if r and not r.startswith("#")]
        bang = getattr(m, "BANG", None)
        if bang is not None:
            line = m.SH[bang][0]
            line = line[0] if isinstance(line, tuple) else line
            if rows[line - 1][4].strip() != "Then.":
                errs.append(f'shots.py: BANG wijst naar regel {line} ("{rows[line-1][4].strip()}"), niet naar "Then.".')
        for sh in m.SH:
            line = sh[0][0] if isinstance(sh[0], tuple) else sh[0]
            if line > len(rows):
                errs.append(f"shots.py: regel {line} bestaat niet in voice-times.tsv ({len(rows)} regels).")
    return errs


if __name__ == "__main__":
    vid = Path(sys.argv[1])
    errs = check(vid)
    if errs:
        print("FOUT – pas dit aan en draai opnieuw:")
        for e in errs:
            print(" -", e)
        sys.exit(1)
    print("Controle goed: alle vaste regels kloppen.")
