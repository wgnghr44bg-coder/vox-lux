#!/usr/bin/env python3
"""Topic -> topics/<slug>/scenario.js, written by xAI Grok (no Claude or Codex needed).

    python whatif-demo/make_topic.py "What if the Sun disappeared?"      # new topic; prints NUMBER=<nr>
    python whatif-demo/make_topic.py --fix 45 "more people on the street, end on a sunrise"

How: Grok first picks the closest existing Short (place, force, style A/B) from the engine catalogue, then writes
the new scenario.js with that Short as the example. The engine itself checks the file (load, timeline, 3 test
frames without voice, free); on an error Grok gets the message and tries again (max. 3x). Cost: see the
'grok:' lines (xAI, paid per token; a few cents per topic). The key is XAI_API_KEY in whatif-demo/.env.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_whatif import load_env, auth, TOPICS  # noqa: E402

MODEL = os.environ.get("WHATIF_MODEL", "grok-4.3")
ENGINE = HERE / "engine"
COST = {"usd": 0.0}


# ------------------------------------------------------------------ Grok
def grok(messages, json_mode=False) -> str:
    import requests
    body = {"model": MODEL, "messages": messages, "temperature": 0.7}
    if json_mode: body["response_format"] = {"type": "json_object"}
    for k in range(4):
        try:
            r = requests.post("https://api.x.ai/v1/chat/completions", json=body,
                              headers=auth("XAI_API_KEY", "Authorization", "Bearer "), timeout=600)
            if r.ok: break
            err = f"HTTP {r.status_code}: {r.text[:300]}"
            if r.status_code in (400, 401, 403, 404): sys.exit(f"xAI {err}")
        except requests.RequestException as e:
            err = str(e)
        if k == 3: sys.exit(f"xAI failed: {err}")
        time.sleep(2 ** (k + 1))
    data = r.json(); u = data.get("usage", {})
    ticks = u.get("cost_in_usd_ticks")
    usd = ticks / 1e10 if ticks else (u.get("prompt_tokens", 0) * 1.25 + u.get("completion_tokens", 0) * 2.5) / 1e6
    COST["usd"] += usd
    print(f"grok: {u.get('prompt_tokens', '?')} in / {u.get('completion_tokens', '?')} out tokens, ~${usd:.3f}", flush=True)
    return data["choices"][0]["message"]["content"]


# ------------------------------------------------------------------ what the engine has
def header(f: Path) -> str:
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.startswith("//"): break
        out.append(line)
    return "\n".join(out)


def place_shots(f: Path) -> list[str]:
    s = re.sub(r"//[^\n]*", "", f.read_text(encoding="utf-8"))          # comments out
    m = re.search(r"(?:const shots|SHOTS)\s*=\s*\{", s) or [m for m in re.finditer(r"shots: \{", s)][-1:] or [None]
    m = m if not isinstance(m, list) else m[0]
    if not m: return []
    i = m.end() - 1; depth, j = 0, i
    for j in range(i, len(s)):
        depth += {"{": 1, "}": -1}.get(s[j], 0)
        if depth == 0: break
    body = s[i + 1:j]; names, d = [], 0
    for m in re.finditer(r"[{}]|(['\"]?)([\w-]+)\1\s*:", body):
        if m.group(0) == "{": d += 1
        elif m.group(0) == "}": d -= 1
        elif d == 0 and m.group(2) not in names: names.append(m.group(2))
    return names


def catalogue() -> str:
    parts = ["PLACES (engine/places/<name>.js) with their camera shots:"]
    for f in sorted((ENGINE / "places").glob("*.js")):
        parts.append(f"\n## place '{f.stem}'  shots: {', '.join(place_shots(f)) or '(see example)'}\n{header(f)}")
    parts.append("\nFORCES (engine/forces/<name>.js):")
    for f in sorted((ENGINE / "forces").glob("*.js")):
        if f.stem != "base": parts.append(f"\n## force '{f.stem}'\n{header(f)}")
    return "\n".join(parts)


def scenarios() -> list[dict]:
    out = []
    for f in sorted(TOPICS.glob("*/scenario.js")):
        s = f.read_text(encoding="utf-8")
        g = lambda k: (re.search(rf"\b{k}:\s*['\"]([^'\"]+)", s) or [None, ""])[1]
        n = re.search(r"\bnumber:\s*(\d+)", s)
        out.append({"slug": f.parent.name, "number": int(n[1]) if n else 0, "place": g("place"), "force": g("force"),
                    "question": g("question"), "stijl": g("stijl"), "wide": bool(re.search(r"\bwide:\s*true", s)),
                    "lines": s.count("\n  ['")})
    return out


def blocks() -> str:
    a = (HERE / "AUTOMATISCH.md").read_text(encoding="utf-8")
    i = a.find("### De engine"); j = a.find("Past het onderwerp niet", i)
    return a[i:j].strip() if i >= 0 else ""


def rules() -> str:
    a = (HERE / "AUTOMATISCH.md").read_text(encoding="utf-8")
    i, j = a.find("Script-regels:"), a.find("### De engine")
    style = (HERE / "regels" / "stijl-afwisseling.md").read_text(encoding="utf-8")
    return a[i:j] + "\n" + style.split("Werkwijze:")[0] + "\nUnits: always metric (°C, m, km, km/h, kg), 24-hour clock."


def next_number() -> int:
    nums = [int(m) for m in re.findall(r"^\|\s*(\d+)\s*\|", (HERE / "onderwerpen.md").read_text(encoding="utf-8"), re.M)]
    used = {s["number"] for s in scenarios()}          # chapters of long videos use 101, 411, 3501 ...
    n = max(nums) + 1
    while n in used: n += 1
    return n


# ------------------------------------------------------------------ checking with the engine (free, no voice)
def check(d: Path) -> str | None:
    """None when fine, else the problem in words (goes back to Grok)."""
    js = ("import(process.argv[1]).then(m => { const L = m.lines; if (!Array.isArray(L) || !m.topic || !m.default || !m.upload) "
          "throw new Error('scenario.js needs exports topic, lines, default function and upload'); "
          "console.log(JSON.stringify({ topic: m.topic, lines: L })) })")
    r = subprocess.run(["node", "-e", js, (d / "scenario.js").as_uri()], capture_output=True, text=True, encoding="utf-8")
    if r.returncode: return "The file does not load in Node:\n" + r.stderr[-1500:]
    sc = json.loads(r.stdout); lines = sc["lines"]; problems = []
    words = sum(len(re.sub(r"\[[^\]]+\]", " ", t).split()) for _, t, _ in lines)
    if not 175 <= words <= 205:
        cnt = lambda t: len(re.sub(r"\[[^\]]+\]", " ", t).split())
        per = "\n".join(f"  {i}: now {cnt(t)} -> make it {max(3, round(cnt(t) * 190 / words))} words" for i, t, _ in lines)
        problems.append(f"The narration has {words} words in total; it must be 175-205. Do NOT add or remove lines and keep "
                        f"all ids; only rewrite each text to this exact word count (count every word):\n{per}")
    if not lines[0][1].startswith("Imagine"): problems.append("The first line must start with 'Imagine'.")
    if len({l[0] for l in lines}) != len(lines): problems.append("Line ids must be unique.")
    for f in ("timing.json", "timeline.json"): (d / f).unlink(missing_ok=True)   # estimated timing from the word count
    r = subprocess.run(["node", str(ENGINE / "render.mjs"), d.name, "timeline"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    if r.returncode or "ERR " in out or not (d / "timeline.json").exists():
        return "\n".join(problems + ["The engine fails while building the timeline:\n" + out[-2000:]])
    tl = json.loads((d / "timeline.json").read_text(encoding="utf-8"))["TL"]
    t_end = tl["T_END"]
    r = subprocess.run(["node", str(ENGINE / "render.mjs"), d.name, "stills", f"{t_end * .2:.1f}", f"{t_end * .6:.1f}", f"{t_end * .9:.1f}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = r.stdout + r.stderr
    if r.returncode or "ERR " in out:
        problems.append("The engine fails while rendering frames:\n" + out[-2000:])
    if not 45 <= t_end <= 110: problems.append(f"The video would last {t_end:.0f} s; a Short must be 50-100 s.")
    return "\n".join(problems) or None


def line_times(lines, off: float = .8):
    """(start, end) per line in video seconds, with the same word-count estimate as engine/timeline.js (no voice yet)."""
    pause = {"none": 0, "": .3, "pause": .5, "long": 1.0}; at = 0.0; out = []
    for _, text, pz in lines:
        words = len(re.sub(r"\[[^\]]+\]", " ", text).split())
        dur = words / 2.55 + max(0, len(re.findall(r"[.!?](\s|$)", text)) - 1) * .3 + text.count(",") * .35
        out.append((at + off, at + off + dur))
        at += dur + (pz if isinstance(pz, (int, float)) else pause.get(pz or "", .3))
    return out


def review(d: Path) -> str | None:
    """Grok checks every sentence: one frame at the end of each line (estimated timing, no voice, free to render),
    all in one grid, next to what the voice says there. Returns the problems in words, or None when it looks right."""
    import base64
    js = "import(process.argv[1]).then(m => console.log(JSON.stringify(m.lines)))"
    lines = json.loads(subprocess.run(["node", "-e", js, (d / "scenario.js").as_uri()], capture_output=True, text=True, check=True).stdout)
    tl = json.loads((d / "timeline.json").read_text(encoding="utf-8"))["TL"]
    tt = line_times(lines, tl.get("VO_OFFSET", .8))
    times = [f"{max(s + .3, e - .2):.1f}" for s, e in tt][:20]
    subprocess.run(["node", str(ENGINE / "render.mjs"), d.name, "stills", *times], capture_output=True, check=True)
    st = d / "stills"; cols = 4; rows = -(-len(times) // cols)
    ins = sum([["-i", str(st / f"still-{t}.jpg")] for t in times], [])
    layout = "|".join(f"{k % cols * 270}_{k // cols * 480}" for k in range(len(times)))
    grid = st / "controle.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex",
                    "".join(f"[{k}]scale=270:480[s{k}];" for k in range(len(times))) + "".join(f"[s{k}]" for k in range(len(times))) +
                    f"xstack=inputs={len(times)}:layout={layout}:fill=black", str(grid)], check=True)
    said = "\n".join(f"frame {k + 1} ({lid}, {t} s): voice says \"{lines[k][1]}\"" for k, (t, (lid, _, _)) in enumerate(zip(times, lines)))
    img = base64.b64encode(grid.read_bytes()).decode()
    ans = grok([{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img}},
        {"type": "text", "text": f"A grid of {len(times)} frames (4 per row, left to right, top to bottom) from a low-poly 3D 'What if' Short. "
         "Each frame is taken at the END of one narration line:\n" + said +
         "\n\nFor each frame: is what the voice says VISIBLE in that frame (water at that height, cars floating, buildings "
         "falling, people, the named object...)? Also flag numbers on screen that contradict the voice, impossible values, "
         "empty/broken pictures or the camera inside an object. Ignore style and taste. Answer JSON: "
         "{\"ok\": true|false, \"problems\": [\"line <id>: voice says ... but the frame shows ...\"]}"}]}], json_mode=True)
    try: r = json.loads(ans)
    except json.JSONDecodeError: return None
    probs = [p for p in r.get("problems", []) if p] if not r.get("ok") else []
    print("review:", "OK" if not probs else "\n  " + "\n  ".join(probs))
    return "\n".join(f"- {p}" for p in probs) or None


def write_reviewed(d: Path, messages: list) -> bool:
    """Write + engine check, then up to 3 rounds of: Grok looks at a frame per sentence and fixes what does not match."""
    if not write_loop(d, messages): return False
    for k in range(3):
        problem = review(d)
        if not problem: return True
        messages += [{"role": "assistant", "content": (d / "scenario.js").read_text(encoding="utf-8")},
                     {"role": "user", "content": "Looking at a rendered frame at the end of every line, these things are wrong:\n" + problem +
                      "\nFix them: change the force parameters, counter, beats and shots so it really happens at that line, or, if the "
                      "engine cannot show it, rewrite the line (and add it to `missing`). Output the full corrected scenario.js."}]
        good = (d / "scenario.js").read_text(encoding="utf-8")
        if not write_loop(d, messages):
            (d / "scenario.js").write_text(good, encoding="utf-8"); check(d); return True
    return True


def save_missing(d: Path):
    """Things the story wanted but the engine cannot show yet -> engine/WENSEN.md (to build later, then kept for good)."""
    js = "import(process.argv[1]).then(m => console.log(JSON.stringify(m.missing || [])))"
    try: miss = json.loads(subprocess.run(["node", "-e", js, (d / "scenario.js").as_uri()], capture_output=True, text=True, check=True).stdout)
    except Exception: return
    if not miss: return
    f = ENGINE / "WENSEN.md"
    old = f.read_text(encoding="utf-8") if f.exists() else "# Wensen: bouwstenen die nog ontbreken\n\nGrok noteert hier wat een verhaal nodig had maar de engine nog niet kan tonen.\nWat gebouwd is, blijft in de engine en is daarna voor elke video beschikbaar.\n\n"
    new = "".join(f"- [ ] {m}  (gevraagd door {d.name}, {dt.date.today()})\n" for m in miss if m.lower() not in old.lower())
    if new: f.write_text(old + new, encoding="utf-8"); print("ontbreekt nog (in engine/WENSEN.md):\n  " + "\n  ".join(miss))


def extract_js(text: str) -> str:
    m = re.search(r"```(?:js|javascript)?\s*\n(.*?)```", text, re.S)
    return (m[1] if m else text).strip() + "\n"


SYSTEM = """You write scenario files for IfScape3D, a YouTube/TikTok channel with low-poly 3D 'What if' Shorts.
A Three.js engine renders the video from a scenario.js file; you only write that file. Use ONLY places, forces, shots,
beats and options that exist in the engine or in the example scenario. Physics must be correct; when unsure about
a number, leave it out. English narration in second person ("you").
What the voice says must be VISIBLE: read the heights and positions in the place header (e.g. in river-city the river
lies at y -10 and the quays at y 0, so water must rise more than 10 m before a street floods) and choose the force
parameters, counter and shots so that every step the narration names really happens on screen at that moment.
How the force follows the counter: level = (counter - range[0]) / (range[1] - range[0]), 0..1. For the water force the water
height above normal = forceParams.rise * level, so use counter values in metres above normal, range [0, R] and rise R:
then the counter on screen and the real water always agree. Use the heights in the place header (e.g. cars float from
+10.6 in river-city) and let the counter pass those heights at the line that names them.
Events need their beat: cars stop/float -> beats.carsStop before it (and water above the float height); people go inside
-> beats.shelter; buildings collapse -> beats.falls; a bridge breaks -> beats.deckBreak (river-city).
NEVER narrate something the engine cannot show (no place, building block, beat or option for it). Leave it out and list
it in the export `missing` (array of short English descriptions) so it can be built later: export const missing = [...]; Output only the complete scenario.js in one ```js block."""


def write_loop(d: Path, messages: list, tries: int = 4) -> bool:
    for k in range(tries):
        (d / "scenario.js").write_text(extract_js(grok(messages)), encoding="utf-8")
        problem = check(d)
        if not problem:
            print("check: OK (loads, timeline, 3 test frames)"); return True
        print(f"check {k + 1}/{tries}: problem ->\n  " + problem[:600].replace("\n", "\n  "))
        messages += [{"role": "assistant", "content": (d / "scenario.js").read_text(encoding="utf-8")},
                     {"role": "user", "content": "The engine check found a problem. Fix it and output the full corrected scenario.js.\n\n" + problem}]
    return False


def new_topic(question: str):
    q = question.strip().rstrip("?") + "?"
    if not q.lower().startswith("what if"): q = "What if " + q[0].lower() + q[1:]
    known = [s for s in scenarios() if not s["wide"] and s["lines"] >= 8 and s["stijl"]]
    lijst = (HERE / "onderwerpen.md").read_text(encoding="utf-8")
    last = max(known, key=lambda s: s["number"]) if known else None
    want_style = "B-gravity" if last and last["stijl"].startswith("A") else "A-pov"

    plan = json.loads(grok([
        {"role": "system", "content": "You plan IfScape3D What if Shorts. Answer in JSON only."},
        {"role": "user", "content": f"New topic: {q}\n\nTopics already made or planned (onderwerpen.md):\n{lijst}\n\n"
         f"Existing Short scenarios to use as example:\n{json.dumps(known, indent=0)}\n\n{catalogue()}\n\n"
         "Answer with JSON: {\"exists\": true ONLY if this topic (or the same idea) was already MADE (on the channel, or status starting with 'gemaakt'/'klaar'), "
         "\"planned\": the number of a row with the same idea that is only planned (status 'gepland'), else null, "
         "\"slug\": short-kebab-case, \"place\": one existing place, \"force\": one existing force, "
         "\"example\": slug of the existing Short scenario that is closest (prefer the same place, then the same force), "
         "\"summary\": one line in Dutch: what happens, with the counter (e.g. 'Zon 100% -> 0%: ...')}"}], json_mode=True))
    print("plan:", json.dumps(plan, ensure_ascii=False))
    if plan.get("exists"):
        print("EXISTS"); sys.exit(3)
    slug = re.sub(r"[^a-z0-9-]", "", plan["slug"].lower())[:40] or "topic"
    while (TOPICS / slug).exists(): slug += "-2"
    ex = TOPICS / plan["example"] / "scenario.js"
    if not ex.exists(): ex = TOPICS / "moon-closer" / "scenario.js"
    planned = plan.get("planned")
    num = int(planned) if planned and not any(sc["number"] == int(planned) for sc in scenarios()) else next_number()
    d = TOPICS / slug; d.mkdir(parents=True)
    pf, ff = ENGINE / "places" / f"{plan['place']}.js", ENGINE / "forces" / f"{plan['force']}.js"
    msg = [{"role": "system", "content": SYSTEM}, {"role": "user", "content":
        f"Write topics/{slug}/scenario.js for: {q}\n"
        f"The narration (all texts in `lines`) must be 175-205 words in total - about 15-18 lines of 10-14 words; count them.\n"
        f"topic: number {num}, slug '{slug}', place '{plan['place']}', force '{plan['force']}', question '{q}'. Style: {want_style}.\n"
        f"Story outline: {plan.get('summary', '')}\n\n"
        f"RULES (from the channel owner, Dutch):\n{rules()}\n\n"
        f"PLACE {plan['place']} (header; shots: {', '.join(place_shots(pf)) if pf.exists() else '?'}):\n{header(pf) if pf.exists() else ''}\n\n"
        f"FORCE {plan['force']}:\n{header(ff) if ff.exists() else ''}\n\n"
        f"ALL BUILDING BLOCKS OF THE ENGINE (Dutch):\n{blocks()}\n\n"
        f"EXAMPLE scenario ({ex.parent.name}) - copy its structure exactly, change the content:\n```js\n{ex.read_text(encoding='utf-8')}```\n\n"
        f"Second example (gravity-doubled):\n```js\n{(TOPICS / 'gravity-doubled' / 'scenario.js').read_text(encoding='utf-8')}```"}]
    ok = write_reviewed(d, msg)
    save_missing(d)
    row = f"| {num} | {q[8:]} (Short, stijl {want_style[0]}) | {plan['place']} | {plan.get('summary', '')} | in de maak {dt.date.today()} (automatisch, Grok); topics/{slug} |"
    text = lijst.splitlines(); same = [i for i, l in enumerate(text) if re.match(rf"^\|\s*{num}\s*\|", l)]
    if same: text[same[0]] = row                    # a planned topic: its row gets the new status
    else: text.insert(max(i for i, l in enumerate(text) if re.match(r"^\|\s*\d+\s*\|", l)) + 1, row)
    (HERE / "onderwerpen.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    print(f"topic {num}: topics/{slug}/scenario.js  ({'OK' if ok else 'NOT OK - see the problems above'}), total ~${COST['usd']:.2f}")
    print(f"NUMBER={num}")
    sys.exit(0 if ok else 2)


def fix_topic(num: int, feedback: str):
    from make_whatif import find_topic
    d = find_topic(num); s = (d / "scenario.js").read_text(encoding="utf-8")
    msg = [{"role": "system", "content": SYSTEM}, {"role": "user", "content":
        f"RULES:\n{rules()}\n\nThis is topics/{d.name}/scenario.js:\n```js\n{s}```\n\n"
        f"The channel owner looked at the 6 test frames and asks:\n{feedback}\n\n"
        "Change the scenario accordingly (keep everything else) and output the full scenario.js."}]
    backup = d / "scenario.vorige.js"; backup.write_text(s, encoding="utf-8")
    ok = write_reviewed(d, msg)
    save_missing(d)
    if not ok: backup.replace(d / "scenario.js"); print("kept the previous version")
    else: backup.unlink()
    print(f"total ~${COST['usd']:.2f}")
    sys.exit(0 if ok else 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("topic", nargs="*", help='e.g. "What if the Sun disappeared?"')
    ap.add_argument("--fix", type=int, metavar="NR", help="adjust an existing topic with feedback (the words after it)")
    a = ap.parse_args()
    load_env()
    text = " ".join(a.topic).strip()
    if not text: ap.error("give a topic")
    if a.fix: fix_topic(a.fix, text)
    else: new_topic(text)


if __name__ == "__main__":
    main()
