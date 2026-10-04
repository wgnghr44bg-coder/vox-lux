#!/usr/bin/env python3
"""Synthesised sound design for a 'What if' video (no recordings, $0).

    python3 whatif-demo/make_audio.py whatif-demo/earth-stops
    python3 whatif-demo/make_audio.py whatif-demo/topics/<slug>     (engine videos: place ambience,
                                    force layer from AUDIO.level, sounds for every EVENT)

Reads <dir>/timeline.json (node render.mjs timeline: the TL object + physics events)
and <dir>/voice.mp3, writes:
    whatif-demo/sfx/*.wav     reusable one-shots and loops (stad, wind, gerommel, klap, glas, ...)
    <dir>/sfx-bed.wav         effects only, on the video timeline
    <dir>/mix.wav             voice + effects, ducked under the voice, -14 LUFS, peak -1 dB

Everything is layered noise: several bands with slow LFOs, stereo decorrelation and a
little echo. The wind follows the counter in TL (wind = counterMax - counter).
"""
from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
HERE = Path(__file__).resolve().parent
SFX = HERE / "sfx"


# ---------- basics ----------
def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x, axis=0)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "lowpass", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "highpass", fs=SR, output="sos"), x, axis=0)


def brown(rng, n):
    x = np.cumsum(rng.standard_normal(n))
    return hp(x - x.mean(), 15)


def norm(x, peak=0.9):
    return x / (np.max(np.abs(x)) or 1) * peak


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def lfo(rng, n, rate, depth):
    t = np.arange(n) / SR
    ph = rng.uniform(0, 6.3, 3)
    v = np.sin(2 * np.pi * rate * t + ph[0]) * .5 + np.sin(2 * np.pi * rate * 2.37 * t + ph[1]) * .3 \
        + np.sin(2 * np.pi * rate * 5.1 * t + ph[2]) * .2
    return 1 + depth * v


def stereo(rng, make, width=.5):
    """Two decorrelated takes of the same sound, partly shared (width 0 = mono)."""
    a, b, c = make(rng), make(rng), make(rng)
    return np.stack([c * (1 - width) + a * width, c * (1 - width) + b * width], 1)


def pan(x, p):
    """p -1..1 (scalar or per-sample), equal power."""
    p = np.asarray(p)
    ang = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(ang), x * np.sin(ang)], 1)


def echo(x, delays=(0.045, 0.11, 0.23), gains=(0.3, 0.18, 0.1)):
    y = x.copy()
    for d, g in zip(delays, gains):
        k = int(d * SR)
        y[k:] += x[:-k] * g
        # cross-feed for width
        if x.ndim == 2:
            y[k:, 0] += x[:-k, 1] * g * .4
            y[k:, 1] += x[:-k, 0] * g * .4
    return y


def env_ad(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def write(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# ---------- the sound library ----------
def s_klap(rng, size=1.0):
    """Concrete impact: low thump + crunchy burst + rubble tail."""
    n = int(2.6 * SR); t = np.arange(n) / SR
    f = 55 * size ** -.3 * np.exp(-t * 3) + 28
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, .003, .18 * size)
    burst = lp(rng.standard_normal(n), 2500) * env_ad(n, .001, .06)
    crunch = bp(rng.standard_normal(n), 300, 3000) * env_ad(n, .002, .25) * .5
    tail = np.zeros(n)
    for _ in range(int(25 * size)):
        p = int(rng.uniform(.03, 1.6) ** 1.5 * SR); L = int(rng.uniform(.005, .03) * SR)
        if p + L < n:
            tail[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(.05, .3) * np.exp(-p / SR * 1.5)
    tail = bp(tail, 400, 5000)
    return norm(thump * 1.0 + burst * .8 + crunch + tail * .9)


def s_glas(rng):
    """Shattering glass: bright bursts + many tinkling pings."""
    n = int(2.4 * SR); t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 3000) * env_ad(n, .001, .09)
    for _ in range(70):
        p = int(rng.uniform(0, 1.6) ** 1.6 * SR); L = int(.25 * SR)
        if p + L >= n: continue
        f = rng.uniform(2500, 8000); tt = np.arange(L) / SR
        ping = np.sin(2 * np.pi * f * tt) * np.exp(-tt * rng.uniform(25, 60))
        click = rng.standard_normal(L) * np.exp(-tt * 400) * .5
        x[p:p + L] += (ping + click) * rng.uniform(.1, .5) * np.exp(-p / SR * 1.2)
    return norm(x)


def s_barst(rng):
    """One sharp glass crack, then a few fine crackles as the cracks spread."""
    n = int(3.5 * SR); t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 1500) * env_ad(n, .0005, .012) * 1.5
    x += np.sin(2 * np.pi * 4200 * t) * np.exp(-t * 30) * .4 + np.sin(2 * np.pi * 6100 * t) * np.exp(-t * 45) * .3
    x += lp(rng.standard_normal(n), 900) * env_ad(n, .001, .03) * .8
    for _ in range(40):
        p = int((.05 + rng.uniform(0, 1) ** 1.8 * 3.0) * SR); L = int(.02 * SR)
        if p + L < n:
            x[p:p + L] += hp(rng.standard_normal(L), 2500) * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(.03, .18)
    return norm(x)


