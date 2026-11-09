"""Strategie 'sweep': HTF Sweep CISD.

Eigen Python-versie van het open-source TradingView-script "HTF Sweep CISD Setups" van WillyAlgoTrader
(v1.7.1), met de standaardinstellingen van dat script. Alleen kopen (long), want Bitvavo is spot.

Werking (standaard):
1. Grote tijdschaal (HTF) automatisch: 15m -> 4h, 1h -> 1 dag, 4h -> 1 week.
2. Trigger: de koers zakt onder de bodem van de vorige HTF-candle, of onder een nog niet geraakte
   HTF-bodem van de laatste 10 HTF-candles (liquiditeit "weggeveegd" = sweep).
3. Na de sweep volgt de bot het laagste punt. Daarna moet een sterke groene candle (lijf >= 0,5 x ATR)
   sluiten boven de laatste swing-top (pivot, 3 candles links/rechts) van vóór dat laagste punt: de breaker.
4. Instap: limietorder op het slot van die breaker-candle (staat de koers er al onder: direct kopen).
   Stop-loss: het laagste punt van de sweep. Risico moet tussen 0,25 en 3 x ATR liggen.
5. Doelen: TP1 = 1R, TP2 = 2R, TP3 = 3R. Na TP1 gaat de stop naar de instap (break-even).
   De positie sluit bij TP3 of bij de stop. Limiet vervalt na 60 candles of als TP1 eerst geraakt wordt.
6. Na een setup wacht de bot tot er een nieuwe sweep komt; na 36 candles zonder setup vervalt de sweep.

Extra voor Bitvavo: `min_risico_pct` (standaard 1%). Een kleinere stop-afstand wordt overgeslagen,
omdat de kosten (2 x 0,25%) dan te veel van de winst afhalen.
Niet overgenomen: de andere instapmodellen (OB, FVG, IFVG, Unicorn), tijdfilters, SMT en short.
"""

STANDAARD = {
    "htf": "auto", "pivot": 3, "max_wacht": 36, "voor_trigger": 30, "max_leeftijd": 120,
    "sweep_vorige": True, "sweep_alle": True, "liq_terug": 10, "atr": 14,
    "min_risico_atr": 0.25, "max_risico_atr": 3.0, "displacement_atr": 0.5, "stop_buffer_atr": 0.0,
    "tp1": 1.0, "tp2": 2.0, "tp3": 3.0, "break_even": True, "limiet_verloop": 60,
    "oude_instap_overslaan": True, "min_risico_pct": 1.0, "venster": 1000, "conservatief": True,
}

MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000,
      "4h": 14_400_000, "1d": 86_400_000, "1w": 604_800_000}
HTF_AUTO = {"1m": "15m", "5m": "1h", "15m": "4h", "30m": "1d", "1h": "1d", "2h": "1w", "4h": "1w"}
MAAN_EPOCH = 4 * 86_400_000            # 1 jan 1970 was een donderdag; weken beginnen op maandag


def periode_sleutel(tijd_ms, htf):
    if htf == "1w":
        return (int(tijd_ms) - MAAN_EPOCH) // MS["1w"]
    return int(tijd_ms) // MS[htf]


class _Ctx:
    """De 'long'-context na een sweep (zoals Ctx in het script, alleen het breaker-deel)."""

    def __init__(self):
        self.active = False
        self.pivots = []                # (prijs, index, low, close) van swing-toppen

    def begin(self, niveau, niveau_index, anker, i):
        self.active = True
        self.trig_bar = i
        self.created = i
        self.level = niveau
        self.level_bar = niveau_index
        self.anchor = anker
        self.ext = None
        self.ext_bar = None
        self.brk = False
        self.br_bot = self.br_c = self.br_top = self.br_x_bar = None

    def advance(self, bi, c, cnt, a, p):
        disp = c["c"] - c["o"] >= p["displacement_atr"] * (a or 0.0)
        if cnt and (self.ext is None or c["l"] < self.ext):
            self.ext, self.ext_bar = c["l"], bi
            self.brk = False                         # nieuw laagste punt: opnieuw zoeken
        if cnt and self.ext_bar is not None and bi >= self.ext_bar:
            if self.brk and self.br_bot is not None and c["c"] < self.br_bot:
                self.brk = False                     # breaker mislukt
            if not self.brk:
                lv = None
                for pp, pb, pl, pc in reversed(self.pivots):
                    if pb < self.ext_bar and pb + p["pivot"] <= bi:
                        lv, zb, zc = pp, pl, pc
                        break
                if lv is not None and c["c"] > lv and disp:
                    self.brk, self.br_x_bar = True, bi
                    self.br_top, self.br_bot, self.br_c = lv, zb, zc


