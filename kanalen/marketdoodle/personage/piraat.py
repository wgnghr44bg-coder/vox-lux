"""Captain Discount: eigen piratenkapitein in de pop_short-stijl (26 nov 2026; bewust GEEN Jack Sparrow/Disney).
Gebruik: ps.C["piraat"] = PIRAAT; poppetje(d, "piraat", ...) tekenen, laag plakken, daarna versier(img, hx, top, s, x, y).
(hx, top) = wat poppetje() teruggeeft; s = dezelfde schaal als bij poppetje (zonder 'groot')."""
from PIL import ImageDraw
PIRAAT = dict(broek=(95, 70, 50), shirt=(240, 232, 210), haar=(45, 32, 25), kapsel="kort", groot=1.12)
INK = (40, 35, 40)

def versier(img, hx, top, s, x, y):
    S = s * PIRAAT["groot"]; R = 60 * S; cy = top + R
    d = ImageDraw.Draw(img)
    for k, dx in enumerate((-1.18, -1.0, 1.0, 1.18)):                 # haarslierten met gouden kraaltjes
        sx = hx + dx * R; lang = (1.45 if k % 2 else 1.2) * R
        d.rounded_rectangle((sx - 0.09 * R, cy - 0.15 * R, sx + 0.09 * R, cy + lang), max(1, int(0.09 * R)), fill=(45, 32, 25), outline=INK, width=3)
        by = cy + lang - 0.25 * R; d.ellipse((sx - 0.12 * R, by - 0.12 * R, sx + 0.12 * R, by + 0.12 * R), fill=(230, 180, 60), outline=INK, width=2)
    d.chord((hx - 1.03 * R, cy - 1.04 * R, hx + 1.03 * R, cy + 0.35 * R), 180, 360, fill=(200, 40, 45), outline=INK, width=4)   # bandana
    for q in range(4): d.ellipse((hx - 0.62 * R + q * 0.4 * R, cy - 0.5 * R, hx - 0.52 * R + q * 0.4 * R, cy - 0.4 * R), fill=(255, 235, 235))
    d.polygon([(hx - 0.98 * R, cy - 0.3 * R), (hx - 1.4 * R, cy - 0.05 * R), (hx - 1.25 * R, cy + 0.12 * R), (hx - 0.93 * R, cy - 0.12 * R)], fill=(200, 40, 45), outline=INK)
    d.polygon([(hx - 1.35 * R, cy - 0.95 * R), (hx, cy - 0.68 * R), (hx + 1.35 * R, cy - 0.95 * R), (hx + 0.85 * R, cy - 1.55 * R), (hx, cy - 1.45 * R), (hx - 0.85 * R, cy - 1.55 * R)],
              fill=(80, 55, 40), outline=INK)                          # driekantige hoed
    d.line([(hx - 1.3 * R, cy - 0.95 * R), (hx, cy - 0.72 * R), (hx + 1.3 * R, cy - 0.95 * R)], fill=(210, 170, 80), width=max(2, int(0.04 * R)))
    for kant in (-1, 1):                                               # snor
        d.polygon([(hx, cy + 0.36 * R), (hx + kant * 0.3 * R, cy + 0.34 * R), (hx + kant * 0.42 * R, cy + 0.24 * R), (hx + kant * 0.4 * R, cy + 0.42 * R), (hx + kant * 0.05 * R, cy + 0.45 * R)], fill=(35, 25, 20), outline=INK)
    d.polygon([(hx - 0.13 * R, cy + 0.78 * R), (hx + 0.13 * R, cy + 0.78 * R), (hx, cy + 1.12 * R)], fill=(35, 25, 20), outline=INK)   # sikje
    d.rectangle((hx + 0.03 * R, cy + 0.44 * R, hx + 0.15 * R, cy + 0.54 * R), fill=(240, 200, 60), outline=INK, width=2)              # gouden tand
    heup = y - 78 * S - 14 * S                                         # rode sjerp
    d.rectangle((x - 50 * S, heup - 18 * S, x + 50 * S, heup + 4 * S), fill=(200, 40, 45), outline=INK, width=4)
    d.polygon([(x + 30 * S, heup + 4 * S), (x + 52 * S, heup + 50 * S), (x + 34 * S, heup + 52 * S)], fill=(200, 40, 45), outline=INK)
    return hx, cy