def s_metaal(rng):
    """Bending metal: inharmonic partials gliding down, with grinding friction."""
    n = int(3.2 * SR); t = np.arange(n) / SR
    glide = 1 - .25 * smooth(0, 3.2, t) + .02 * np.sin(2 * np.pi * 3 * t)
    x = np.zeros(n)
    for f, a in [(180, 1), (437, .6), (811, .4), (1290, .25), (2150, .12)]:
        x += np.sin(2 * np.pi * np.cumsum(f * glide * rng.uniform(.95, 1.05)) / SR) * a
    am = np.clip(lfo(rng, n, 7, .9), 0, None)
    fric = bp(rng.standard_normal(n), 600, 3000) * am * .6
    e = smooth(0, .4, t) * (1 - smooth(2.2, 3.2, t))
    return norm(echo(((x * am * .5 + fric) * e)[:, None].repeat(2, 1)))[:, 0]


def s_kraak(rng):
    """Low structural groan of a building."""
    n = int(3.5 * SR); t = np.arange(n) / SR
    f0 = 70 + 25 * np.sin(2 * np.pi * .4 * t) + rng.uniform(-10, 10)
    saw = sum(np.sin(2 * np.pi * np.cumsum(f0 * k) / SR) / k for k in range(1, 9))
    jit = np.clip(lfo(rng, n, 11, 1.0), 0, None)
    x = bp(saw * jit, 60, 900) + bp(rng.standard_normal(n), 80, 400) * .3
    return norm(x * smooth(0, .6, t) * (1 - smooth(2.4, 3.5, t)))


