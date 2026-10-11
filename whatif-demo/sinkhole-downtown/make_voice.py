#!/usr/bin/env python3
"""Voice for the sinkhole Short: the LINES from scene.html in one xAI Atlas take (make_whatif.one_take,
speed 1.00 on request of the owner, documentary pauses) -> voice.mp3, voice-times.tsv, timing.json (read by scene.html).
    node render.mjs timeline && python3 make_voice.py"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import make_whatif as M

SPEED = 1.00   # eigenaar, 11 okt 2026: tempo 1.00 voor deze Short
lines = json.loads((HERE / "timeline.json").read_text())["LINES"]
M.one_take(HERE, lines, SPEED)
rows = M.parse_tsv(HERE / "voice-times.tsv")
t = M.timing_from_tsv(lines, rows, offset=1.0)
(HERE / "timing.json").write_text(json.dumps(t, indent=1))
(HERE / "script.txt").write_text(M.script_text(lines), encoding="utf-8")
print(json.dumps(t["lines"]))
