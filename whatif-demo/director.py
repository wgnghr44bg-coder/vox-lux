#!/usr/bin/env python3
"""The director: picks the camera for every sentence, following the story and the voice.

    python whatif-demo/director.py 45                 # choose the shots of topic 45 again (rules + Grok looks)
    python whatif-demo/director.py 45 --no-look       # rules only (free)
    python whatif-demo/director.py 45 --wish "zin 3 dichtbij op de auto's"

0. The script may say it itself: export const camera = { cars: 'close cars', sky: 'pov' } (line id -> camera).
1. Every camera standpoint has a label (engine/shots.json): wide, aerial, medium, close, pov, tele or sky, and what it shows.
   Auto blocks with a position (engine/auto/) get their own wide and close standpoint.
2. Grok reads the sentences and says per sentence what it is about (subject), what kind of moment it is
   (establish, explain, detail, event, climax, aftermath, reflect) and how intense (0-3).
3. Film rules give every standpoint a score per sentence: open wide; a detail gets a close-up that shows it;
   POV only as a short accent (2-3 s) at the most intense moments; wide after the climax to show the scale;
   never the same shot twice in a row; cuts in the middle of the pauses in the voice, a long sentence gets a second shot.
4. Where it is close, the three best standpoints are rendered at that moment and Grok picks the one that shows
   what the voice says best (about 1-2 cents). The result is written into scenario.js (shots and extraShots).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "engine"
sys.path.insert(0, str(HERE))

TYPES = ["wide", "aerial", "medium", "close", "pov", "tele", "sky"]
# score per kind of moment for each type of shot
PREFER = {
    "establish": {"wide": 3, "aerial": 3, "medium": 1, "tele": 0, "close": -1, "pov": -2, "sky": -1},
    "explain":   {"wide": 1, "aerial": 1, "medium": 2, "tele": 1, "close": 1, "pov": -1, "sky": 0},
    "detail":    {"close": 3, "medium": 2, "tele": 2, "pov": 0, "wide": -1, "aerial": -2, "sky": 0},
    "event":     {"medium": 2, "close": 2, "wide": 1, "tele": 1, "pov": 1, "aerial": 0, "sky": 0},
    "climax":    {"pov": 2, "wide": 2, "medium": 1, "close": 1, "tele": 1, "aerial": 1, "sky": 1},
    "aftermath": {"wide": 3, "aerial": 3, "medium": 1, "tele": 1, "close": 0, "pov": -1, "sky": 0},
    "reflect":   {"wide": 2, "aerial": 2, "sky": 2, "medium": 1, "tele": 1, "close": 0, "pov": 0},
}


def node_json(js: str, f: Path):
    return json.loads(subprocess.run(["node", "-e", js, f.as_uri()], capture_output=True, text=True, check=True, encoding="utf-8").stdout)


def render(slug: str, times, shots=None) -> str:
    import os
    env = dict(os.environ); env.pop("SHOTS", None)
    if shots is not None: env["SHOTS"] = json.dumps(shots)
    r = subprocess.run(["node", str(ENGINE / "render.mjs"), slug, *(["stills", *times] if times else ["timeline"])],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode: raise RuntimeError((r.stdout + r.stderr)[-1500:])
    return r.stdout


def line_times(d: Path, lines, tl) -> list[tuple[float, float]]:
    """Real times from timing.json (after the voice), else the engine's word-count estimate."""
    f = d / "timing.json"
    if f.exists():
        tm = json.loads(f.read_text(encoding="utf-8")); off = tm.get("VO_OFFSET", .8)
        return [(tm["lines"][lid][0] + off, tm["lines"][lid][1] + off) for lid, _, _ in lines]
    from make_topic import line_times as est
    return est(lines, tl.get("VO_OFFSET", .8))


def open_dirs(shots: dict, c) -> list:
    """Directions (unit x, z) from c towards the place's own standpoints: there is open space for a camera."""
    import math
    out = []
    for v in (shots or {}).values():
        p = v.get("pos") if isinstance(v, dict) else None
        if not p: continue
        dx, dz = p[0] - c[0], p[2] - c[2]; l = math.hypot(dx, dz)
        if l > 20: out.append((dx / l, dz / l, l, p[1]))
    return out


