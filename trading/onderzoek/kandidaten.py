"""Strategieën van TradingView Editors' Picks, nagebouwd in Python (alleen long, spot).
Elke functie geeft trades: dicts met i_in, p_in, maker_in, i_out, p_out, maker_out."""
import math

def ema(x, n):
    k = 2 / (n + 1); out = []; e = None
    for v in x:
        e = v if e is None else v * k + e * (1 - k); out.append(e)
    return out

def rma(x, n):
    out = []; r = None
    for i, v in enumerate(x):
        if i < n - 1: out.append(None); continue
        if r is None: r = sum(x[:n]) / n
        else: r = (r * (n - 1) + v) / n
        out.append(r)
    return out

def tr(k):
    return [k[0]["h"] - k[0]["l"]] + [max(c["h"] - c["l"], abs(c["h"] - p["c"]), abs(c["l"] - p["c"])) for p, c in zip(k, k[1:])]

def atr(k, n): return rma(tr(k), n)

def _posities(k, koop, verkoop):
    """Signaal op slot candle i -> uitvoering op open van i+1 (geen vooruitkijken)."""
    t, inn = [], None
    for i in range(len(k) - 1):
        if inn is None and koop[i]:
            inn = i + 1
        elif inn is not None and verkoop[i] and i + 1 > inn:
            t.append(dict(i_in=inn, p_in=k[inn]["o"], maker_in=False, i_out=i + 1, p_out=k[i + 1]["o"], maker_out=False)); inn = None
    if inn is not None:
        t.append(dict(i_in=inn, p_in=k[inn]["o"], maker_in=False, i_out=len(k) - 1, p_out=k[-1]["c"], maker_out=False, open=True))
    return t

# 1. PMax (KivancOzbilgic): EMA(hl2,10), ATR 10, mult 3
def pmax(k, atr_n=10, mult=3.0, ma_n=10):
    src = [(c["h"] + c["l"]) / 2 for c in k]; ma = ema(src, ma_n); a = atr(k, atr_n)
    ls_prev = ss_prev = None; d = 1; pm = []
    for i in range(len(k)):
        if a[i] is None: pm.append(None); continue
        ls = ma[i] - mult * a[i]; ss = ma[i] + mult * a[i]
        lsp = ls if ls_prev is None else ls_prev; ssp = ss if ss_prev is None else ss_prev
        ls = max(ls, lsp) if ma[i] > lsp else ls
        ss = min(ss, ssp) if ma[i] < ssp else ss
        d = 1 if (d == -1 and ma[i] > ssp) else (-1 if (d == 1 and ma[i] < lsp) else d)
        pm.append(ls if d == 1 else ss); ls_prev, ss_prev = ls, ss
    koop = [i > 0 and pm[i] is not None and pm[i-1] is not None and ma[i] > pm[i] and ma[i-1] <= pm[i-1] for i in range(len(k))]
    verk = [i > 0 and pm[i] is not None and pm[i-1] is not None and ma[i] < pm[i] and ma[i-1] >= pm[i-1] for i in range(len(k))]
    return _posities(k, koop, verk)

# 2. SuperTrend (ATR 10, mult 3, hl2)
def supertrend(k, atr_n=10, mult=3.0):
    a = atr(k, atr_n); up_p = dn_p = None; d = 1; dirs = []
    for i, c in enumerate(k):
        if a[i] is None: dirs.append(None); continue
        hl2 = (c["h"] + c["l"]) / 2; up = hl2 - mult * a[i]; dn = hl2 + mult * a[i]
        if up_p is not None and k[i-1]["c"] > up_p: up = max(up, up_p)
        if dn_p is not None and k[i-1]["c"] < dn_p: dn = min(dn, dn_p)
        if up_p is not None:
            d = 1 if (d == -1 and c["c"] > dn_p) else (-1 if (d == 1 and c["c"] < up_p) else d)
        up_p, dn_p = up, dn; dirs.append(d)
    koop = [i > 0 and dirs[i] == 1 and dirs[i-1] == -1 for i in range(len(k))]
    verk = [i > 0 and dirs[i] == -1 and dirs[i-1] == 1 for i in range(len(k))]
    return _posities(k, koop, verk)

# 3. Grover Llorens Activator (alexgrover), strategie: slot kruist boven = long, onder = uit
def gla(k, length=480, mult=14):
    a = atr(k, length); ts = None; val = 0.0; bars = 0; out = []
    for i, c in enumerate(k):
        src = c["c"]
        prev = src if ts is None else ts
        diff = src - prev
        prevdiff = out[-1][1] if out else 0.0
        up = diff > 0 and prevdiff <= 0; dn = diff < 0 and prevdiff >= 0
        if a[i] is None: ts = src; out.append((ts, 0.0)); continue
        if up or dn: val = a[i] / length; bars = 0
        else: bars += 1
        ts = prev - a[i] * mult if up else (prev + a[i] * mult if dn else prev + math.copysign(1, diff) * val * bars if diff else prev)
        out.append((ts, diff))
    lijn = [o[0] for o in out]
    koop = [i > 0 and k[i]["c"] > lijn[i] and k[i-1]["c"] <= lijn[i-1] for i in range(len(k))]
    verk = [i > 0 and k[i]["c"] < lijn[i] and k[i-1]["c"] >= lijn[i-1] for i in range(len(k))]
    return _posities(k, koop, verk)

