#!/usr/bin/env python3
"""Bouwt script-cues.txt volgens stories/OPBOUW.md: src/begin.txt, src/deel1-6.txt (TOPIC/BRIDGE + IMG/HEAD/BODY), src/slot.txt."""
import subprocess, sys
from pathlib import Path
d = Path(__file__).parent
subprocess.run([sys.executable, str(d.parent.parent / "tools" / "bouw_feiten.py"), str(d), "--src", "src"], check=True)
