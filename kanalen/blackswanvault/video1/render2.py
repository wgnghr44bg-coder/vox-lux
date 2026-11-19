"""BlackSwanVault video 1, versie 2 (eigenaar 19 nov 12:22): stijl zoals de goedgekeurde proef (vooral foto's met langzame zoom,
rustige grafieken en grote tekst op donker), video alleen waar die precies past (Trump, videokaart, servers), geen hoofdstukkaarten,
elke tekst/beeldwissel op de zin die op dat moment klinkt. Hergebruikt de hulpfuncties uit render.py.
Gebruik: python render2.py [--van s --tot s] [--plaat uit.jpg]"""
import sys
import render as R
from render import *   # noqa: F401,F403  (W, HH, fonts, kleuren, foto, vid, lijn, staven, txt, ...)

def zi(naam, t):                                   # index van de zin die nu klinkt (binnen de scene)
    k = 0
    while zin_t(naam, k + 1) <= t and zin_t(naam, k + 1) > zin_t(naam, k): k += 1
    return k
def zt(naam, k): return zin_t(naam, k)
CUR = [None, 0.0, 1.0]
ACHTER = {  # 19 nov: eerste proef was beter -> bijna altijd een passend beeld achter de tekst, zwart alleen voor grote momenten
 "open-vraag": "f:hq-atrium", "open-dennys": "f:riva-kaart", "h1-booth": "f:riva-chip", "h2-cuda": "f:gtc-b", "h2-alexnet": "v:rtx-a",
 "h3-iedereen": "f:dc-a", "h4-h20": "f:h100-b", "h4-megaspeed": "v:gh-rek", "h4-onderzoek": "f:dc-b", "h5-nyt": "f:hq-entry",
 "h5-congres": "f:hq-wall", "h5-druk": "f:hq-hq", "h6-cijfers": "f:dc-a", "h6-datacenter": "v:gh-servers", "h6-kress": "f:computex-b",
 "h7-waarom": "f:dc-b", "open-datacenter": "v:gh-servers"}
def donker_bg():
    b = ACHTER.get(CUR[0])
    if not b: return raster(leeg(), 0.6)
    naam, t, dur = CUR
    if b.startswith("v:"): return vid(b[2:], t, dur, donker=0.38, speed=0.7)
    return foto(b[2:], t, dur, (1.0, 1.08), donker=0.38)
