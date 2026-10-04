"""Sound bed for 'What if the Internet disappeared?' (python3 whatif-demo/make_audio.py whatif-demo/internet-gone).

City -> notification pings that die out -> screens clicking off, error beep, shutters -> horns, murmur, siren -> silence, wind.
"""
import json
from pathlib import Path

import numpy as np
from make_audio import (SR, library, place, smooth, db, lp, bp, brown, norm, stereo, lfo, pan,
                        s_ping, s_toeter, s_uitval, s_rolluik)


def build(topic: Path):
    data = json.loads((topic / "timeline.json").read_text())
    TL, EV = data["TL"], data["EVENTS"]
    B = TL["beats"]; T = TL["T_END"]; Q = B["quiet"]
    n = int(T * SR); t = np.arange(n) / SR
    lib = library(); rng = np.random.default_rng(23)
    loop = (lambda x: np.tile(x, (int(T * SR / len(x)) + 2, 1))[:n])
    live = (1 - smooth(Q - .9, Q - .05, t))[:, None]          # everything of the busy street stops in the dip to black
    bed = np.zeros((n, 2))

    # 1. city: traffic bed + passing cars until the traffic locks up, then idling engines
    bed += loop(lib["stad"]) * db(-13) * (1 - smooth(B["nav"], B["jam"] + 2, t) * .6)[:, None]
    for tc in np.arange(1.5, B["nav"] + 1, 3.1):
        place(bed, lib["auto"], tc + rng.uniform(0, 1.5), db(-15) * (1 - smooth(B["nav"] - 4, B["nav"] + 1, tc)))
    idle = stereo(rng, lambda r: norm(lp(brown(r, n), 160) * lfo(r, n, .3, .3)), .6)
    bed += idle * (db(-20) * smooth(B["nav"], B["jam"] + 3, t))[:, None]
    # 2. tension: very soft drone from "Now imagine it simply stops"
    bed += loop(lib["drone"]) * (db(-36) + db(-24) * smooth(26, 40, t) + db(-22) * smooth(60, B["climax"], t))[:, None]
    # 3. crowd murmur: starts when people stop, swells into the climax
    bed += loop(lib["stemmen"]) * (db(-30) * smooth(B["stopWalk"], B["eachOther"] + 1, t) + db(-16) * smooth(B["evening"], B["climax"] + 2, t)
                                   + db(-10) * smooth(B["climax"], B["climax"] + 4, t))[:, None]

    # 4. events from the scene
    for e in EV:
        k, tt, x = e["kind"], e["t"], e.get("x", 0)
        if k == "ping":
            place(bed, s_ping(rng, e["pitch"]), tt, db(-23), np.clip(x, -.8, .8))
        elif k == "glitch":
            for j in range(3): place(bed, lib["uitval"], tt + j * .22, db(-20), rng.uniform(-.5, .5))
        elif k == "screen":
            s = s_uitval(rng); far = e.get("z", 0) < -150
            place(bed, lp(s, 1500) if far else s, tt, db(-21 if far else -13), np.clip(x, -.9, .9))
        elif k == "atm":
            place(bed, lib["foutpiep"], tt, db(-11), .6)
        elif k == "shutter":
            place(bed, s_rolluik(rng), tt, db(-14) / (1 + max(0, 20 - e.get("z", 0)) / 60), .75)
        elif k == "horn":
            d = max(4, 44 - e["z"])
            h = s_toeter(rng, e["len"], e["pitch"]); h = lp(h, 4000 if d < 40 else 1500)
            place(bed, h, tt, db(-6) / (1 + d / 25), np.clip(e["x"] / 14, -.8, .8))
        elif k == "siren":
            sir = np.tile(lib["sirene"], (3, 1))
            sir = sir * smooth(0, 4, np.arange(len(sir)) / SR)[:, None]
            place(bed, sir, tt, db(-15))
    bed *= live
    k = int(.03 * SR); i0 = int(Q * SR)

    # 5. after: silence, then only wind
    wind = loop(lib["wind"])
    bed += wind * (db(-17) * smooth(Q + .4, Q + 3, t) * (1 - smooth(B["fade"], T - .05, t)))[:, None]
    bed += loop(lib["drone"]) * (db(-30) * smooth(Q + 1, Q + 4, t) * (1 - smooth(B["fade"], T, t)))[:, None]
    return bed