class Motor:
    """Loopt candle voor candle (alleen afgesloten candles) en geeft setups (plannen)."""

    def __init__(self, candles, inst=None, interval="1h"):
        self.p = p = {**STANDAARD, **(inst or {})}
        self.k = candles
        self.htf = HTF_AUTO.get(interval, "1d") if p["htf"] == "auto" else p["htf"]
        if MS[self.htf] <= MS.get(interval, 0):
            raise ValueError("De grote tijdschaal (htf) moet groter zijn dan het candle-interval")
        self.atr = []
        self._tr_som = 0.0
        self.cur = None
        self.htfs = []
        self.liq = []                    # nog niet geraakte HTF-bodems: [prijs, index, htf_nr]
        self.htf_nr = 0
        self.eerste_klaar = False
        self.prev_gedaan = False
        self.ctx = _Ctx()

    def _atr(self, i):
        c, n = self.k[i], self.p["atr"]
        tr = c["h"] - c["l"] if i == 0 else max(c["h"] - c["l"], abs(c["h"] - self.k[i - 1]["c"]),
                                                  abs(c["l"] - self.k[i - 1]["c"]))
        if i < n - 1:
            self._tr_som += tr
            self.atr.append(None)
        elif i == n - 1:
            self._tr_som += tr
            self.atr.append(self._tr_som / n)
        else:
            self.atr.append((self.atr[-1] * (n - 1) + tr) / n)

    def stap(self, i):
        k, p, ctx = self.k, self.p, self.ctx
        c = k[i]
        self._atr(i)
        # swing-top (pivot) bevestigd op i - L
        L = p["pivot"]
        j = i - L
        if j >= L:
            links = max(x["h"] for x in k[j - L:j])
            rechts = max(x["h"] for x in k[j + 1:i + 1])
            if k[j]["h"] > links and k[j]["h"] >= rechts:
                ctx.pivots.append((k[j]["h"], j, k[j]["l"], k[j]["c"]))
                del ctx.pivots[:-40]
        # grote tijdschaal opbouwen
        sl = periode_sleutel(c["tijd"], self.htf)
        if self.cur is None or sl != self.cur["sleutel"]:
            if self.cur is not None and self.eerste_klaar:
                self.htfs.append(self.cur)
                del self.htfs[:-300]
                self.htf_nr += 1
                self.liq.append([self.cur["l"], self.cur["lb"], self.htf_nr])
            if self.cur is not None:
                self.eerste_klaar = True   # de eerste (halve) HTF-candle telt niet mee
            self.cur = {"sleutel": sl, "o": c["o"], "h": c["h"], "l": c["l"], "c": c["c"], "lb": i}
            self.prev_gedaan = False
        else:
            if c["l"] < self.cur["l"]:
                self.cur["l"], self.cur["lb"] = c["l"], i
            self.cur["h"] = max(self.cur["h"], c["h"])
            self.cur["c"] = c["c"]
        # triggers (sweeps)
        trig = None

        def zet(niveau, nb, anker):
            nonlocal trig
            if trig is None:
                trig = [niveau, nb, anker]
            else:
                if niveau < trig[0]:
                    trig[0], trig[1] = niveau, nb
                trig[2] = min(trig[2], anker)

        if self.htfs and p["sweep_vorige"] and not self.prev_gedaan and c["l"] < self.htfs[-1]["l"]:
            zet(self.htfs[-1]["l"], self.htfs[-1]["lb"], i)
            self.prev_gedaan = True
        sw = swb = None
        for q in list(reversed(self.liq)):
            if self.htf_nr - q[2] >= p["liq_terug"]:
                self.liq.remove(q)
            elif c["l"] < q[0]:
                if sw is None or q[0] < sw:
                    sw, swb = q[0], q[1]
                self.liq.remove(q)
        if sw is not None and p["sweep_alle"]:
            zet(sw, swb, i)
        gestart = False
        if trig:
            if not ctx.active:
                ctx.begin(trig[0], trig[1], trig[2], i)
                gestart = True
            else:
                ctx.trig_bar = i
                if trig[0] < ctx.level:
                    ctx.level, ctx.level_bar = trig[0], trig[1]
        # context bijwerken (bij een nieuwe sweep: candles vanaf het anker opnieuw doorlopen)
        if ctx.active:
            n = min(max(i - ctx.anchor, 0) + p["voor_trigger"], 450, i - 2) if gestart else 0
            for t in range(max(n, 0), -1, -1):
                bi = i - t
                ctx.advance(bi, k[bi], bi >= ctx.anchor, self.atr[bi], p)
        if ctx.active and (i - ctx.trig_bar > p["max_wacht"] or i - ctx.created > p["max_leeftijd"]):
            ctx.active = False
        return self._setup(i)

    def _setup(self, i):
        k, p, ctx = self.k, self.p, self.ctx
        if not ctx.active or i < max(p["atr"], 50) or ctx.ext_bar is None or not ctx.brk:
            return None
        a = self.atr[i] or 0.0
        e = ctx.br_c
        s = ctx.ext - p["stop_buffer_atr"] * a
        sluit = k[i]["c"]
        if p["oude_instap_overslaan"]:
            terug = min(i - ctx.br_x_bar - 1, 400)
            if any(k[i - t]["l"] <= e for t in range(1, terug + 1)):
                return None                  # instapprijs was al geraakt: setup is oud
        if not (e > s and sluit > s):
            return None
        markt = sluit <= e
        instap = sluit if markt else e
        risico = instap - s
        if risico <= 0 or a <= 0:
            return None
        if p["min_risico_atr"] and risico / a < p["min_risico_atr"]:
            return None
        if p["max_risico_atr"] and risico / a > p["max_risico_atr"]:
            return None
        if risico / instap * 100 < p["min_risico_pct"]:
            return None
        ctx.active = False
        return {"index": i, "markt": markt, "instap": instap, "stop": s,
                "tp1": instap + risico * p["tp1"], "tp2": instap + risico * p["tp2"],
                "tp3": instap + risico * p["tp3"], "sweep": ctx.level, "atr": a}

    def alles(self):
        return [pl for i in range(len(self.k)) if (pl := self.stap(i))]


