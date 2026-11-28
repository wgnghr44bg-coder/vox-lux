"""Shortregels (eigenaar 27 nov 2026: "zorg dat je je eraan houdt, elke nieuwe video, zet dat vast").
De drie regels uit de Studio-analyse (Shorts bleven steken op ± 1.200 views: 40-48% swipete weg in seconde 0-6, afhaken rond 30 s):
  1. HAAK     de eerste zin begint met "What if" en de vraag (tot het eerste ?) is binnen MAX_VRAAG s uitgesproken;
              in het allereerste beeld (t = 0,3 s) staat al iets bijzonders: minstens één voorwerp/grafiek naast de
              achtergrond en de poppetjes (game-HUD, haai, pijl, -90% ...). Een leeg beeld met alleen een poppetje = FOUT.
  2. LENGTE   30-38 seconden (28 nov, Studio-vergelijking: shorts verliezen kijkers in de laatste 10 s; was 35-45).
  3. LOOP     de laatste zin moet terugwijzen naar het begin: hij noemt het onderwerp van de vraag opnieuw (een
              kernwoord uit de eerste zin) of eindigt met een vervolg-haak ("never ends", "way worse", "day thirty" ...).
  4. VRAAG    (28 nov, Studio: bijna geen reacties) in de laatste 3 s staat een keuze-/debatvraag in beeld (tekst met "?"),
              bv. "WHICH POWER WOULD YOU PICK? 👇". Geef de schermteksten van het eind mee als teksten_eind.
Gebruik in een Short-renderer (na het tekenen van frame(0.3)):
    from shortregels import controleer
    fouten = controleer(Z, EIND, voorwerpen_bij_start=[naam for naam, box in WACHT.dit_frame], teksten_eind=[...])
    print("SHORTREGELS:", fouten or "alles goed")
"""
import re
MAX_VRAAG, MIN_S, MAX_S = 3.2, 30.0, 38.0
STOP = {"what", "if", "you", "your", "the", "a", "an", "was", "were", "is", "are", "that", "can", "could", "and", "there's", "over", "of",
        "to", "in", "on", "it", "every", "single", "day", "never", "ended", "built", "real", "life"}
VERVOLG = ("never ends", "way worse", "day thirty", "and it never", "that's why", "only day one", "again")

def controleer(Z, eind, voorwerpen_bij_start=(), woorden=None, teksten_eind=None):
    """woorden = [[zin, woord, t0, t1], ...] (scriptwoorden met tijden) -> precieze tijd van het vraagteken."""
    fout = []
    z0 = Z[0][2]
    if not z0.lower().startswith("what if"): fout.append(f'HAAK: eerste zin begint niet met "What if": {z0[:60]}')
    if "?" in z0:
        vraag = z0[:z0.index("?") + 1]; n = len(vraag.split()); tot = len(z0.split())
        t_vraag = Z[0][0] + (Z[0][1] - Z[0][0]) * n / max(1, tot)
        ww = [w for w in (woorden or []) if w[0] == 0]
        if len(ww) >= n: t_vraag = ww[n - 1][3]
        if t_vraag > MAX_VRAAG: fout.append(f"HAAK: de vraag is pas na {t_vraag:.1f} s uitgesproken (max {MAX_VRAAG})")
    else: fout.append("HAAK: geen vraag (?) in de eerste zin")
    if not [v for v in voorwerpen_bij_start if v]: fout.append("HAAK: in het eerste beeld staat niets bijzonders (alleen achtergrond/poppetjes)")
    if not (MIN_S <= eind <= MAX_S): fout.append(f"LENGTE: {eind:.1f} s (moet {MIN_S:.0f}-{MAX_S:.0f} s)")
    laatste = Z[-1][2].lower(); kern = {w for w in re.findall(r"[a-z0-9']+", z0.lower()) if w not in STOP and len(w) > 2}
    if not (kern & set(re.findall(r"[a-z0-9']+", laatste)) or any(v in laatste for v in VERVOLG)):
        fout.append(f'LOOP: laatste zin wijst niet terug naar het begin ("{Z[-1][2][:60]}")')
    if not any("?" in (t or "") for t in (teksten_eind or [])): fout.append("VRAAG: aan het eind staat geen keuzevraag in beeld (bv. WHICH ... WOULD YOU PICK? 👇)")
    return fout
