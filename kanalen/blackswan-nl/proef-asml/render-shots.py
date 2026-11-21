
# ---------- Geldverhaal proef ASML (zinnummers = zinnen.json) ----------
YB = "Bron: Yahoo Finance, slotkoersen"
SHOTS = [
 (0.0, fasen(F("asml-hq", (1.0, 1.08), 0.55), [(0, ST("VRIJDAG 20 NOVEMBER")), (1, GR("-9,3%", "ASML in Amsterdam, slot €1.168", ROOD, 190))])),
 (ZR(2) - 0.15, koersgrafiek("asml", "2026-06-01", "2026-11-20", "ASML (AMSTERDAM)", "Slotkoers in euro, 1 juni t/m 20 november 2026", YB,
                             markers=[("2026-06-30", "Top")], labels=[("2026-11-20", 1700, 330, "-32%", ROOD)], teken=0.8, eenheid="€")),
 (ZR(4) - 0.15, fasen(F("nvidia-bord", (1.0, 1.08), 0.5), [(4, ON("ASML stond er niet alleen voor")), (5, GR("-14%", "Nvidia, vrijdag 20 november", ROOD, 190))])),
 (ZR(6) - 0.15, fasen(F("ai-rood", (1.08, 1.0), 0.5), [(6, GR("-5,6%", "Nasdaq 100, de Amerikaanse techbeurs", ROOD, 170))])),
 (ZR(6.55) - 0.15, fasen(F("beurs-a", (1.0, 1.08), 0.45), [(6.55, GR("-2,4%", "AEX, de beurs van Amsterdam", ROOD, 170))])),
 (ZR(7) - 0.15, fasen(F("ai-bubbel", (1.0, 1.08), 0.55), [(7, GR("Wat is er aan de hand?", None, WIT, 100)), (8, GR("BARST DE AI-BUBBEL?", None, ORANJE, 120)),
                                                          (9, ON("En wat betekent het voor ASML, en voor jouw geld?"))])),
 (ZR(10) - 0.15, fasen(F("ai-twijfel", (1.0, 1.08), 0.5), [(10, ON("Beleggers twijfelen: levert AI genoeg op?"))])),
 (ZR(11) - 0.15, fasen(F("ai-twijfel", (1.08, 1.0), 0.5), [(11, ON("ASML voelt het als een van de eersten"))])),
 (ZR(12) - 0.15, fasen(F("asml-hq", (1.08, 1.0), 0.55, pan=(0.4, 0.4, 0.5, 0.45)), [(12, LT("ASML, VELDHOVEN", "Zonder de machines van ASML geen nieuwste chips"))])),
]
