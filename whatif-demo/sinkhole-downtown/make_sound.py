#!/usr/bin/env python3
"""Sound for the sinkhole Short, from the make_audio.py library: city, a car or two, water at the pipe, creaks and
cracks, a far siren, the drop (deep rumble + rubble), pieces sliding in while the hole grows, the corner building.
Mix as make_audio.mix_engine: bed ducked 8 dB under the voice, -14 LUFS, peak -1 dB.
    node render.mjs timeline && python3 make_sound.py   -> mix.wav"""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import make_audio as A
from make_audio import SR, db, place, smooth, lp, bp, brown, norm, env_ad, stereo, lfo


def build(topic: Path):
    data = json.loads((topic / "timeline.json").read_text())
    TL, EV = data["TL"], data["EVENTS"]; B = TL["beats"]; T = TL["T_END"]
    n = int(T * SR); t = np.arange(n) / SR
    lib = A.library(); rng = np.random.default_rng(5)
    bed = np.zeros((n, 2))
    loop = lambda k: np.tile(lib[k], (int(T / (len(lib[k]) / SR)) + 2, 1))[:n]
    # city: busy until the drop, then hushed
    bed += loop("stad") * (db(-12) * (1 - .8 * smooth(B["dip"], B["police"] + 2, t)) * (1 - .7 * smooth(B["drop"], B["drop"] + 3, t)))[:, None]
    for tc in (1.5, 5.0, 8.5, 12.0):
        place(bed, lib["auto"], tc, db(-15), rng.uniform(-.5, .5))
    # water bubbling at the manhole
    w = stereo(rng, lambda r: norm(bp(r.standard_normal(n), 300, 2400) * np.clip(lfo(r, n, 3.1, 1.2), 0, None)), .5)
    bed += w * (db(-30) * smooth(B["pipe"], B["pipe"] + 1.5, t) * (1 - smooth(B["drop"] - 1, B["drop"], t)))[:, None]
    # the road gives: creaks, cracks, low grumble under the street
    place(bed, A.s_kraak(rng), B["dip"], db(-8), -.2)
    for k, tc in enumerate((B["cracks"], B["cracks"] + .7, B["cracks"] + 1.5, B["police"] + 1.2, B["police"] + 3.5)):
        place(bed, A.s_barst(rng), tc, db(-6 - 2 * k), rng.uniform(-.6, .6))
    rum = loop("gerommel")
    bed += rum * (db(-30) * smooth(B["dip"], B["cracks"] + 2, t) + db(-14) * smooth(B["police"] + 2, B["drop"], t) * (1 - smooth(B["drop"] + 4, B["size"] + 4, t))
                  + db(-20) * smooth(B["grow"] - .5, B["grow"] + 1, t) * (1 - smooth(B["grow"] + 7, B["china"] + 3, t)))[:, None]
    # a far siren when the police arrive
    sir = A.s_siren(rng, 12.0)
    place(bed, sir * (1 - smooth(8, 12, np.arange(len(sir)) / SR))[:, None], B["police"] - .3, db(-24))
    # the drop: a deep roar, rubble pouring in, impacts far below
    L = int(9 * SR); roar = norm(lp(brown(rng, L), 120)) * env_ad(L, .25, 3.0)
    place(bed, np.stack([roar, roar], 1), B["drop"] - .1, db(-1))
    place(bed, lib["puin"], B["drop"] + .1, db(-5), -.3); place(bed, lib["puin"], B["drop"] + .6, db(-7), .3)
    for j in range(7):
        place(bed, lp(A.s_klap(rng, 1.3), 900), B["drop"] + .3 + j * .38 + rng.uniform(0, .25), db(-9 - j), rng.uniform(-.5, .5))
    # things on the crossing tipping over the edge (thinned)
    last = -1
    for e in EV:
        if e["kind"] == "fall" and e["t"] - last > .35:
            last = e["t"]; place(bed, lp(A.s_klap(rng, .5), 1500), e["t"] + .2, db(-24), float(np.clip(e["x"] / 40, -.8, .8)))
        elif e["kind"] == "slide" and e["e"] > .1:
            place(bed, lib["puin"], e["t"], db(-10) * e["e"] ** .5, rng.uniform(-.6, .6))
        elif e["kind"] == "building":
            L2 = int(7 * SR); r2 = norm(lp(brown(rng, L2), 160)) * env_ad(L2, .6, 2.6)
            place(bed, np.stack([r2, r2 * .9], 1), e["t"], db(-4))
            place(bed, A.s_kraak(rng), e["t"] - .6, db(-6), .4); place(bed, A.s_metaal(rng), e["t"] + .5, db(-12), .5)
            for j in range(4): place(bed, lp(A.s_klap(rng, 1.4), 1000), e["t"] + 1.2 + j * .5, db(-10 - 2 * j), .4)
    # a low drone that holds the tension, softer at the end
    bed += loop("drone") * (db(-32) + db(-22) * smooth(B["drop"], B["drop"] + 2, t) * (1 - .5 * smooth(B["q"] - 1, T, t)))[:, None]
    # dust settling: a few late trickles
    for tc in (B["china"] + 1.0, B["tall"] + .5, B["q"] + 1.2):
        place(bed, lp(lib["puin"], 1800), tc, db(-26), rng.uniform(-.6, .6))
    bed *= (1 - smooth(T - .8, T, t))[:, None]
    return bed


A.build_engine = build
A.mix_engine(HERE)
