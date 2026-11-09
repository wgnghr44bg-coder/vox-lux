"""Tweede ronde: Editors' Picks-indicatoren als long-only regels."""
import math
from kandidaten import ema, atr, _posities

def supersmoother_var(src, perioden):
    f = []
    for i, x in enumerate(src):
        p = perioden[i] if isinstance(perioden, list) else perioden
        a1 = math.exp(-1.414 * math.pi / p); c2 = 2 * a1 * math.cos(1.414 * math.pi / p); c3 = -a1 * a1; c1 = 1 - c2 - c3
        if i < 2: f.append(x); continue
        f.append(c1 * (x + src[i-1]) / 2 + c2 * f[i-1] + c3 * f[i-2])
    return f

# A. Adaptive SuperSmoother (Ehlers): long als ASS > SS
def adaptive_ss(k, basis=20, rms_n=81):
    c = [x["c"] for x in k]
    ss = supersmoother_var(c, basis)
    roc = [0.0] + [ss[i] - ss[i-1] for i in range(1, len(ss))]
    per = []
    for i in range(len(c)):
        w = roc[max(0, i - rms_n + 1):i + 1]
        rms = math.sqrt(sum(r * r for r in w) / len(w)) if w else 0
        sc = min(abs(roc[i]) / rms, 2) if rms else 0
        per.append(max(basis * (1 - sc / 2) ** 2, 2))
    ass = supersmoother_var(c, per)
    boven = [i > rms_n and ass[i] > ss[i] for i in range(len(c))]
    koop = [i > 0 and boven[i] and not boven[i-1] for i in range(len(c))]
    verk = [i > 0 and not boven[i] and boven[i-1] for i in range(len(c))]
    return _posities(k, koop, verk)

# B1. Chandelier (22, 3x ATR)
def chandelier(k, n=22, mult=3.0):
    a = atr(k, n); d = 1; ls_p = ss_p = None; dirs = []
    for i in range(len(k)):
        if a[i] is None or i < n: dirs.append(None); continue
        hh = max(x["h"] for x in k[i-n+1:i+1]); ll = min(x["l"] for x in k[i-n+1:i+1])
        ls = hh - mult * a[i]; ss = ll + mult * a[i]
        if ls_p is not None and k[i-1]["c"] > ls_p: ls = max(ls, ls_p)
        if ss_p is not None and k[i-1]["c"] < ss_p: ss = min(ss, ss_p)
        if ls_p is not None:
            d = 1 if k[i]["c"] > ss_p else (-1 if k[i]["c"] < ls_p else d)
        ls_p, ss_p = ls, ss; dirs.append(d)
    koop = [i > 0 and dirs[i] == 1 and dirs[i-1] == -1 for i in range(len(k))]
    verk = [i > 0 and dirs[i] == -1 and dirs[i-1] == 1 for i in range(len(k))]
    return _posities(k, koop, verk)

# B2. Donchian (20): slot boven hoogste top van vorige 20 = kopen, slot onder laagste bodem = verkopen
def donchian(k, n=20):
    koop = [i > n and k[i]["c"] > max(x["h"] for x in k[i-n:i]) for i in range(len(k))]
    verk = [i > n and k[i]["c"] < min(x["l"] for x in k[i-n:i]) for i in range(len(k))]
    return _posities(k, koop, verk)

# C. Dual-Phase Reversal: 9 x slot < slot 4 candles eerder (na een 'momentum shift');
#    instap volgende open, stop = laagste bodem van de fase, doel = hoogste top van de fase
def dpr9(k):
    t, tel, pos = [], 0, None
    for i in range(5, len(k)):
        c = k[i]
        if pos:
            if c["l"] <= pos["stop"]:
                t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=i, p_out=min(c["o"], pos["stop"]), maker_out=False)); pos = None
            elif c["h"] >= pos["doel"]:
                t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=i, p_out=max(c["o"], pos["doel"]), maker_out=True)); pos = None
            continue
        if c["c"] < k[i-4]["c"]:
            tel = tel + 1 if (tel > 0 or k[i-1]["c"] >= k[i-5]["c"]) else 0
        else:
            tel = 0
        if tel == 9 and i + 1 < len(k):
            fase = k[i-8:i+1]; stop = min(x["l"] for x in fase); doel = max(x["h"] for x in fase)
            p = k[i+1]["o"]
            if stop < p < doel:
                pos = {"i": i + 1, "p": p, "stop": stop, "doel": doel}
            tel = 0
    if pos: t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=len(k)-1, p_out=k[-1]["c"], maker_out=False, open=True))
    return t

# D. Katsanos RSMK (dagcandles), munt t.o.v. benchmark BTC
def rsi(c, n):
    out = [None] * len(c); ag = al = None
    for i in range(1, len(c)):
        ch = c[i] - c[i-1]; g, l = max(ch, 0), max(-ch, 0)
        if i < n: ag = (ag or 0) + g / n; al = (al or 0) + l / n; continue
        if i == n: ag += g / n; al += l / n
        else: ag = (ag * (n - 1) + g) / n; al = (al * (n - 1) + l) / n
        out[i] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return out

def corr(a, b):
    n = len(a); ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a)); sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else 0

def rsmk(k, bench, n=35, rsi_n=10, ma_n=50, min_corr=0.5, corr_n=20):
    bt = {x["tijd"]: x["c"] for x in bench}
    k = [x for x in k if x["tijd"] in bt]; b = [bt[x["tijd"]] for x in k]; c = [x["c"] for x in k]
    lr = [math.log(c[i] / b[i]) for i in range(len(c))]
    rs1 = [lr[i] - lr[i-n] if i >= n else 0.0 for i in range(len(c))]
    rm = [v * 100 for v in ema(rs1, 4)]
    r = rsi(c, rsi_n); e5 = ema(c, 5)
    ret = [0] + [c[i] / c[i-1] - 1 for i in range(1, len(c))]; bret = [0] + [b[i] / b[i-1] - 1 for i in range(1, len(b))]
    t, pos = [], None
    for i in range(max(n + ma_n, 30), len(k) - 1):
        if pos:
            cr = corr(ret[i-corr_n+1:i+1], bret[i-corr_n+1:i+1])
            if (cr > min_corr and rm[i] < -3) or i - pos["i"] >= 30 or c[i] >= pos["p"] * 1.25:
                t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=i + 1, p_out=k[i+1]["o"], maker_out=False)); pos = None
            continue
        sma_rm = sum(rm[i-ma_n+1:i+1]) / ma_n
        sma15_5 = sum(c[i-5-14:i-5+1]) / 15
        cr = corr(ret[i-corr_n+1:i+1], bret[i-corr_n+1:i+1])
        roc6 = b[i] / b[i-6] - 1
        markt = (roc6 > -0.06 and cr > min_corr) or (roc6 < -0.06 and cr < -min_corr)
        if (rm[i] > sma_rm and rm[i] > 3 and rm[i] >= max(rm[i-3:i+1]) and
                any(x is not None and x < 35 for x in r[i-19:i+1]) and r[i] > r[i-1] > r[i-2] > r[i-3] and
                rm[i] < 25 and e5[i] > sma15_5 and markt):
            pos = {"i": i + 1, "p": k[i+1]["o"]}
    if pos: t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=len(k)-1, p_out=k[-1]["c"], maker_out=False, open=True))
    return t, k

STRATEGIEEN = {"Adaptive SuperSmoother": adaptive_ss, "Chandelier": chandelier, "Donchian": donchian, "Dual-Phase 9": dpr9}
