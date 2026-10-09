"""Animal and nature sounds for the What if engine (used by make_audio.py).

  s_jungle   prehistoric valley ambience: insects, far calls, river, soft wind
  s_stomp    a heavy footstep: low thud the ground carries (size e)
  s_roar     calls: roar (T. rex), boom (long-neck), bellow (triceratops), hiss (raptor), trumpet (elephant/mammoth)
  s_flyby    a rock (or anything huge) tearing across the sky: rising roar, crackle, low boom
"""
from __future__ import annotations

import numpy as np

from make_audio import SR, bp, lp, hp, brown, norm, lfo, stereo, pan, env_ad, smooth, s_water


def s_jungle(rng, sec=30):
    n = int(sec * SR); t = np.arange(n) / SR

    def insects(r):
        chirp = np.clip(np.sin(2 * np.pi * r.uniform(18, 26) * t), 0, None) ** 3
        swell = np.clip(lfo(r, n, .08, .9), .1, None)
        return bp(r.standard_normal(n), 3800, 6500) * chirp * swell * .35 + bp(r.standard_normal(n), 2400, 3200) * np.clip(lfo(r, n, .3, 1), 0, None) * .12
    x = norm(stereo(rng, insects, .9), .35)
    x += s_water(rng, sec) * .35
    x += norm(stereo(rng, lambda r: bp(brown(r, n), 150, 900) * lfo(r, n, .05, .7), .8), .2)
    for _ in range(int(sec / 4)):          # far calls: low hoots and short whistles
        L = int(rng.uniform(.4, 1.0) * SR); tt = np.arange(L) / SR; p = int(rng.uniform(0, sec - 1.2) * SR)
        f = rng.choice([180, 320, 1400]) * (1 + .15 * np.sin(np.pi * tt / tt[-1]))
        call = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]) ** 2 * rng.uniform(.03, .07)
        x[p:p + L] += pan(call, rng.uniform(-.8, .8))
    return x


def s_stomp(rng, e=1.0):
    n = int(1.6 * SR); t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * np.cumsum(30 + 40 * np.exp(-t * 9)) / SR) * env_ad(n, .006, .35 + .2 * e)
    body = lp(rng.standard_normal(n), 180) * env_ad(n, .003, .12) * .8
    rustle = bp(rng.standard_normal(n), 900, 4000) * env_ad(n, .01, .08) * .12
    rattle = bp(rng.standard_normal(n), 120, 500) * env_ad(n, .02, .6) * .25 * e
    return norm(thud + body + rustle + rattle)


def _growl(rng, n, f0, rasp, form):
    t = np.arange(n) / SR
    jit = 1 + .04 * lfo(rng, n, 7, 1) + .02 * lfo(rng, n, 23, 1)
    f = f0 * jit
    saw = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k ** .8 for k in range(1, 18))
    am = 1 + rasp * np.sin(2 * np.pi * np.cumsum(28 + 6 * lfo(rng, n, 1.5, 1)) / SR)
    voiced = sum(bp(saw * am, a, b) * g for (a, b, g) in form)
    noise = sum(bp(rng.standard_normal(n), a, b) * g * .6 for (a, b, g) in form) * am
    return voiced + noise * .5 + lp(saw, 140) * .8


def s_roar(rng, call="roar", dur=2.6, e=1.0):
    n = int((dur + .8) * SR); t = np.arange(n) / SR
    env = smooth(0, .35, t) * (1 - smooth(dur - .6, dur + .3, t))
    if call == "roar":       # T. rex: deep, rasping, falling pitch
        f0 = 62 - 14 * t / dur
        x = _growl(rng, n, f0, .6, [(200, 600, 1.0), (700, 1400, .55), (1800, 3200, .18)])
    elif call == "boom":     # long-neck: very low hum through closed mouth
        x = _growl(rng, n, 34 + 4 * np.sin(t * 1.5), .15, [(60, 300, 1.0), (300, 700, .25)])
    elif call == "bellow":   # triceratops: mid, short, nasal
        x = _growl(rng, n, 115 - 25 * t / dur, .35, [(250, 900, 1.0), (1000, 2000, .4)])
    elif call == "hiss":     # raptor: hiss + clicks + a short screech
        x = bp(rng.standard_normal(n), 2000, 7000) * .6
        for k in range(int(dur * 6)):
            p = int(rng.uniform(0, dur) * SR); L = int(.01 * SR)
            if p + L < n: x[p:p + L] += hp(rng.standard_normal(L), 1500) * 2
        L = int(.5 * SR); tt = np.arange(L) / SR; p = int(dur * .3 * SR)
        x[p:p + L] += np.sin(2 * np.pi * np.cumsum(900 + 600 * np.sin(np.pi * tt / tt[-1])) / SR) * np.sin(np.pi * tt / tt[-1]) * .8
    else:                    # trumpet: elephant / mammoth
        f0 = 420 + 120 * np.sin(np.pi * np.minimum(1, t / dur)) + 12 * np.sin(2 * np.pi * 7 * t)
        x = sum(np.sin(2 * np.pi * np.cumsum(f0 * k) / SR) / k for k in range(1, 9)) + bp(rng.standard_normal(n), 800, 3000) * .3
    x = norm(x * env)
    # a little air: short room echo
    out = x.copy()
    for d, g in ((.07, .25), (.16, .14), (.31, .08)):
        k = int(d * SR); out[k:] += x[:-k] * g
    return norm(out) * min(1.0, .5 + .5 * e)


def s_flyby(rng, dur=8.0):
    n = int((dur + 3) * SR); t = np.arange(n) / SR
    u = np.clip(t / dur, 0, 1); env = np.sin(np.pi * u) ** 1.5 * (t < dur) + 0
    roar = lp(brown(rng, n), 300) * env
    tear = bp(rng.standard_normal(n), 500, 3500) * env ** 2 * .35
    crack = np.zeros(n)
    for _ in range(int(dur * 18)):
        p = int(rng.uniform(.2, .9) * dur * SR); L = int(rng.uniform(.004, .02) * SR)
        crack[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(.1, .6)
    boom_at = int(dur * .55 * SR); tb = np.arange(n - boom_at) / SR
    boom = np.zeros(n); boom[boom_at:] = np.sin(2 * np.pi * np.cumsum(28 + 30 * np.exp(-tb * 3)) / SR) * np.exp(-tb * .9)
    mono = norm(roar) + tear + bp(crack, 600, 6000) * .5 + boom * .7
    # pans from left to right as it crosses the sky
    p = np.interp(t, [0, dur], [-.8, .8])
    return np.stack([mono * np.sqrt((1 - p) / 2), mono * np.sqrt((1 + p) / 2)], 1)