# 4. Keltner Channel (TradingView standaard: EMA 20, ema(TR) x 2; stop-order boven high bij uitbraak)
def keltner(k, n=20, mult=2.0):
    ma = ema([c["c"] for c in k], n); rng = ema(tr(k), n)
    t, inn, i = [], None, n
    while i < len(k) - 1:
        bov, ond = ma[i] + mult * rng[i], ma[i] - mult * rng[i]
        bov_p, ond_p = ma[i-1] + mult * rng[i-1], ma[i-1] - mult * rng[i-1]
        if inn is None and k[i]["c"] > bov and k[i-1]["c"] <= bov_p:
            stop = k[i]["h"]
            if k[i+1]["h"] > stop:
                inn = (i + 1, max(k[i+1]["o"], stop))
        elif inn is not None and k[i]["c"] < ond and k[i-1]["c"] >= ond_p:
            stop = k[i]["l"]
            if k[i+1]["l"] < stop:
                t.append(dict(i_in=inn[0], p_in=inn[1], maker_in=False, i_out=i + 1, p_out=min(k[i+1]["o"], stop), maker_out=False)); inn = None
        i += 1
    if inn: t.append(dict(i_in=inn[0], p_in=inn[1], maker_in=False, i_out=len(k)-1, p_out=k[-1]["c"], maker_out=False, open=True))
    return t

# 5. Bjorgum Double Tap (dubbele bodem): zigzag, W-vorm, instap bij slot boven de hals,
#    stop onder de patroonbodem, doel = hals + patroonhoogte
def double_tap(k, zz=10, tol=0.25):
    a = atr(k, 14); piv = []          # (type, prijs, index) afwisselend
    t, i = [], 2 * zz
    pos = None
    while i < len(k):
        j = i - zz                    # pivot bevestigd met zz candles rechts
        venster = k[j - zz:i + 1]
        if k[j]["l"] == min(c["l"] for c in venster):
            if piv and piv[-1][0] == "L":
                if k[j]["l"] < piv[-1][1]: piv[-1] = ("L", k[j]["l"], j)
            else: piv.append(("L", k[j]["l"], j))
        if k[j]["h"] == max(c["h"] for c in venster):
            if piv and piv[-1][0] == "H":
                if k[j]["h"] > piv[-1][1]: piv[-1] = ("H", k[j]["h"], j)
            else: piv.append(("H", k[j]["h"], j))
        c = k[i]
        if pos:
            if c["l"] <= pos["stop"]:
                t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=i, p_out=min(c["o"], pos["stop"]), maker_out=False)); pos = None
            elif c["h"] >= pos["doel"]:
                t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=i, p_out=max(c["o"], pos["doel"]), maker_out=True)); pos = None
        elif len(piv) >= 3 and piv[-1][0] == "L" and piv[-2][0] == "H" and piv[-3][0] == "L" and a[i]:
            l1, hals, l2 = piv[-3][1], piv[-2][1], piv[-1][1]
            if abs(l2 - l1) <= tol * (hals - min(l1, l2)) and l2 >= l1 - 0.1 * a[i] and c["c"] > hals and k[i-1]["c"] <= hals and i > piv[-1][2]:
                bodem = min(l1, l2); hoogte = hals - bodem
                if i + 1 < len(k):
                    pos = {"i": i + 1, "p": k[i+1]["o"], "stop": bodem, "doel": hals + hoogte}
        i += 1
    if pos: t.append(dict(i_in=pos["i"], p_in=pos["p"], maker_in=False, i_out=len(k)-1, p_out=k[-1]["c"], maker_out=False, open=True))
    return t

# 6. TASC One Percent A Week (op uur-candles, week = maandag 00:00 UTC)
#    limiet -1% onder maandagopen; vanaf de dag na de instap doel +1%; na 0,5% daling een
#    break-even-limiet op de instap; vrijdag 23:00 UTC (slot) eruit. Eén trade per week.
def one_percent(k):
    import datetime as dt
    t, status = [], None
    for i, c in enumerate(k):
        d = dt.datetime.fromtimestamp(c["tijd"] / 1000, dt.timezone.utc)
        if d.weekday() == 0 and d.hour == 0:
            limiet, status = c["o"] * 0.99, "wacht"
        if status == "wacht":
            if d.weekday() <= 4 and c["l"] <= limiet:
                inn_i, inn_p, dag_in, tp, status = i, min(c["o"], limiet), d.date(), None, "in"
                daling = c["l"] <= inn_p * 0.995           # telt pas vanaf de volgende candle
            elif d.weekday() == 4 and d.hour == 23:
                status = None
            continue
        if status == "in":
            if tp is None and d.date() > dag_in:
                tp = inn_p * 1.01
            uit = None
            if daling and c["h"] >= inn_p:
                uit = (max(c["o"], inn_p), True)          # break-even-limiet
            elif tp and c["h"] >= tp:
                uit = (max(c["o"], tp), True)             # doel-limiet
            elif d.weekday() == 4 and d.hour == 23:
                uit = (c["c"], False)                     # vrijdag slot, marktorder
            if uit:
                t.append(dict(i_in=inn_i, p_in=inn_p, maker_in=True, i_out=i, p_out=uit[0], maker_out=uit[1]))
                status = None
            elif c["l"] <= inn_p * 0.995:
                daling = True
    return t


STRATEGIEEN = {"PMax": pmax, "SuperTrend": supertrend, "Grover Llorens": gla, "Keltner": keltner,
               "Double Tap": double_tap, "One Percent A Week": one_percent}