def candidates(place: str, tl: dict, shots: dict | None = None) -> dict:
    """All standpoints the director may use: labelled place shots, the scenario's own extra shots, and a wide and a
    close standpoint for every auto block that has a position."""
    meta = json.loads((ENGINE / "shots.json").read_text(encoding="utf-8")).get(place, {})
    out = {k: v for k, v in meta.items() if not v.get("skip")}
    for k, v in (tl.get("extraShots") or {}).items():
        if k.startswith("auto-"): continue
        t = "pov" if k.startswith("pov") or v.get("hand") else "tele" if v.get("fov", 60) < 35 else "medium"
        out.setdefault(k, {"type": t, "shows": re.split(r"[-_ ]", k)})
    for a in tl.get("auto") or []:
        pts = a.get("pos")
        if not pts: continue
        pts = pts if isinstance(pts[0], (list, tuple)) else [pts]
        c = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
        words = re.split(r"[-_ ]", a["block"])
        # aim from where the place has its own standpoints (open space), the closest of them that is far enough away
        wide = {k: v for k, v in (shots or {}).items() if meta.get(k, {}).get("type") in ("wide", "aerial")}
        dirs = sorted(open_dirs(wide, c), key=lambda d: d[2]) or sorted(open_dirs(shots, c), key=lambda d: d[2]) or [(0.4, 0.92, 80, 10)]
        ux, uz = dirs[0][0], dirs[0][1]
        out[f"auto-{a['block']}-wide"] = {"type": "wide", "shows": words, "shot": {"pos": [c[0] + ux * 75, c[1] + 24, c[2] + uz * 75], "look": c, "fov": 52}}
        out[f"auto-{a['block']}-close"] = {"type": "close", "shows": words, "shot": {"pos": [c[0] + ux * 36, c[1] + 13, c[2] + uz * 36], "look": c, "fov": 50}}
    return out


def tag_lines(grok, lines, vocab, style: str, wish: str = "") -> dict:
    said = "\n".join(f'{lid}: "{text}"' for lid, text, _ in lines)
    ans = grok([{"role": "system", "content": "You are the director of a short 3D 'What if' video. Answer in JSON only."},
                {"role": "user", "content":
                 f"Sentences of the voice-over:\n{said}\n\nWords for what can be on screen: {', '.join(sorted(vocab))}\n"
                 f"Style: {style} ({'POV: first person, handheld' if style.startswith('A') else 'observer on a tripod, wide shots'}).\n"
                 + (f"The owner asks: {wish}\n" if wish else "") +
                 "For every sentence give: subject (1-3 words from the list, most important first: what the viewer must SEE), "
                 "kind (establish, explain, detail, event, climax, aftermath, reflect), intensity (0 calm - 3 peak), and "
                 "want (only if the owner asked for something for that sentence: a shot type wide/aerial/medium/close/pov/tele/sky "
                 "or a standpoint name, else null). JSON: {\"<id>\": {\"subject\": [...], \"kind\": \"...\", \"intensity\": 0, \"want\": null}}"}],
               json_mode=True)
    try: return json.loads(ans)
    except json.JSONDecodeError: return {}


def script_cam(tags: dict, camera: dict, cands: dict) -> None:
    """export const camera = { lineId: 'close cars', other: 'pov', last: 'aerial' } in scenario.js: the script says which
    camera a sentence gets (a type or a standpoint name, then optional words for what must be in it). The director follows it."""
    for lid, how in camera.items():
        words = str(how).lower().replace(",", " ").split()
        if not words: continue
        t = tags.setdefault(lid, {})
        head = next((w for w in words if w in TYPES or w in cands), None)
        if head: t["want"] = head
        rest = [w for w in words if w != head]
        if rest: t["subject"] = rest + [w for w in (t.get("subject") or []) if w not in rest]


def score(name, c, tag, prev, used, first, style, pov_left):
    s = 0.0
    subj = [w.lower() for w in tag.get("subject") or []]
    shows = [w.lower() for w in c.get("shows", [])]
    for i, w in enumerate(subj):
        if any(w == x or w in x or x in w for x in shows): s += 4 - i          # what the sentence is about must be in it
    kind = tag.get("kind", "explain"); t = c["type"]
    s += PREFER.get(kind, PREFER["explain"]).get(t, 0)
    inten = tag.get("intensity", 1)
    if first: s += 4 if t in ("wide", "aerial") else -3
    if t == "sky" and pov_left <= 0: s -= 9
    if t == "pov":
        if inten < 2 and kind != "climax": s -= 3                              # POV is an accent, not the default
        if not style.startswith("A"): s -= 1.5                                 # gravity style: mostly observer shots
        if pov_left <= 0: s -= 9
    if name == prev: s -= 8
    if prev and c["type"] == used.get("_type_" + prev): s -= 1                # vary the type
    s -= 2.5 * used.get(name, 0)                                              # spread the standpoints
    if used.get(name, 0) >= 3: s -= 20                                         # never more than 3 times
    want = (tag.get("want") or "")
    if want and (want == name or want == t): s += 12
    return s