def s_puin(rng):
    """Rubble: many small pieces clattering down."""
    n = int(4 * SR); x = np.zeros(n)
    for _ in range(160):
        p = int(rng.uniform(0, 3.4) ** 1.2 * SR); L = int(rng.uniform(.01, .06) * SR)
        if p + L < n:
            x[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(.05, .5) * np.exp(-p / SR * .7)
    return norm(bp(x, 250, 6000) + lp(x, 300) * .5)


def s_rammel(rng):
    """Rattling: loose things knocking at a few hertz."""
    n = int(6 * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    rate = 9
    for k in range(int(6 * rate)):
        p = int((k / rate + rng.uniform(0, .05)) * SR); L = int(.03 * SR)
        if p + L < n:
            x[p:p + L] += bp(rng.standard_normal(L), 800, 4000) * np.exp(-np.arange(L) / (L / 6)) * rng.uniform(.2, 1)
    return norm(x * lfo(rng, n, .5, .6))


def s_wind(rng, sec=30):
    """Generic wind loop (light to medium) for the library."""
    n = int(sec * SR)
    return norm(stereo(rng, lambda r: bp(brown(r, n), 80, 600) * lfo(r, n, .09, .5)
                       + bp(r.standard_normal(n), 500, 1400) * .25 * lfo(r, n, .13, .8), .7))


def s_gerommel(rng, sec=20):
    """Deep rumble: brown noise 20-90 Hz + slow sub tones."""
    n = int(sec * SR); t = np.arange(n) / SR
    x = lp(brown(rng, n), 90, 4) * lfo(rng, n, .07, .5)
    x = norm(x) + np.sin(2 * np.pi * 33 * t) * .25 * lfo(rng, n, .05, .6) + np.sin(2 * np.pi * 41.5 * t) * .15
    return norm(stereo(rng, lambda r: x + lp(r.standard_normal(n), 120) * .2, .3))


def s_drone(rng, sec=30):
    """Very soft dark drone, no melody."""
    n = int(sec * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * a for f, a in [(55, 1), (55.4, .8), (82.4, .35), (110.2, .15)])
    x = x * lfo(rng, n, .03, .3) + lp(brown(rng, n), 200) * .02
    return norm(stereo(rng, lambda r: x, 0))


def s_carpass(rng, sec=5):
    n = int(sec * SR); t = np.arange(n) / SR
    c = sec / 2
    env = np.exp(-((t - c) / (sec / 5)) ** 2)
    tyre = bp(brown(rng, n), 120, 1800) * env
    hiss = hp(rng.standard_normal(n), 1800) * env ** 2 * .25
    eng = np.sin(2 * np.pi * np.cumsum(np.where(t < c, 95, 80) * (1 + .02 * np.sin(t * 9))) / SR) * env * .3
    return norm(pan(tyre + hiss + eng, np.tanh((t - c) * 1.5) * .8))


def s_stad(rng, sec=30):
    """Calm city: distant traffic bed, a few passing cars, birds."""
    n = int(sec * SR)
    bed = stereo(rng, lambda r: lp(brown(r, n), 350) * lfo(r, n, .05, .3), .6)
    x = norm(bed, .35)
    for k in range(5):
        cp = s_carpass(rng, 4 + rng.uniform(0, 2)) * rng.uniform(.25, .5)
        p = int(rng.uniform(0, sec - 7) * SR); x[p:p + len(cp)] += cp
    for _ in range(9):
        L = int(.12 * SR); tt = np.arange(L) / SR; p = int(rng.uniform(0, sec - 1) * SR)
        f = rng.uniform(2800, 4200)
        chirp = np.sin(2 * np.pi * np.cumsum(f * (1 + .3 * np.sin(tt * 60))) / SR) * np.sin(np.pi * tt / tt[-1]) * .05
        x[p:p + L] += pan(chirp, rng.uniform(-.8, .8))
    return x


def s_tik(rng):
    """Pedestrian crossing tick."""
    n = int(.08 * SR); t = np.arange(n) / SR
    return norm(np.sin(2 * np.pi * 1250 * t) * np.exp(-t * 120) + bp(rng.standard_normal(n), 1500, 4000) * np.exp(-t * 300) * .3)


def library():
    SFX.mkdir(exist_ok=True)
    rng = np.random.default_rng(7)
    lib = {
        "stad": s_stad(rng), "wind": s_wind(rng), "gerommel": s_gerommel(rng), "drone": s_drone(rng),
        "klap": s_klap(rng), "glas": s_glas(rng), "metaal": s_metaal(rng), "kraak": s_kraak(rng),
        "puin": s_puin(rng), "rammel": s_rammel(rng), "barst": s_barst(rng), "tik": s_tik(rng),
        "auto": s_carpass(rng),
    }
    lib = {k: v if v.ndim == 2 else np.stack([v, v], 1) for k, v in lib.items()}
    for k, v in lib.items():
        write(SFX / f"{k}.wav", v)
    return lib


# ---------- the bed for this video ----------
def monotone(pts):
    xs = np.array([p[0] for p in pts], float); ys = np.array([p[1] for p in pts], float)
    d = np.diff(ys) / np.diff(xs); m = np.zeros(len(xs)); m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(xs) - 1):
        m[i] = 0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2
    for i in range(len(d)):
        if d[i] == 0: m[i] = m[i + 1] = 0; continue
        a, b = m[i] / d[i], m[i + 1] / d[i]; s = a * a + b * b
        if s > 9: tau = 3 / np.sqrt(s); m[i] = tau * a * d[i]; m[i + 1] = tau * b * d[i]

    def f(x):
        x = np.clip(x, xs[0], xs[-1]); i = np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2)
        h = xs[i + 1] - xs[i]; t = (x - xs[i]) / h
        return (2*t**3 - 3*t**2 + 1) * ys[i] + (t**3 - 2*t**2 + t) * h * m[i] + (-2*t**3 + 3*t**2) * ys[i + 1] + (t**3 - t**2) * h * m[i + 1]
    return f


def db(x):
    return 10 ** (x / 20)


def place(bed, snd, t, gain, p=0.0):
    s = snd if snd.ndim == 2 else pan(snd, p)
    i = int(t * SR)
    if i >= len(bed) or i + len(s) < 0: return
    s = s[: len(bed) - i] * gain
    bed[i:i + len(s)] += s