def interval_van(candles):
    if len(candles) > 1:
        d = int(candles[-1]["tijd"]) - int(candles[-2]["tijd"])
        for naam, ms in MS.items():
            if ms == d:
                return naam
    return "1h"


def signaal(candles, inst=None):
    """Setup op de laatste afgesloten candle, of None."""
    p = {**STANDAARD, **(inst or {})}
    venster = candles[-p["venster"]:]
    if len(venster) < 60:
        return None
    m = Motor(venster, p, inst.get("interval") if inst and inst.get("interval") else interval_van(venster))
    laatste = None
    for i in range(len(venster)):
        pl = m.stap(i)
        if pl and i == len(venster) - 1:
            laatste = pl
    if not laatste:
        return None
    return {"richting": "koop", "instap": laatste["instap"], "stop": laatste["stop"], "doel": laatste["tp3"],
            "tp1": laatste["tp1"], "limiet": not laatste["markt"], "verloop_candles": p["limiet_verloop"],
            "atr": laatste["atr"], "vast": True}


def backtest(candles, inst=None, kosten_pct=0.25, interval=None):
    """Zoals de trade-motor van het script: limiet, break-even na TP1, sluiten op TP3 of stop.

    Uitkomst per trade in R (1R = afstand instap-stop), na kosten (kosten_pct per order, 2 orders).
    conservatief=True: raakt één candle zowel stop als doel, dan telt de stop eerst.
    """
    p = {**STANDAARD, **(inst or {})}
    m = Motor(candles, p, interval or interval_van(candles))
    cons = p["conservatief"]
    tr = pend = None
    trades = []

    def kosten_r(t):
        return t["instap"] * kosten_pct / 100 * 2 / t["risico"]

    def sluit(t, prijs, i, reden):
        r = (prijs - t["instap"]) / t["risico"] - kosten_r(t)
        trades.append({"tijd": candles[i]["tijd"], "richting": "koop", "R": round(r, 3),
                       "gewonnen": t["hit1"], "reden": reden})

    for i, c in enumerate(candles):
        # 1. open trade beheren
        if tr and i > tr["bar"]:
            sl = tr["stop"]
            sl_hit = c["l"] <= sl
            tp1_hit, tp3_hit = c["h"] >= tr["tp1"], c["h"] >= tr["tp3"]
            gap_sl, gap_tp = c["o"] <= sl, c["o"] >= tr["tp1"]
            sl_eerst = sl_hit and (gap_sl or (cons and not gap_tp))
            tp1_nu = tp1_hit and not tr["hit1"] and not sl_eerst
            if tp1_nu:
                tr["hit1"] = True
                if p["break_even"]:
                    tr["stop"] = tr["instap"]
            tp3_sluit = tp3_hit and not sl_eerst
            stop_sluit = sl_hit and not tp3_sluit and (sl_eerst or not tp1_nu or c["c"] <= sl)
            if tp3_sluit:
                sluit(tr, max(c["o"], tr["tp3"]), i, "TP3")
                tr = None
            elif stop_sluit:
                sluit(tr, min(c["o"], sl), i, "BE" if tr["hit1"] and sl >= tr["instap"] else "SL")
                tr = None
        # 2. wachtende limiet
        if pend and tr is None and i > pend["bar"]:
            if i - pend["bar"] > p["limiet_verloop"]:
                pend = None
            elif c["l"] <= pend["instap"]:
                vul = min(c["o"], pend["instap"])
                gap = vul <= pend["stop"]               # geopend onder de stop
                tr = {**pend, "instap": vul, "risico": pend["risico"] if gap else vul - pend["stop"],
                      "bar": i, "hit1": False}
                pend = None
                if gap or (c["l"] <= tr["stop"] if cons else c["c"] <= tr["stop"]):
                    # stop op de vulcandle (zoals het script: gap = 0R, anders -1R)
                    trades.append({"tijd": c["tijd"], "richting": "koop", "gewonnen": False, "reden": "SL",
                                   "R": round((0.0 if gap else -1.0) - kosten_r(tr), 3)})
                    tr = None
            elif c["h"] >= pend["tp1"]:
                pend = None
        # 3. nieuwe setup
        pl = m.stap(i)
        if pl and tr is None and pend is None:
            t = {"instap": pl["instap"], "stop": pl["stop"], "tp1": pl["tp1"], "tp3": pl["tp3"],
                 "risico": pl["instap"] - pl["stop"], "bar": i, "hit1": False}
            if pl["markt"]:
                tr = t
            else:
                pend = t
    return trades