def plan(lines, times, tags, cands, style, tl):
    """Greedy choice per sentence (and a second shot for long sentences and silences). Returns segments
    [(time expression, start seconds, line id, [ranked candidate names])]."""
    segs, used, prev = [], {}, None
    pov_left = 3 if style.startswith("A") else 2                           # owner: observer shots by default, POV only as an accent
    climax = tl.get("beats", {}).get("climax")
    for i, ((lid, text, pz), (s, e)) in enumerate(zip(lines, times)):
        tag = tags.get(lid) or {}
        if i:                                                                  # cut in the middle of the pause before the sentence
            pl = lines[i - 1][0]; pe = times[i - 1][1]
            parts = [(f"(at('{pl}').e + at('{lid}').s) / 2", (pe + s) / 2)] if s - pe > .25 else [(f"at('{lid}').s", s)]
        else: parts = [("0", 0.0)]
        if e - s > 6.0: parts.append((f"at('{lid}').s + (at('{lid}').e - at('{lid}').s) * .5", (s + e) / 2))
        if isinstance(pz, (int, float)) and pz >= 2.5:                         # a silent climax: show the scale while it is quiet
            parts.append((f"at('{lid}').e + .3", e + .3))
        for k, (expr, t0) in enumerate(parts):
            if segs and t0 - segs[-1][1] < 2.2 and k == 0 and not (tag.get("want")):
                continue                                                       # too short: keep the previous shot
            tg = dict(tag)
            if k == len(parts) - 1 and isinstance(pz, (int, float)) and pz >= 2.5 and k > 0: tg["kind"] = "aftermath"
            sc = {n: score(n, cands[n], tg, prev, used, not segs, style, pov_left) for n in cands}
            ranked = sorted(cands, key=lambda n: -sc[n])
            pick = ranked[0]
            # Grok may only choose between standpoints the film rules find (almost) as good; the opening stays an overview
            close = [n for n in ranked[:3] if sc[n] >= sc[pick] - 2.5 and (segs or cands[n]["type"] in ("wide", "aerial"))
                     and (cands[n]["type"] not in ("pov", "sky") or cands[pick]["type"] in ("pov", "sky"))]   # Grok never adds a POV
            want = tg.get("want")
            if want:                                                           # the script asks for this camera: only matching options
                close = [n for n in ranked[:6] if n == want or cands[n]["type"] == want][:3] or [pick]
            if len(close) < 2 and not want:                                   # always a second option: Grok can reject a blocked view
                alt = next((n for n in ranked[1:6] if cands[n]["type"] not in ("pov", "sky") and n != prev), None)
                if alt: close = (close or [pick]) + [alt]
            segs.append([expr, t0, lid, close or [pick]])
            used[pick] = used.get(pick, 0) + 1; used["_type_" + pick] = cands[pick]["type"]
            if cands[pick]["type"] in ("pov", "sky"): pov_left -= 1
            prev = pick
    return segs


def look(grok, d: Path, slug: str, segs, lines, tags, max_rows=5) -> None:
    """Render the 3 best standpoints of every segment at its moment and let Grok choose (in place, segs[i][3][0])."""
    import base64
    segs = [s for s in segs if len(s[3]) > 1]                        # only where there is a real choice
    if not segs: return
    times = [f"{min(s[1] + 1.4, s[1] + 3):.1f}" for s in segs]
    st = d / "stills" / "director"; shutil.rmtree(st, ignore_errors=True); st.mkdir(parents=True)
    for k in range(3):
        sched = [[max(0, s[1] - .05), s[3][min(k, len(s[3]) - 1)]] for s in segs]
        if sched[0][0] > 0: sched.insert(0, [0, segs[0][3][0]])
        render(slug, times, sched)
        for t in times: shutil.move(str(d / "stills" / f"still-{t}.jpg"), str(st / f"{k}-{t}.jpg"))
    text = {lid: t for lid, t, _ in lines}
    for g0 in range(0, len(segs), max_rows):
        grp = segs[g0:g0 + max_rows]; ins = []
        for i, s in enumerate(grp):
            for k in range(3): ins += ["-i", str(st / f"{k}-{times[g0 + i]}.jpg")]
        n, R = len(grp) * 3, len(grp)
        grid = st / f"grid-{g0}.jpg"
        fc = "".join(f"[{j}]scale=240:426[s{j}];" for j in range(n))
        fc += "".join(f"[s{3 * r}][s{3 * r + 1}][s{3 * r + 2}]hstack=3[r{r}];" for r in range(R))   # a row: A B C
        fc += "".join(f"[r{r}]" for r in range(R)) + (f"vstack={R}[o]" if R > 1 else "null[o]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", "[o]", str(grid)], check=True)
        rows = "\n".join(f'row {i + 1}: voice says "{text[s[2]]}"; the viewer must see: {", ".join(tags.get(s[2], {}).get("subject") or ["-"])}'
                         for i, s in enumerate(grp))
        ans = grok([{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(grid.read_bytes()).decode()}},
            {"type": "text", "text": f"A grid of camera options for a low-poly 3D video: {len(grp)} rows, 3 columns (A, B, C). "
             f"Each row is one moment:\n{rows}\n\nFor every row choose the column whose picture shows best what the voice says "
             "(the subject clearly visible, well framed). A picture blocked by something big in the foreground (a parasol, "
             "a wall, a pillar, a tree), with the camera inside an object, or mostly empty, must NOT be chosen. "
             'JSON: {"1": "A", "2": "C", ...}'}]}], json_mode=True)
        try: choice = json.loads(ans)
        except json.JSONDecodeError: continue
        for i, s in enumerate(grp):
            k = "ABC".find(str(choice.get(str(i + 1), "A")).strip().upper()[:1])
            if 0 < k < len(s[3]): s[3][0], s[3][k] = s[3][k], s[3][0]