def build(topic: Path):
    data = json.loads((topic / "timeline.json").read_text())
    TL, EV = data["TL"], data["EVENTS"]
    B = TL["beats"]; T = TL["T_END"]; STOP = B["stop"]
    n = int(T * SR); t = np.arange(n) / SR
    counter = monotone(TL["counter"])
    wind = np.where(t < STOP, np.maximum(0, TL["counterMax"] - counter(np.minimum(t, STOP))), 0)
    I = .06 + .94 * (wind / TL["counterMax"]) ** .6          # wind intensity 0..1
    lib = library()
    rng = np.random.default_rng(11)
    bed = np.zeros((n, 2))
    alive = (t < STOP).astype(float)
    alive = np.minimum(alive, 1)  # hard stop; a 30 ms ramp is added below
    k = int(.03 * SR); i0 = int(STOP * SR)
    alive[i0 - k:i0] = np.linspace(1, 0, k)

    # 1. city: loop of stad.wav until the wind takes over
    stad = np.tile(lib["stad"], (int(T / 30) + 2, 1))[:n]
    bed += stad * db(-14) * (1 - smooth(38, 50, t))[:, None]
    for tc in (2.5, 9.5, 21.0, 27.5, 33.0):
        place(bed, lib["auto"], tc - 2.5, db(-16) * (1 - smooth(36, 42, tc)))
    r0, r1 = B["redLight"]
    for tk in np.arange(r0, r1, 1.0):
        place(bed, lib["tik"], tk, db(-30), .35)

    # 2. wind that follows the counter: roar, mid, whistles and hiss crossfade with intensity
    def layer(make, gain, width=.7):
        return stereo(rng, make, width) * gain[:, None]
    roar = layer(lambda r: norm(bp(brown(r, n), 50, 420) * lfo(r, n, .11, .45)), I ** 1.1)
    mid = layer(lambda r: norm(bp(r.standard_normal(n), 350, 1300) * lfo(r, n, .17, .6)), I ** 1.8 * .7)
    whis = np.zeros((n, 2))
    for f0 in (650, 980, 1450, 2100):
        whis += layer(lambda r: norm(bp(r.standard_normal(n), f0 * .93, f0 * 1.07, 2) * np.clip(lfo(r, n, .23, 1.0), 0, None)),
                      smooth(.35 + f0 / 6000, .85, I) * .35)
    hiss = layer(lambda r: norm(hp(r.standard_normal(n), 2500)), I ** 2.4 * .35)
    breeze = layer(lambda r: norm(bp(brown(r, n), 120, 900) * lfo(r, n, .08, .7)), np.full(n, .12) * (1 - smooth(40, 52, t)))
    bed += (roar + mid + whis + hiss) * db(-6) * alive[:, None] + breeze * db(-14)

    # 3. rumble, rattle, drone
    rum = np.tile(lib["gerommel"], (int(T / 20) + 2, 1))[:n]
    bed += rum * (db(-34) * smooth(25, 32, t) + db(-14) * smooth(40, 66, t) + db(-6) * smooth(66, 70, t))[:, None] * alive[:, None]
    ram = np.tile(lib["rammel"], (int(T / 6) + 2, 1))[:n]
    bed += ram * (db(-22) * smooth(32, 40, t) * (1 - smooth(52, 58, t)))[:, None]
    dr = np.tile(lib["drone"], (int(T / 30) + 2, 1))[:n]
    bed += dr * (db(-34) + db(-24) * smooth(30, 70, t) * alive + db(-28) * smooth(STOP, STOP + .5, t) * (1 - smooth(B["fade"], T, t)))[:, None]

    # 4. creaks and bending metal as things start to give
    for tc in (44.5, 47.5, 50.5, 53.0, 56.0, 61.5, 64.5, 68.0, 71.0):
        place(bed, s_kraak(rng), tc, db(-12), rng.uniform(-.6, .6))
    for tc in (46.6, 49.0, 52.0, 58.0, 62.5, 66.0, 69.5, 72.2):
        place(bed, s_metaal(rng), tc, db(-15), rng.uniform(-.7, .7))
    for tc in np.arange(41, 52, 1.6):        # things falling over
        place(bed, s_klap(rng, .3), tc + rng.uniform(0, .8), db(-24), rng.uniform(-.8, .8))

    # 5. glass: one big burst on 'Windows burst', then more and more
    place(bed, s_glas(rng), B["windows"], db(-4), -.3)
    place(bed, s_glas(rng), B["windows"] + .35, db(-7), .4)
    for tc in np.sort(rng.uniform(B["windows"] + 1, STOP, 14)):
        place(bed, s_glas(rng), tc, db(-12), rng.uniform(-.8, .8))
    place(bed, s_kraak(rng), B["walls"], db(-6), 0)
    place(bed, s_puin(rng), B["walls"] + .3, db(-10), .3)

    # 6. physics events: impacts (thinned), floors tearing, towers collapsing
    last = -1
    for e in EV:
        if e["t"] >= STOP: continue
        if e["kind"] == "impact":
            if e["t"] - last < .12: continue
            last = e["t"]
            dist = np.hypot(e["x"] + 1, e["z"] - 35)
            g = db(-4) * e["e"] ** .6 / (1 + dist / 25)
            s = s_klap(rng, .6 + e["heavy"] * .3)
            if dist > 50: s = lp(s, 900)
            place(bed, s, e["t"], g, np.clip(e["x"] / 15, -.9, .9))
            if e["heavy"] >= 2: place(bed, s_puin(rng), e["t"] + .1, g * .5, np.clip(e["x"] / 15, -.9, .9))
        elif e["kind"] == "tear":
            place(bed, s_metaal(rng), e["t"] - .3, db(-14), rng.uniform(-.7, .7))
        elif e["kind"] == "collapse":
            rumble = lp(brown(rng, 6 * SR), 140) ; rumble = norm(rumble) * env_ad(6 * SR, .8, 2.5)
            place(bed, np.stack([rumble, rumble], 1), e["t"], db(-6))
            for j in range(6):
                place(bed, lp(s_klap(rng, 1.4), 1200), e["t"] + .4 + j * .45 + rng.uniform(0, .3), db(-12), rng.uniform(-.5, .5))
    # climax: debris whooshing past the camera
    for tc in np.sort(rng.uniform(B["climax"] - 1, STOP - .1, 22)):
        L = int(.9 * SR); tt = np.arange(L) / SR
        w = bp(rng.standard_normal(L), 300, 3000) * np.exp(-((tt - .45) / .15) ** 2)
        place(bed, pan(norm(w), np.linspace(-.9, .9, L) * rng.choice([-1, 1])), tc, db(-12))

    # hard stop: cut everything that was placed after STOP onwards
    bed[i0:] *= 0
    bed[i0 - k:i0] *= np.linspace(1, 0, k)[:, None]

    # 7. after the stop: distant wind, a few pieces settling, low tone
    after = np.zeros((n, 2))
    far = stereo(rng, lambda r: norm(lp(brown(r, n), 250) * lfo(r, n, .06, .5)), .8)
    after += far * (db(-32) * smooth(STOP, STOP + 1.5, t) * (1 - smooth(B["end"] + 3, B["fade"], t)))[:, None]
    for tc in (STOP + .9, STOP + 2.3, STOP + 4.1):
        place(after, lp(s_puin(rng), 1500), tc, db(-30), rng.uniform(-.6, .6))
    bed += after
    bed *= (1 - smooth(B["fade"], T - .05, t))[:, None]
    return bed


