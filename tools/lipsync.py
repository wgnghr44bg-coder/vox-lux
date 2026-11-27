"""Lip sync voor de poppetjes (eigenaar 27 nov 2026, na een TikTok over een "3D Animator skill": "kun je lip sync eens laten zien").
Van de woordtijden (Whisper, woorden.json) naar een mondvorm per klank: A (wijd open), E (breed), O (rond), U (klein rond),
M (lippen dicht: m/b/p), F (tanden op de lip: f/v), L (half open met tong: l/t/d/n/th), en rust tussen woorden.
Simpel op de letters (geen woordenboek nodig), klinkers duren langer dan medeklinkers.
    from lipsync import Lipsync
    LS = Lipsync(woorden)            # [[zin, woord, t0, t1], ...]
    v = LS.viseem(t)                 # "A" / "E" / "O" / "U" / "M" / "F" / "L" / None (stil)
    pop_short.poppetje(..., mond=luid, viseem=v)
"""
import re

REGELS = [("th", "L"), ("ee", "E"), ("ea", "E"), ("oo", "U"), ("ou", "O"), ("ow", "O"), ("oy", "O"), ("ai", "E"), ("ay", "E"),
          ("a", "A"), ("e", "E"), ("i", "E"), ("y", "E"), ("o", "O"), ("u", "U"), ("w", "U"),
          ("m", "M"), ("b", "M"), ("p", "M"), ("f", "F"), ("v", "F"), ("l", "L"), ("t", "L"), ("d", "L"), ("n", "L"),
          ("s", "E"), ("z", "E"), ("c", "E"), ("k", "E"), ("g", "E"), ("h", "A"), ("r", "O"), ("j", "E"), ("q", "U"), ("x", "E")]
KLINKER = set("AEOU")
GETAL = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}

def klanken(woord):
    w = re.sub(r"[^a-z0-9]", "", woord.lower())
    w = "".join(GETAL.get(c, c) for c in w)
    uit, i = [], 0
    while i < len(w):
        for letters, v in REGELS:
            if w.startswith(letters, i): uit.append(v); i += len(letters); break
        else: i += 1
    samen = []                                             # dubbele achter elkaar samenvoegen
    for v in uit:
        if not samen or samen[-1] != v: samen.append(v)
    return samen or ["E"]

class Lipsync:
    def __init__(self, woorden):
        self.tl = []                                       # (t0, t1, viseem)
        for _, w, t0, t1 in woorden:
            ks = klanken(w); gew = [2.0 if k in KLINKER else 1.0 for k in ks]; tot = sum(gew); t = t0
            for k, g in zip(ks, gew):
                d = (t1 - t0) * g / tot; self.tl.append((t, t + d, k)); t += d
        self.tl.sort()

    def viseem(self, t):
        lo, hi = 0, len(self.tl)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.tl[mid][1] < t: lo = mid + 1
            else: hi = mid
        if lo < len(self.tl) and self.tl[lo][0] - 0.03 <= t <= self.tl[lo][1] + 0.03: return self.tl[lo][2]
        return None