def write_extra(d: Path, cands) -> None:
    """Standpoints the place does not have (auto blocks) go into the scenario's extraShots (replacing earlier ones)."""
    f = d / "scenario.js"; s = f.read_text(encoding="utf-8")
    s = re.sub(r"'auto-[\w-]+': \{[^{}]*\},?\s*", "", s)
    extra = {n: c["shot"] for n, c in cands.items() if "shot" in c}
    if extra:
        add = ", ".join(f"'{n}': {json.dumps(v)}" for n, v in extra.items())
        if re.search(r"\bextraShots:\s*\{", s): s = re.sub(r"\bextraShots:\s*\{", lambda m: m.group(0) + f" {add},", s, count=1)
        else: s = re.sub(r"\bshots:", f"extraShots: {{ {add} }},\n    shots:", s, count=1)
    f.write_text(s, encoding="utf-8")


def write_shots(d: Path, segs, cands) -> None:
    f = d / "scenario.js"; s = f.read_text(encoding="utf-8")
    # no two identical shots in a row after the choices
    out, last = [], None
    for expr, _, _, ranked in segs:
        pick = ranked[0] if ranked[0] != last else next((r for r in ranked[1:] if r != last), ranked[0])
        if pick != last: out.append((expr, pick)); last = pick
    shots = "shots: [" + ", ".join(f"[{e}, '{n}']" for e, n in out) + "],"
    i = s.find("shots:")
    if i < 0: raise ValueError("no shots: in scenario.js")
    j = s.index("[", i); depth = 0
    for k in range(j, len(s)):
        depth += {"[": 1, "]": -1}.get(s[k], 0)
        if depth == 0: break
    end = k + 1 + (1 if s[k + 1:k + 2] == "," else 0)
    s = s[:i] + shots + s[end:]
    f.write_text(s, encoding="utf-8")
    print("director:", " | ".join(f"{n}" for _, n in out))


def direct(d: Path, grok=None, use_look=True, wish: str = "") -> None:
    if grok is None:
        from make_topic import grok as g; grok = g
    d = d.resolve(); slug = d.name
    render(slug, None)                                                # timeline.json
    tlj = json.loads((d / "timeline.json").read_text(encoding="utf-8")); tl = tlj["TL"]
    sc = node_json("import(process.argv[1]).then(m => console.log(JSON.stringify({ topic: m.topic, lines: m.lines, upload: m.upload || {}, camera: m.camera || {} })))", d / "scenario.js")
    lines = sc["lines"]; place = sc["topic"]["place"]
    style = (sc.get("upload") or {}).get("stijl") or ("B-gravity" if tl.get("tripod") else "A-pov")
    cands = candidates(place, tl, {k: v for k, v in (tlj.get('SHOTS') or {}).items() if not k.startswith('auto-')})
    vocab = {w for c in cands.values() for w in c.get("shows", [])}
    tags = tag_lines(grok, lines, vocab, style, wish)
    script_cam(tags, sc.get("camera") or {}, cands)
    times = line_times(d, lines, tl)
    write_extra(d, cands)
    segs = plan(lines, times, tags, cands, style, tl)
    if use_look:
        try: look(grok, d, slug, segs, lines, tags)
        except Exception as e: print("director: could not compare shots:", str(e)[:300])
    write_shots(d, segs, cands)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("number", type=int)
    ap.add_argument("--no-look", action="store_true", help="rules only, no rendered comparison (free)")
    ap.add_argument("--wish", default="", help="what the owner wants from the camera (Dutch is fine)")
    a = ap.parse_args()
    from make_whatif import find_topic, load_env
    load_env()
    direct(find_topic(a.number), use_look=not a.no_look, wish=a.wish)


if __name__ == "__main__":
    main()