# ---------- generic engine videos (engine/ + topics/<slug>/) ----------
def s_water(rng, sec=30):
    """River/harbour water lapping against a quay wall."""
    n = int(sec * SR)
    def one(r):
        lap = bp(r.standard_normal(n), 250, 1600) * np.clip(lfo(r, n, .35, 1.0), 0, None) ** 2
        return lap * .5 + lp(brown(r, n), 300) * .3
    return norm(stereo(rng, one, .7))


def s_waves(rng, sec=30):
    """Sea waves: slow swells of surf every 6-9 s."""
    n = int(sec * SR); t = np.arange(n) / SR
    env = np.zeros(n); p = 0.0
    while p < sec:
        env += np.exp(-((t - p - 1.2) / .9) ** 2) * (1 - np.exp(-np.maximum(0, t - p) * 2)) * rng.uniform(.6, 1)
        env += np.exp(-np.maximum(0, t - p - 1.6) * .6) * (t > p + 1.6) * .35
        p += rng.uniform(6, 9)
    return norm(stereo(rng, lambda r: (bp(r.standard_normal(n), 200, 5000) * env + lp(brown(r, n), 200) * .2), .8))


def s_berg(rng, sec=30):
    """Mountain quiet: soft high wind, a far bird now and then."""
    n = int(sec * SR); t = np.arange(n) / SR
    x = norm(stereo(rng, lambda r: bp(brown(r, n), 200, 1500) * lfo(r, n, .06, .8), .8), .4)
    for _ in range(4):
        L = int(.5 * SR); tt = np.arange(L) / SR; p = int(rng.uniform(0, sec - 1) * SR)
        call = np.sin(2 * np.pi * np.cumsum(1900 * (1 - .25 * tt / tt[-1])) / SR) * np.sin(np.pi * tt / tt[-1]) * .04
        x[p:p + L] += pan(call, rng.uniform(-.7, .7))
    return x