def groot(img, t, s, kleur=WIT, y=HH // 2, size=150, sub=None, start=0.0):
    d = ImageDraw.Draw(img, "RGBA"); a = ease((t - start) / 0.35); sc = 1.25 - 0.25 * a
    txt(d, (W // 2, y), s, font(BOLD, int(size * sc)), kleur, a, "mm")
    if sub: txt(d, (W // 2, y + size * 0.75), sub, font(REG, 40), GRIJS, ease((t - start - 0.3) / 0.4), "mm")
    return img
def regels(img, t, rr, start=0.0, y=None, size=64, stap=0.5):
    d = ImageDraw.Draw(img, "RGBA"); y = y or HH // 2 - (len(rr) - 1) * size * 0.7
    for k, r in enumerate(rr):
        a = ease((t - start - k * stap) / 0.4); txt(d, (W // 2, y + k * size * 1.4 + 20 * (1 - a)), r, font(BOLD if k == 0 else REG, size if k == 0 else size * 0.7), WIT if k == 0 else GRIJS, a, "mm")
    return img

def S(naam, t, dur):
    k = zi(naam, t); CUR[:] = [naam, t, dur]
    if naam == "open-capitol":
        img = foto("huang-b", t, dur, (1.05, 1.16), (0.5, 0.42, 0.5, 0.38)); stempel(img, t - 0.3, "NOVEMBER 12, 2026"); return img
    if naam == "open-huang":
        img = foto("gtc-a", t, dur, (1.0, 1.08))
        if k == 0: lower_third(img, t - 0.2, "JENSEN HUANG", "Co-founder and CEO of Nvidia, 1993 to 2026")
        else: onder(img, t - zt(naam, 1), "The leather jacket. The keynotes. The AI gold rush.", 0)
        return img
    if naam in ("open-koers", "h5-koers"):
        img, _ = lijn(t, dur, "2026-10-20", "2026-11-18", "NVIDIA STOCK", "Daily closing price, October 20 to November 18, 2026",
                      markers=[("2026-10-29", "First report"), ("2026-11-08", "Letter"), ("2026-11-12", "Resigns"), ("2026-11-17", "Earnings")], teken=0.5)
        d = ImageDraw.Draw(img, "RGBA"); a = ease((t - dur * 0.5 - 0.2) / 0.4)
        txt(d, (1700, 330), "-29%", font(BLACK, 150), ROOD, a, "rm"); txt(d, (1700, 420), "Oct 29 to Nov 18", font(REG, 30), GRIJS, a, "rm")
        if naam == "open-koers" and k >= 1: txt(d, (1700, 490), "More than $1 trillion in value", font(BOLD, 36), WIT, ease((t - zt(naam, 1)) / 0.4), "rm")
        if naam == "h5-koers" and k >= 1: txt(d, (1700, 490), "Most valuable company in the world until Oct 30", font(BOLD, 32), WIT, ease((t - zt(naam, 1)) / 0.4), "rm")
        return img
    if naam == "open-datacenter":
        img = donker_bg()
        if k == 0: return groot(img, t, "And then...", WIT, size=110)
        if k == 1: return groot(img, t - zt(naam, 1), "RECORD QUARTER", GROEN, size=150, sub="Five days after he left")
        teller(img, t, 115.8, lambda v: f"${v:.1f}B", HH // 2 - 30, 200, GROEN, 1.4, zt(naam, 2))
        return regels(img, t - zt(naam, 2) - 0.6, ["", "revenue in three months"], y=HH // 2 + 70)
    if naam == "open-vraag":
        img = donker_bg(); d = ImageDraw.Draw(img, "RGBA")
        for i, r in enumerate(["A record quarter.", "A crashing stock.", "A founder gone."]):
            txt(d, (W // 2, 380 + i * 120), r, font(BLACK, 86), ROOD if i == 1 else WIT, ease((t - 0.4 - i * 1.0) / 0.4), "mm")
        return img
    if naam == "open-dennys":
        return groot(donker_bg(), t, "SAN JOSE, 1993", WIT, size=130, sub="A booth at a Denny's restaurant", start=0.3)
    if naam == "titel":
        img = foto("gtc-a", t, dur, (1.0, 1.05), donker=0.3); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (W // 2, 500), "THE MAN WHO", font(BOLD, 60), GRIJS, ease(t / 0.6), "mm")
        txt(d, (W // 2, 600), "BUILT NVIDIA", font(BLACK, 150), WIT, ease((t - 0.3) / 0.6), "mm"); logo_klein(img, ease((t - 0.6) / 0.5)); return img
    if naam == "h1-taiwan":
        img = foto("huang-g", t, dur, (1.0, 1.1), (0.55, 0.45, 0.6, 0.42))
        cap = ["Born in Taiwan, 1963", "Moved to the U.S. as a boy. Worked at Denny's", "Oregon State University. Stanford",
               "Chip designer at AMD and LSI Logic", "He wanted to build something of his own"]
        onder(img, t - zt(naam, k), cap[min(k, 4)], 0); return img
    if naam == "h1-booth":
        img = donker_bg(); d = ImageDraw.Draw(img, "RGBA"); stempel(img, t - 0.2, "APRIL 1993", DONKER)
        for i, (n, r) in enumerate([("JENSEN HUANG", "30, chip designer"), ("CHRIS MALACHOWSKY", "engineer"), ("CURTIS PRIEM", "engineer")]):
            a = ease((t - 0.8 - i * 0.7) / 0.5); x = 360 + i * 600
            d.rectangle([x - 260, 380, x + 260, 560], outline=(255, 255, 255, int(70 * a)), width=2)
            txt(d, (x, 445), n, font(BOLD, 40), WIT, a, "mm"); txt(d, (x, 505), r, font(REG, 30), GRIJS, a, "mm")
        if k >= 1: txt(d, (W // 2, 760), "One idea: a chip made only for 3D graphics", font(BOLD, 50), WIT, ease((t - zt(naam, 1)) / 0.4), "mm")
        return img
    if naam == "h1-concurrentie":
        img = donker_bg(); d = ImageDraw.Draw(img, "RGBA"); weg = ease((t - zt(naam, 1)) / 2.5)
        txt(d, (W // 2, 150), "3D GRAPHICS CHIP COMPANIES, 1990s", font(BOLD, 44), WIT, ease(t / 0.4), "mm")
        rng = np.random.default_rng(4)
        for i in range(48):
            x = 330 + (i % 12) * 105; y = 330 + (i // 12) * 130; nv = i == 17
            a = ease((t - i * 0.03) / 0.3); al = a * (1 if nv else max(0.0, 1 - weg * (0.6 + rng.random())))
            d.rounded_rectangle([x, y, x + 80, y + 80], 12, fill=(GROEN if nv and weg > 0.5 else (70, 72, 80)) + (int(255 * al),))
        if k >= 1: txt(d, (W // 2, 930), "Most of them would not survive.", font(BOLD, 48), WIT, ease((t - zt(naam, 1)) / 0.4), "mm")
        if k >= 3: txt(d, (W // 2, 230), "Nvidia almost didn't either.", font(BOLD, 44), ROOD, ease((t - zt(naam, 3)) / 0.4), "mm")
        return img
    if naam == "h1-flop":
        img = donker_bg()
        if k == 0: return groot(img, t, "1995: NV1", WIT, size=130, sub="A flop", start=0.2)
        return groot(img, t - zt(naam, 1), "Running out of money", ROOD, size=100)
    if naam == "h1-riva":
        if k == 0:
            img = foto("riva-kaart", t, dur, (1.0, 1.08), donker=0.75); lower_third(img, t - 0.2, "RIVA 128", "1997"); return img
        img = foto("riva-chip", t, dur, (1.0, 1.1), donker=0.5)
        if k <= 2:
            teller(img, t, 1_000_000, lambda v: f"{v:,.0f}", HH // 2 - 20, 150, WIT, 1.6, zt(naam, 1))
            regels(img, t - zt(naam, 1) - 0.6, ["", "units in four months"], y=HH // 2 + 70)
            if k == 2: onder(img, t - zt(naam, 2), "Nvidia was saved", 0)
        else: onder(img, t - zt(naam, 3), "“Always thirty days from going out of business”", 0)
        return img
    if naam == "h1-geforce":
        if k == 0:
            img = foto("geforce-kaart", t, dur, (1.0, 1.08), donker=0.75); stempel(img, t - 0.2, "1999: NVIDIA GOES PUBLIC", DONKER)
            if t > 3: lower_third(img, t - 3, "GEFORCE 256", "Marketed as “the world's first GPU”")
            return img
        img = vid("rtx-b", t, dur, donker=0.7, speed=0.8); onder(img, t - zt(naam, 1), "Graphics cards for gamers", 0.3); return img
    if naam == "h2-idee":
        return R.S("h2-idee", t, dur)
    if naam == "h2-cuda":
        img = donker_bg()
        if k == 0: return groot(img, t, "2006: CUDA", GROEN, size=140, sub="Use graphics chips for almost any kind of math", start=0.2)
        return regels(img, t - zt(naam, 1), ["Wall Street didn't get it.", "Expensive to build, almost no money for years"])
    if naam == "h2-alexnet":
        img = donker_bg()
        if k == 0: return groot(img, t, "2012: ALEXNET", WIT, size=130, sub="Trained on two Nvidia gaming cards", start=0.2)
        if k == 1: return regels(img, t - zt(naam, 1), ["KRIZHEVSKY  ·  SUTSKEVER  ·  HINTON", "University of Toronto"])
        if k in (2, 3): return groot(img, t - zt(naam, 2), "AI discovers Nvidia", GROEN, size=110)
        if k == 4: return regels(img, t - zt(naam, 4), ["Geoffrey Hinton", "Nobel Prize, 2024"])
        return regels(img, t - zt(naam, 5), ["Ilya Sutskever", "Co-founder of OpenAI"])
    if naam == "h2-openai":
        img = foto("gtc-b", t, dur, (1.0, 1.08), donker=0.55); stempel(img, t - 0.2, "2016: FIRST DGX-1", GROEN)
        if k >= 1: groot(img, t - zt(naam, 1), "OpenAI", WIT, size=150)
        return img
    if naam == "h3-chatgpt":
        img = donker_bg(); stempel(img, t - 0.2, "NOVEMBER 30, 2022", ROOD)
        if k == 0: return groot(img, t, "ChatGPT", WIT, size=170, start=0.3)
        teller(img, t, 100_000_000, lambda v: f"{v:,.0f}", HH // 2 - 20, 140, WIT, 2.0, zt(naam, 1))
        return regels(img, t - zt(naam, 1) - 0.6, ["", "users in about two months (estimated)"], y=HH // 2 + 70)
    if naam == "h3-iedereen":
        if k <= 3:
            img = donker_bg(); d = ImageDraw.Draw(img, "RGBA")
            if k == 0: return groot(img, t, "Everyone wanted AI", WIT, size=110)
            for i, n in enumerate(["MICROSOFT", "GOOGLE", "META", "AMAZON"]):
                txt(d, (W // 2, 300 + i * 110), n, font(BLACK, 80), WIT, ease((t - zt(naam, 1) - i * 0.35) / 0.35), "mm")
            if k == 3: onder(img, t - zt(naam, 3), "All needed Nvidia chips", 0)
            return img
        img = foto("dgx-b200", t, dur, (1.0, 1.08), donker=0.5)
        cap = {4: "Months-long waiting lists", 5: "Startups bragged about how many they owned", 6: "Almost a currency of their own"}
        onder(img, t - zt(naam, k), cap.get(k, ""), 0); return img
    if naam == "h3-omzet":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (200, 110), "NVIDIA ANNUAL REVENUE", font(BOLD, 50)); txt(d, (200, 175), "Fiscal years, in billions of US dollars", font(REG, 30), GRIJS)
        labels, waarden = ["FY2023", "FY2024", "FY2025", "FY2026"], [27.0, 60.9, 130.5, 215.9]
        for i, (lab, v) in enumerate(zip(labels, waarden)):
            p = ease((t - zt(naam, i + 1)) / 0.8) if zt(naam, i + 1) > 0 else 0
            x = 330 + i * 360; h = 560 * v / 230 * p
            if p > 0:
                d.rectangle([x, 900 - h, x + 220, 900], fill=(GROEN if i == 3 else (60, 140, 90)) + (255,))
                txt(d, (x + 110, 900 - h - 14), f"${v * p:.1f}B", font(BOLD, 36), WIT, min(1, p * 2), "ms")
            txt(d, (x + 110, 925), lab, font(REG, 30), GRIJS, 1, "ma")
        bron(img, "Source: Nvidia annual reports (SEC filings)"); return img
    if naam == "h3-ster":
        if k <= 1:
            img = foto("huang-c" if k == 0 else "huang-b", t, dur, (1.05, 1.15))
            onder(img, t - zt(naam, k), "A celebrity CEO" if k == 0 else "Sold-out keynotes. Crowds of fans.", 0); return img
        if k == 2:
            img = foto("gtc-a", t, dur, (1.08, 1.0)); onder(img, t - zt(naam, 2), "Every year, the black leather jacket", 0); return img
        img = foto("computex-b", t, dur, (1.0, 1.06), donker=0.4); d = ImageDraw.Draw(img, "RGBA"); t2 = t - zt(naam, 3)
        for i, n in enumerate(["HOPPER", "BLACKWELL", "VERA RUBIN"]):
            a = ease((t2 - i * 0.6) / 0.4); txt(d, (420 + i * 540, HH // 2), n, font(BLACK, 72), GROEN if i == 2 else WIT, a, "mm")
            if i < 2: txt(d, (690 + i * 540, HH // 2), "→", font(BOLD, 60), GRIJS, a, "mm")
        return img
    if naam == "h4-h20":
        img = donker_bg(); d = ImageDraw.Draw(img, "RGBA")
        if k >= 2: return regels(img, t - zt(naam, 2), ["Every rule change, a new chip.", "Security for Washington. Billions for Nvidia."] if k >= 3 else ["Every rule change, a new chip."])
        for i, (n, s_, c) in enumerate([("TOP AI CHIPS", "Banned for China", ROOD), ("H20", "Weaker version, made for China", GROEN)]):
            a = ease((t - (0.3 if i == 0 else zt(naam, 1))) / 0.5); x = 560 + i * 800
            d.rectangle([x - 320, 380, x + 320, 640], outline=c + (int(255 * a),), width=4)
            txt(d, (x, 470), n, font(BLACK, 64), c, a, "mm"); txt(d, (x, 560), s_, font(REG, 34), WIT, a, "mm")
        return img
    if naam == "h4-h200":
        img = vid("trump", t, dur, donker=0.75, speed=1.0, zoom=(1.0, 1.04)); stempel(img, t - 0.2, "DECEMBER 2025", DONKER)
        onder(img, t, "President Trump: Nvidia may sell the H200 to China", 0.5); return img
    if naam == "h4-megaspeed":
        img = donker_bg(); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (W // 2, 300), "MEGASPEED", font(BLACK, 110), WIT, ease(t / 0.5), "mm")
        txt(d, (W // 2, 380), "AI computing centers in Asia", font(REG, 36), GRIJS, ease(t / 0.5), "mm")
        if k >= 1:
            teller(img, t, 4.8, lambda v: f"${v:.1f} BILLION", 600, 120, GROEN, 1.4, zt(naam, 1) + 2.5)
            txt(d, (W // 2, 700), "of Nvidia equipment, according to The New York Times", font(REG, 34), GRIJS, ease((t - zt(naam, 1) - 3) / 0.5), "mm")
            tag(img, t - zt(naam, 1) - 2.5, "REPORTED", 150, 860)
        return img
    if naam == "h4-onderzoek":
        img = donker_bg(); d = ImageDraw.Draw(img, "RGBA")
        if k == 0: return regels(img, t, ["UNITED STATES  ·  SINGAPORE", "investigating possible export violations"])
        if k == 1: return regels(img, t - zt(naam, 1), ["“Completely normal”", "Jensen Huang to Bloomberg, about his dealings with Megaspeed"])
        return regels(img, t - zt(naam, 2), ["“No reason to believe products had been diverted”", "Nvidia"], size=54)
    if naam == "h4-vrouw":
        return regels(donker_bg(), t, ["A former senior executive at Megaspeed", "who knew Jensen Huang personally"], start=0.3)
    if naam == "h5-nyt":
        img = donker_bg(); stempel(img, t - 0.2, "OCTOBER 29", ROOD)
        if k == 0: return regels(img, t, ["The New York Times reports", "a close relationship with the executive"], start=0.3)
        return regels(img, t - zt(naam, 1), ["Nvidia: “not unusual or unexpected”"])
    if naam == "h5-congres":
        if k == 0:
            img = donker_bg(); stempel(img, t - 0.2, "NOVEMBER 5", ROOD)
            return regels(img, t, ["Congress wants answers", "Three Republican committee chairmen request a briefing"], start=0.3)
        img, _ = lijn(t - zt(naam, 1), dur - zt(naam, 1), "2026-11-03", "2026-11-05", "NVIDIA STOCK", "November 3 to 5, 2026", teken=0.4)
        txt(ImageDraw.Draw(img, "RGBA"), (1700, 330), "-9.3%", font(BLACK, 140), ROOD, ease((t - zt(naam, 1) - 1) / 0.4), "rm"); return img
    if naam == "h5-board":
        if k <= 1:
            img = foto("hq-atrium", t, dur, (1.0, 1.06), donker=0.45); stempel(img, t - 0.2, "NVIDIA BOARD", DONKER)
            return regels(img, t - zt(naam, k), ["Independent investigation", "Was Huang targeted by a foreign intelligence service?"] if k == 0 else ["“The Board has confidence in Jensen”"])
        if k == 2:
            img = vid("trump", t - zt(naam, 2), dur, donker=0.75, speed=1.0, zoom=(1.04, 1.0))
            onder(img, t - zt(naam, 2), "Trump: Huang is “a fine person” and should stay", 0.2); return img
        img, _ = lijn(t - zt(naam, 3), dur - zt(naam, 3), "2026-11-06", "2026-11-09", "NVIDIA STOCK", "November 6 to 9, 2026", teken=0.4)
        txt(ImageDraw.Draw(img, "RGBA"), (1700, 330), "-4.3%", font(BLACK, 140), ROOD, ease((t - zt(naam, 3) - 1.2) / 0.4), "rm"); return img
    if naam == "h5-druk":
        img = donker_bg(); d = ImageDraw.Draw(img, "RGBA")
        if k == 0: return groot(img, t, "The pressure builds", WIT, size=110)
        for i, s_ in enumerate(["More reports", "Talk of a subpoena", "Justice Department takes over the investigation"]):
            txt(d, (W // 2, 360 + i * 130), s_, font(BOLD, 66), WIT, ease((t - zt(naam, 1) - i * 1.4) / 0.4), "mm")
        tag(img, t - zt(naam, 1) - 2.8, "REPORTED", W // 2 - 90, 640); return img
    if naam == "h5-ontslag":
        if k == 0:
            img = foto("huang-h", t, dur, (1.05, 1.15), (0.6, 0.45, 0.62, 0.42), grijs=True); stempel(img, t - 0.2, "NOVEMBER 12: RESIGNS", ROOD); return img
        img = foto("hq-hq", t, dur, (1.0, 1.06), donker=0.35); d = ImageDraw.Draw(img, "RGBA")
        if k in (1, 3):
            txt(d, (W // 2, 430), "COLETTE KRESS", font(BLACK, 100), WIT, ease((t - zt(naam, 1)) / 0.4), "mm")
            txt(d, (W // 2, 520), "Interim CEO" + ("  ·  CFO since 2013" if k == 3 else ""), font(REG, 40), GRIJS, 1, "mm")
        elif k == 2: groot(img, t - zt(naam, 2), "Huang will testify before Congress", WIT, size=80)
        elif k == 4: regels(img, t - zt(naam, 4), ["HARVEY JONES", "First chair of the board"])
        else: regels(img, t - zt(naam, 5), ["Democrats open their own investigation", "into the government's handling of chip sales to China"], size=58)
        return img
    if naam == "h6-cijfers":
        img = donker_bg(); stempel(img, t - 0.2, "NOVEMBER 17", GROEN)
        if k == 0: return groot(img, t, "Earnings day", WIT, size=110)
        teller(img, t, 115.8, lambda v: f"${v:.1f}B", HH // 2 - 40, 200, GROEN, 1.6, zt(naam, 1))
        if k >= 2: regels(img, t - zt(naam, 2), ["+103% vs. a year earlier"], y=HH // 2 + 120)
        return img
    if naam == "h6-datacenter":
        if k == 0:
            img = vid("gh-servers", t, dur, donker=0.55, speed=0.7); teller(img, t, 107.6, lambda v: f"${v:.1f}B", 480, 170, GROEN, 1.5, 0.3)
            regels(img, t - 0.8, ["", "from data center chips alone"], y=600); return img
        img = donker_bg(); return regels(img, t - zt(naam, 1), ["NEXT QUARTER: ~$130 BILLION", "with no data center chip sales to China"], size=76)
    if naam == "h6-kress":
        if k <= 1:
            img = donker_bg(); return regels(img, t - zt(naam, k), ["No more H200 sales in China", "Colette Kress, interim CEO"] if k == 0 else ["VERA RUBIN", "Nvidia's next generation of chips"])
        return citaat(t - zt(naam, 2), dur, ["Vera Rubin is off to an explosive start.", "Our roadmap is on track, and our", "ambition has never been greater."],
                      "Colette Kress, interim CEO, November 17, 2026", donker_bg())
    if naam == "h7-waarom":
        img = donker_bg()
        if k == 0: return groot(img, t, "Why sell?", WIT, size=140)
        if k in (1, 2): return regels(img, t - zt(naam, 1), ["Markets don't pay for the past.", "They pay for the future."] if k == 2 else ["Markets don't pay for the past."])
        d = ImageDraw.Draw(img, "RGBA")
        for i in range(3): txt(d, (660 + i * 300, HH // 2), "?", font(BLACK, 220), ROOD, ease((t - zt(naam, 3) - i * 0.3) / 0.3), "mm")
        return img
    vragen = {"h7-china": (1, "CHINA", "computex-a"), "h7-leider": (2, "LEADERSHIP", "huang-a"), "h7-bubbel": (3, "THE AI BOOM", "dc-a")}
    if naam in vragen:
        nr, titel, ft = vragen[naam]; img = foto(ft, t, dur, (1.0, 1.08), donker=0.4); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (200, 230), f"QUESTION {nr}", font(BOLD, 40), ROOD, ease(t / 0.4)); txt(d, (200, 280), titel, font(BLACK, 110), WIT, ease((t - 0.2) / 0.4))
        cap = {"h7-china": {1: "Was American technology put at risk?"},
               "h7-leider": {2: "CEO. Face of the company. Chief salesman.", 3: "Can Nvidia convince the world it doesn't need him?"},
               "h7-bubbel": {1: "Hundreds of billions spent on AI chips", 2: "If spending slows, Nvidia feels it first"}}[naam]
        if k in cap: onder(img, t - zt(naam, k), cap[k], 0)
        if naam == "h7-leider" and k >= 4:
            for i, (a_, b_) in enumerate([("APPLE", "after Steve Jobs"), ("MICROSOFT", "after Bill Gates")]):
                a = ease((t - zt(naam, 4) - i * 0.5) / 0.4); txt(d, (200, 520 + i * 120), a_, font(BLACK, 60), WIT, a); txt(d, (620, 540 + i * 120), b_, font(REG, 40), GRIJS, a)
        if naam == "h7-bubbel" and k >= 3:
            for i, n in enumerate(["AMD", "GOOGLE", "AMAZON", "MICROSOFT"]):
                txt(d, (200 + i * 400, 620), n, font(BLACK, 56), WIT, ease((t - zt(naam, 3) - i * 0.35) / 0.35))
            txt(d, (200, 700), "all building AI chips of their own", font(REG, 38), GRIJS, ease((t - zt(naam, 3) - 1.5) / 0.4))
        return img
    if naam == "h7-getuigenis":
        img = foto("huang-f", t, dur, (1.0, 1.08), donker=0.55); stempel(img, t - 0.2, "BEFORE THANKSGIVING", ROOD)
        onder(img, t, "Jensen Huang testifies before Congress", 0.4); return img
    if naam == "slot-zwaan":
        img = donker_bg()
        if k == 0: return regels(img, t, ["An event nobody sees coming,", "but that changes everything"], start=0.3)
        return groot(img, t - zt(naam, 1), "BLACK SWAN", WIT, size=170)
    if naam == "slot-twee":
        return foto("hq-entry", t, dur, (1.0, 1.1), donker=0.55)
    if naam == "slot-dennys":
        img = foto("huang-g", t, dur, (1.0, 1.08), (0.55, 0.45, 0.58, 0.43), grijs=True, donker=0.5)
        if k >= 1: onder(img, t - zt(naam, 1), "From a booth at Denny's. No longer running it.", 0)
        return img
    if naam == "slot-abonneer":
        img = leeg(); d = ImageDraw.Draw(img, "RGBA"); logo_klein(img, ease(t / 0.6))
        txt(d, (W // 2, 420), "BLACKSWANVAULT", font(BLACK, 90), WIT, ease((t - 0.3) / 0.5), "mm")
        txt(d, (W // 2, 500), "Subscribe and step inside the vault", font(REG, 40), GRIJS, ease((t - 0.6) / 0.5), "mm")
        if t > dur - 1.0: img = Image.blend(img, Image.new("RGB", (W, HH)), (t - (dur - 1.0)) / 1.0)
        return img
    return R.S(naam, t, dur)          # overige scenes (grafieken, citaten) zoals in render.py

R.S = S if False else R.S
def frame(t):
    for naam, s, e, _ in SCENES:
        if s <= t < e: R.HUIDIG[0] = naam; return S(naam, t - s, e - s), naam
    n = SCENES[-1]; return S(n[0], t - n[1], n[2] - n[1]), n[0]

def main():
    van = float(sys.argv[sys.argv.index("--van") + 1]) if "--van" in sys.argv else 0
    tot = float(sys.argv[sys.argv.index("--tot") + 1]) if "--tot" in sys.argv else EIND
    uit = R.H / ("video-ruw.mp4" if van == 0 and tot == EIND else f"stuk-{van:.0f}-{tot:.0f}.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{HH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(uit)], stdin=subprocess.PIPE)
    vorige, wissel, laatste_vorige = None, -1, None
    for i in range(int(van * FPS), int(tot * FPS)):
        t = i / FPS; img, naam = frame(t)
        if naam != vorige and vorige is not None: wissel = i
        if 0 <= i - wissel < 8 and laatste_vorige is not None: img = Image.blend(laatste_vorige, img, (i - wissel + 1) / 9)
        else: laatste_vorige = img
        vorige = naam; p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait(); print("KLAAR", uit.name, flush=True)

if __name__ == "__main__":
    if "--plaat" in sys.argv:                    # per zin een beeld, met de zin eronder
        uit = sys.argv[sys.argv.index("--plaat") + 1]; Z = R.Z
        van = int(sys.argv[sys.argv.index("--zinnen") + 1]) if "--zinnen" in sys.argv else 0
        Zs = Z[van:van + 30]; kol = 5; rij = (len(Zs) + kol - 1) // kol
        s = Image.new("RGB", (kol * 400, rij * 290), (25, 25, 25)); dd = ImageDraw.Draw(s); f = font(REG, 13)
        for i, (a, b, zin, sc) in enumerate(Zs):
            t = a + min(1.8, (b - a) * 0.7); img, _ = frame(t); R.Vid._open.clear()
            x, y = (i % kol) * 400, (i // kol) * 290; s.paste(img.resize((400, 225)), (x, y))
            regel = zin if len(zin) < 62 else zin[:60] + "..."
            dd.text((x + 3, y + 228), f"{van + i} {sc}", font=f, fill=(255, 220, 0)); dd.text((x + 3, y + 246), regel, font=f, fill=(230, 230, 230))
        s.save(uit); print("plaat", len(Zs))
    else:
        main()
