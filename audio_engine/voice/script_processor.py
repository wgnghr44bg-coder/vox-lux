"""Turns a script into pieces (text, pause after) that OmniVoice can speak one by one.

- Blank line = new paragraph (longer pause).
- [pause] and [long-pause] on their own or inside the text add an extra pause.
- Sentences end at . ! ? (also with closing quotes), but not after Mr. / Dr. / St. etc. or in numbers like 1.5.
- Sentences longer than max_chars are split at ';' or ',' near the middle, with a short pause.
"""
import re

ABBREV = {"mr", "mrs", "ms", "dr", "st", "mt", "jr", "sr", "vs", "etc", "no", "prof", "gen", "col", "capt", "lt",
          "sgt", "e.g", "i.e", "approx", "fig", "u.s", "u.k"}
MARK = re.compile(r"\[(long-pause|pause)\]", re.I)


def sentences(par):
    out, buf = [], ""
    for tok in re.split(r"(?:(?<=[.!?])|(?<=[.!?][\"'”’)]))\s+", par.strip()):
        buf = f"{buf} {tok}".strip() if buf else tok
        last = re.sub(r"[\"'”’)]+$", "", buf).rsplit(" ", 1)[-1].rstrip(".").lower()
        if last in ABBREV or re.search(r"\b[A-Z]\.$", buf):       # Mr. / initials: sentence goes on
            continue
        out.append(buf)
        buf = ""
    if buf:
        out.append(buf)
    return [s for s in out if s.strip()]


def split_long(s, max_chars):
    if len(s) <= max_chars:
        return [s]
    mid = len(s) // 2
    cuts = [m.end() for m in re.finditer(r"[;,]\s", s)]
    if not cuts:
        return [s]
    cut = min(cuts, key=lambda c: abs(c - mid))
    return split_long(s[:cut].strip(), max_chars) + split_long(s[cut:].strip(), max_chars)


def pieces(script, cfg):
    """List of (text, pause_after_seconds). Text '' = pure pause."""
    out = []
    pars = re.split(r"\n\s*\n", script.replace("\r\n", "\n").strip())
    for par in pars:
        for chunk in MARK.split(" ".join(par.split())):
            if chunk.lower() == "pause":
                out.append(("", cfg.pause_marker))
                continue
            if chunk.lower() == "long-pause":
                out.append(("", cfg.pause_long_marker))
                continue
            for s in sentences(chunk):
                parts = split_long(s, cfg.max_chars)
                for i, p in enumerate(parts):
                    out.append((p, cfg.pause_split if i < len(parts) - 1 else cfg.pause_sentence))
        if out:
            out[-1] = (out[-1][0], max(out[-1][1], cfg.pause_paragraph))
    # merge pause-only pieces into the previous piece's pause
    merged = []
    for text, pause in out:
        if not text and merged:
            merged[-1] = (merged[-1][0], merged[-1][1] + pause)
        elif text:
            merged.append((text, pause))
    return merged