def s_snap(rng):
    """A steel cable snapping: sharp crack and a falling twang."""
    n = int(2.2 * SR); t = np.arange(n) / SR
    crack = hp(rng.standard_normal(n), 1200) * env_ad(n, .0003, .01) * 1.4
    f = 420 * np.exp(-t * 1.4) + 60
    tw = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in (1, 2.76, 5.4)) * np.exp(-t * 2.2) * .5
    return norm(crack + tw + lp(rng.standard_normal(n), 400) * env_ad(n, .001, .15) * .4)


def s_splash(rng, size=1.0):
    """Heavy object into water: thump, splash burst, falling drops."""
    n = int(3 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-t * 4) + 30) / SR) * env_ad(n, .004, .2 * size)
    burst = bp(rng.standard_normal(n), 300, 6000) * env_ad(n, .01, .35 * size)
    drops = np.zeros(n)
    for _ in range(int(60 * size)):
        p = int((.2 + rng.uniform(0, 1.8) ** 1.3) * SR); L = int(.04 * SR)
        if p + L < n: drops[p:p + L] += bp(rng.standard_normal(L), 900, 5000) * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(.05, .3)
    return norm(thump + burst + drops)


def s_ice(rng):
    """Ice cracking: a ringing 'pew' plus crackle."""
    n = int(2 * SR); t = np.arange(n) / SR
    pew = np.sin(2 * np.pi * np.cumsum(2400 * np.exp(-t * 6) + 300) / SR) * np.exp(-t * 5) * .5
    return norm(pew + hp(rng.standard_normal(n), 2000) * env_ad(n, .0005, .02) + lp(rng.standard_normal(n), 300) * env_ad(n, .001, .1) * .5)


def s_groan(rng, sec=4.0):
    """Very low structural groan (steel and concrete under load)."""
    n = int(sec * SR); t = np.arange(n) / SR
    f0 = 38 + 10 * np.sin(2 * np.pi * .3 * t + rng.uniform(0, 6)) + rng.uniform(-5, 5)
    saw = sum(np.sin(2 * np.pi * np.cumsum(f0 * k) / SR) / k for k in range(1, 12))
    jit = np.clip(lfo(rng, n, 6, .9), 0, None)
    x = lp(saw * jit, 600) + bp(rng.standard_normal(n), 60, 250) * .25
    return norm(x * smooth(0, .8, t) * (1 - smooth(sec - 1.2, sec, t)))


AMBIENCE = {"stad": "stad", "rivier": "rivier", "zee": "zee", "berg": "berg"}


