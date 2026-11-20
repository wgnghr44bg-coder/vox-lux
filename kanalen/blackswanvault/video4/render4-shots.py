
PCT = lambda v: f"-{v:.1f}%"
SHOTS = [
 (0.0, fasen(F("nasdaq-b", (1.0, 1.1), 0.55), [(0, ST("NOVEMBER 19, 2026")), (1, GR("+17%", "Anthropic's first day, vs its offering price", GROEN, 170))])),
 (ZR(2) - 0.15, fasen(F("nasdaq-bel", (1.08, 1.0), 0.5), [(2, ON("It was supposed to be a celebration")), (3, GR("THEN THE MARKET FELL", None, ROOD, 110))])),
 (ZR(4) - 0.15, lijst("wallst", "Thursday, November 19", [(4, "S&P 500: -2%"), (5, "Nasdaq: -2.25%"), (6, "Dow: below 50,000, first time since June")])),
 (ZR(7) - 0.15, koersgrafiek("nasdaq", "2026-09-01", "2026-11-19", "NASDAQ COMPOSITE", "Daily close, September to November 2026", YB,
                             markers=[("2026-10-06", "Peak")], labels=[("2026-11-18", 1700, 330, "-13.5%", ROOD)], teken=0.8)),
 (ZR(8) - 0.15, fasen(F("nasdaq-a", (1.0, 1.08), 0.35), [(8, GR("-10%", None, WIT, 190)), (9, GR("CORRECTION", "a fall of 10% from the peak", ORANJE, 150)),
                                                       (10, GR("-20%", None, WIT, 190)), (11, GR("BEAR MARKET", "a fall of 20% from the peak", ROOD, 150))])),
 (ZR(12) - 0.15, fasen(F("ai-trader-rood", (1.0, 1.08), 0.5), [(12, GR("What are investors afraid of?", None, WIT, 90)), (14, GR("4 FEARS", None, ORANJE, 190))])),
 (ZR(15) - 0.15, koersgrafiek("sp500", "2026-11-03", "2026-11-19", "S&P 500", "Daily close, November 3 to 19, 2026", YB,
                              labels=[("2026-11-19", 1700, 330, "6 DAYS DOWN", ROOD)], teken=0.85)),
 (ZR(17) - 0.15, balken([("Dow Jones", 6.2), ("S&P 500", 5.0), ("Nasdaq", 5.0)], "THIS WEEK, MONDAY TO THURSDAY", "Percent lost", "Source: CNBC", PCT, [17, 18, 18], kleur=ROOD)),
 (ZR(19) - 0.15, lijst("ai-tokyo-nacht", "Friday in Asia", [(20, "Nikkei: -5.06%"), (21, "Kospi: -5.21%"), (22, "Samsung: -7%")])),
 (ZR(23) - 0.15, fasen(F("nasdaq-c", (1.0, 1.06), 0.4), [(23, ON("(rest volgt)"))])),
]