def loop(snd, n):
    return np.tile(snd, (n // len(snd) + 2, 1))[:n]


def build_engine(topic: Path):
    data = json.loads((topic / "timeline.json").read_text())
    TL, EV, AU = data["TL"], data["EVENTS"], data["AUDIO"]
    B = TL["beats"]; T = TL["T_END"]; STOP = B["stop"]
    n = int(T * SR); t = np.arange(n) / SR
    lv = np.array(AU["level"], float)
    I = np.interp(np.minimum(t, STOP), np.arange(len(lv)) / 10, lv)            # force intensity 0..1
    lib = library()
    rng = np.random.default_rng(11)
    bed = np.zeros((n, 2))
    k = int(.03 * SR); i0 = min(n, int(STOP * SR))
    alive = (t < STOP).astype(float); alive[max(0, i0 - k):i0] = np.linspace(1, 0, i0 - max(0, i0 - k))
    force, amb = AU["force"], AU.get("ambience") or "stad"

    # 1. place ambience, fading as the force takes over
    ambs = {"stad": lambda: lib["stad"], "rivier": lambda: lib["stad"] * .6 + s_water(rng) * .5,
            "zee": lambda: s_waves(rng) * .8 + lib["stad"] * .2, "berg": lambda: s_berg(rng)}
    A = loop(ambs.get(amb, ambs["stad"])(), n)
    bed += A * (db(-14) * (1 - smooth(.25, .7, I)) * alive + db(-30) * alive)[:, None]

    def layer(make, gain, width=.7):
        return stereo(rng, make, width) * gain[:, None]

    # 2. the force itself, following its intensity
    if force == "wind":
        roar = layer(lambda r: norm(bp(brown(r, n), 50, 420) * lfo(r, n, .11, .45)), I ** 1.1)
        mid = layer(lambda r: norm(bp(r.standard_normal(n), 350, 1300) * lfo(r, n, .17, .6)), I ** 1.8 * .7)
        hiss = layer(lambda r: norm(hp(r.standard_normal(n), 2500)), I ** 2.4 * .35)
        bed += (roar + mid + hiss) * db(-6) * alive[:, None]
    elif force == "gravity":
        rum = loop(lib["gerommel"], n)
        bed += rum * (db(-30) + db(-10) * smooth(.15, 1, I) ** 1.5)[:, None] * alive[:, None]
        sub = np.sin(2 * np.pi * np.cumsum(28 + 6 * I) / SR) * smooth(.05, 1, I) * .5
        bed += np.stack([sub, sub], 1) * db(-10) * alive[:, None]
        tc = 0.0
        while True:      # groans and creaks, more often as the load grows
            nxt = np.argmax((t > tc + .5) & (I > .12))
            if nxt == 0: break
            tc = t[nxt] + rng.uniform(1.0, 3.0) * (1.4 - I[nxt])
            if tc >= STOP - .5: break
            place(bed, s_groan(rng, rng.uniform(2.5, 4.5)), tc, db(-9) * (.4 + I[min(n - 1, int(tc * SR))]), rng.uniform(-.6, .6))
            if rng.random() < .5: place(bed, s_metaal(rng), tc + rng.uniform(0, 1), db(-17), rng.uniform(-.7, .7))
            if rng.random() < .4: place(bed, s_kraak(rng), tc + rng.uniform(0, 1), db(-15), rng.uniform(-.7, .7))
    elif force == "water":
        rush = layer(lambda r: norm(bp(r.standard_normal(n), 150, 2500) * lfo(r, n, .2, .4)), I ** 1.3)
        low = layer(lambda r: norm(lp(brown(r, n), 180) * lfo(r, n, .07, .5)), I)
        bed += (rush * db(-8) + low * db(-10)) * alive[:, None]
    elif force == "cold":
        thin = layer(lambda r: norm(bp(r.standard_normal(n), 1500, 4000) * np.clip(lfo(r, n, .1, 1), 0, None)), I * .5)
        bed += thin * db(-16) * alive[:, None]
        for tc in np.sort(rng.uniform(STOP * .4, STOP, 10)):
            place(bed, s_ice(rng), tc, db(-18) * I[int(tc * SR)], rng.uniform(-.8, .8))

    # 3. dark drone under everything
    dr = loop(lib["drone"], n)
    bed += dr * (db(-34) + db(-24) * smooth(.2, 1, I) * alive + db(-28) * smooth(STOP, STOP + .5, t) * (1 - smooth(B["fade"], T, t)))[:, None]

    # 4. events
    last = -1
    for e in EV:
        if e["t"] >= STOP: continue
        p = float(np.clip((e.get("x") or 0) / 60, -.8, .8))
        if e["kind"] == "impact":
            if e["t"] - last < .12: continue
            last = e["t"]
            place(bed, s_klap(rng, .6 + e.get("heavy", 1) * .3), e["t"], db(-8) * e["e"] ** .6, p)
        elif e["kind"] == "collapse":
            rumble = norm(lp(brown(rng, 7 * SR), 140)) * env_ad(7 * SR, .6, 2.8)
            place(bed, np.stack([rumble, rumble], 1), e["t"], db(-4) * min(1.2, e.get("e", 1)))
            for j in range(7):
                place(bed, lp(s_klap(rng, 1.4), 1400), e["t"] + .3 + j * .4 + rng.uniform(0, .3), db(-11), rng.uniform(-.5, .5))
            place(bed, lp(s_puin(rng), 2500), e["t"] + 1.2, db(-10), p)
        elif e["kind"] == "snap":
            place(bed, s_snap(rng), e["t"], db(-9), p)
        elif e["kind"] == "splash":
            place(bed, s_splash(rng, .6 + e["e"]), e["t"], db(-6) * e["e"] ** .5, p)
        elif e["kind"] == "glass":
            place(bed, s_glas(rng), e["t"], db(-6), p)
        elif e["kind"] in ("crack", "tear"):
            place(bed, s_kraak(rng), e["t"], db(-8), p)
            place(bed, s_metaal(rng), e["t"] + .2, db(-14), -p)

    # 5. hard stop, then a quiet aftermath
    bed[i0:] *= 0
    bed[max(0, i0 - k):i0] *= np.linspace(1, 0, i0 - max(0, i0 - k))[:, None]
    after = stereo(rng, lambda r: norm(lp(brown(r, n), 250) * lfo(r, n, .06, .5)), .8)
    bed += after * (db(-32) * smooth(STOP, STOP + 1.5, t) * (1 - smooth(B["end"] + 3, B["fade"], t)))[:, None]
    for tc in (STOP + 1.1, STOP + 2.6):
        place(bed, lp(s_puin(rng), 1500), tc, db(-32), rng.uniform(-.6, .6))
    bed *= (1 - smooth(B["fade"], T - .05, t))[:, None]
    return bed


def read_audio(path: Path, T: float) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, "<f4").reshape(-1, 2).astype(np.float64)
    out = np.zeros((int(T * SR), 2)); m = min(len(x), len(out)); out[:m] = x[:m]
    return out


def mix_engine(topic: Path):
    """Voice first: the bed ducks 8 dB under the voice, then -14 LUFS and peaks at -1 dBTP."""
    data = json.loads((topic / "timeline.json").read_text())
    T, off = data["TL"]["T_END"], data["TL"]["VO_OFFSET"]
    bed = build_engine(topic)
    bed = bed / (np.max(np.abs(bed)) or 1) * .5
    voice = read_audio(topic / "voice.mp3", T)
    k = int(off * SR); voice = np.concatenate([np.zeros((k, 2)), voice])[:len(bed)]
    # envelope follower (40 ms attack, 450 ms release) on the voice -> gain on the bed
    lvl = np.abs(voice).max(1); hop = 441
    blk = lvl[: len(lvl) // hop * hop].reshape(-1, hop).max(1)
    on = (blk > .02).astype(float); env = np.zeros_like(on); a, r = 1 - np.exp(-1 / 4), 1 - np.exp(-1 / 45)
    for i in range(1, len(on)): env[i] = env[i - 1] + (on[i] - env[i - 1]) * (a if on[i] > env[i - 1] else r)
    g = np.repeat(1 - (1 - db(-8)) * env, hop); g = np.concatenate([g, np.full(len(bed) - len(g), g[-1] if len(g) else 1)])
    mix = voice * db(-1) + bed * g[:, None]
    write(topic / "sfx-bed.wav", bed)
    write(topic / "premix.wav", mix / (np.max(np.abs(mix)) or 1) * .9)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(topic / "premix.wav"),
                    "-af", "loudnorm=I=-14:TP=-1:LRA=11:linear=true,alimiter=limit=0.89:level=false,aresample=44100",
                    "-t", str(T), str(topic / "mix.wav")], check=True)
    (topic / "premix.wav").unlink()
    print("ok:", topic / "mix.wav")


def main():
    topic = Path(sys.argv[1]).resolve()
    if "AUDIO" in json.loads((topic / "timeline.json").read_text()):
        return mix_engine(topic)
    bed = build(topic)
    bed = bed / (np.max(np.abs(bed)) or 1) * .7
    write(topic / "sfx-bed.wav", bed)
    data = json.loads((topic / "timeline.json").read_text())
    off = int(data["TL"]["VO_OFFSET"] * 1000); T = data["TL"]["T_END"]
    # voice first: duck the bed ~8 dB while the voice speaks, then loudness -14 LUFS, peak -1 dB
    fc = (f"[1:a]adelay={off}|{off},apad,atrim=0:{T},aformat=channel_layouts=stereo,asplit=2[v][sc];"
          f"[0:a][sc]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=450:makeup=1[d];"
          f"[d][v]amix=inputs=2:weights='1.9 1.6':normalize=0,"
          f"loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.8:level=false,aresample=44100[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(topic / "sfx-bed.wav"), "-i", str(topic / "voice.mp3"),
                    "-filter_complex", fc, "-map", "[out]", "-t", str(T), str(topic / "mix.wav")], check=True)
    print("ok:", topic / "mix.wav")


if __name__ == "__main__":
    main()
