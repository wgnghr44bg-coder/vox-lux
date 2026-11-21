
# ---------- Geldverhaal video 1: ASML zakt 9% (zinnen per @scene; S(scene, k) = k-de zin van die scene) ----------
# Regels eigenaar: echte beelden waar het mag en past; geen personen die het niet zijn (AI-beelden zonder mensen);
# grafieken met top en laagste; tekst in beeld in het Nederlands.
_SC = {}
for _i, _z in enumerate(Z): _SC.setdefault(_z[3], _i)
def S(sc, k=0.0): return _SC[sc] + k
def T(sc, k=0.0): return ZR(S(sc, k)) - 0.15
YB = "Bron: Yahoo Finance, slotkoersen"
MLD = lambda v: f"${v:.1f} mld".replace(".", ",")
SHOTS = [
 # --- opening ---
 (0.0, fasen(F("asml-hq", (1.0, 1.08), 0.55), [(S("open-val"), ST("VRIJDAG 20 NOVEMBER")), (S("open-val", 1), GR("-9,3%", "ASML in Amsterdam, slot €1.168", ROOD, 190))])),
 (T("open-top"), koersgrafiek("asml", "2026-06-01", "2026-11-20", "ASML (AMSTERDAM)", "Slotkoers in euro, 1 juni t/m 20 november 2026", YB,
                             labels=[("2026-11-20", 1700, 330, "-32%", ROOD)], teken=0.8, eenheid="€", eind_label=False)),
 (T("open-meer"), fasen(F("nvidia-bord", (1.0, 1.08), 0.5), [(S("open-meer"), ON("ASML stond er niet alleen voor")), (S("open-meer", 1), GR("-14%", "Nvidia, vrijdag 20 november", ROOD, 190))])),
 (T("open-meer", 2), fasen(F("ai-rood", (1.08, 1.0), 0.5), [(S("open-meer", 2), GR("-5,6%", "Nasdaq 100, de Amerikaanse techbeurs", ROOD, 170))])),
 (T("open-meer", 2.55), fasen(F("beurs-a", (1.0, 1.08), 0.45), [(S("open-meer", 2.55), GR("-2,4%", "AEX, de beurs van Amsterdam", ROOD, 170))])),
 (T("open-vraag"), fasen(F("ai-bubbel", (1.0, 1.08), 0.55), [(S("open-vraag"), GR("Wat is er aan de hand?", None, WIT, 100)), (S("open-vraag", 1), GR("BARST DE AI-BUBBEL?", None, ORANJE, 120)),
                                                          (S("open-vraag", 2), ON("En wat betekent het voor ASML, en voor jouw geld?"))])),
 (T("open-antwoord"), fasen(F("ai-twijfel", (1.0, 1.08), 0.5), [(S("open-antwoord"), ON("Beleggers twijfelen: levert AI genoeg op?"))])),
 (T("open-antwoord", 1), fasen(F("sec", (1.0, 1.08), 0.5, pan=(0.5, 0.4, 0.5, 0.5)), [(S("open-antwoord", 1), ON("Onderzoek naar de boekhouding van Nvidia"))])),
 (T("open-antwoord", 2), fasen(F("asml-hq", (1.08, 1.0), 0.55, pan=(0.4, 0.4, 0.5, 0.45)), [(S("open-antwoord", 3), LT("ASML, VELDHOVEN", "Zonder deze machines geen nieuwste chips"))])),
 (T("open-antwoord", 4), lijst("ai-kalender", "In deze video", [(S("open-antwoord", 4), "Wat er precies gebeurde"), (S("open-antwoord", 4.35), "Waarom juist ASML"),
                                                              (S("open-antwoord", 4.7), "Moet je je zorgen maken?")])),
 # --- h1: de week ---
 (T("h1-week"), fasen(F("ai-kalender", (1.0, 1.08), 0.5), [(S("h1-week"), ON("Een paar dagen terug"))])),
 (T("h1-cijfers"), fasen(F("nvidia-hq", (1.0, 1.08), 0.5), [(S("h1-cijfers"), ST("DINSDAG 17 NOVEMBER")), (S("h1-cijfers", 1), ON("De kwartaalcijfers van Nvidia: uitstekend"))])),
 (T("h1-cijfers", 2), balken([("Q3 vorig jaar", 57.0), ("Q3 dit jaar", 115.8)], "NVIDIA: OMZET IN DRIE MAANDEN", "Miljard dollar", "Bron: Nvidia",
                             MLD, [S("h1-cijfers", 2), S("h1-cijfers", 2.4)], kleur=GROEN)),
 (T("h1-cijfers", 4), koersgrafiek("nvda", "2026-10-01", "2026-11-20", "NVIDIA", "Slotkoers in dollar, 1 oktober t/m 20 november 2026", YB, teken=0.85, eenheid="$", eind_label=False)),
 (T("h1-huang"), fasen(F("jensen", (1.0, 1.06), 0.6, pan=(0.48, 0.42, 0.5, 0.4)), [(S("h1-huang", 1), LT("JENSEN HUANG", "33 jaar topman van Nvidia, opgestapt op 12 november"))])),
 (T("h1-sec"), fasen(F("sec", (1.0, 1.08), 0.5, pan=(0.5, 0.35, 0.5, 0.45)), [(S("h1-sec"), ST("VRIJDAG")), (S("h1-sec", 1), LT("SEC", "De Amerikaanse beurswaakhond")),
                                                                            (S("h1-sec", 3), ON("Een onderzoek, nog geen beschuldiging")),
                                                                            (S("h1-sec", 4), GR("-14%", "Nvidia: de zevende daling op rij", ROOD, 180))])),
 (T("h1-rest"), fasen(F("broadcom", (1.0, 1.08), 0.5), [(S("h1-rest"), ON("Andere chipbedrijven gingen mee omlaag")), (S("h1-rest", 1), GR("-12%", "Broadcom", ROOD, 180))])),
 (T("h1-rest", 2), fasen(F("dario", (1.0, 1.06), 0.6), [(S("h1-rest", 2), LT("ANTHROPIC", "Het bedrijf achter chatbot Claude (topman Dario Amodei)")),
                                                       (S("h1-rest", 3), GR("$81 MLD", "opgehaald bij de beursgang, 19 november", WIT, 160)),
                                                       (S("h1-rest", 5), GR("$83 → $111", "uitgifteprijs → eerste koers", GROEN, 150)),
                                                       (S("h1-rest", 6), ON("Binnen twee dagen was een groot deel van de winst weg"))])),
 (T("h1-correctie"), koersgrafiek("sp500", "2025-12-01", "2026-11-20", "S&P 500", "De brede Amerikaanse beurs, slotkoers in punten", YB,
                                  labels=[("2026-11-20", 1700, 330, "-11,6%", ROOD)], teken=0.85, eenheid="", eind_label=False)),
 # --- h2: wat is ASML ---
 (T("h2-asml"), fasen(F("asml-tower", (1.0, 1.06), 0.5, pan=(0.5, 0.3, 0.5, 0.4)), [(S("h2-asml"), ON("Waarom raakt dit een bedrijf uit Brabant?"))])),
 (T("h2-begin"), fasen(F("ai-keet", (1.0, 1.08), 0.55), [(S("h2-begin"), EN(ST("1984"), LT("PHILIPS + ASM INTERNATIONAL", "Het begin van ASML"))), (S("h2-begin", 1), ON("Begonnen in houten keten bij Philips in Eindhoven"))])),
 (T("h2-machines"), fasen(F("ai-euv", (1.0, 1.08), 0.5), [(S("h2-machines"), ON("ASML maakt de machines waarmee chips worden gemaakt")), (S("h2-machines", 1), LT("EUV", "Extreem ultraviolet licht"))])),
 (T("h2-machines", 2), fasen(F("ai-wafer", (1.0, 1.08), 0.55), [(S("h2-machines", 2), ON("Duizenden keren dunner dan een haar")),
                                                              (S("h2-machines", 3), GR("± €200 MLN", "per EUV-machine, zo groot als een bus", ORANJE, 160))])),
 (T("h2-highna"), fasen(F("ai-euv", (1.08, 1.0), 0.45, pan=(0.6, 0.5, 0.4, 0.5)), [(S("h2-highna", 1), GR("± €350 MLN", "High-NA-machine (volgens berichten)", ORANJE, 160))])),
 (T("h2-uniek"), fasen(F("asml-hq", (1.0, 1.08), 0.5), [(S("h2-uniek"), GR("ENIGE TER WERELD", "die deze machines kan maken", ORANJE, 120))])),
 (T("h2-uniek", 1), fasen(F("tsmc", (1.0, 1.08), 0.5), [(S("h2-uniek", 1), LT("TSMC, TAIWAN", "Klant van ASML, net als Samsung en Intel")), (S("h2-uniek", 2), ON("Ook de chips van Nvidia worden met ASML-machines gemaakt"))])),
 (T("h2-uniek", 3), fasen(F("asml-tower", (1.08, 1.0), 0.5, pan=(0.5, 0.4, 0.5, 0.3)), [(S("h2-uniek", 3), ON("Tienduizenden medewerkers, vooral in Nederland"))])),
 (T("h2-uniek", 4), fasen(F("ai-vliegtuig", (1.0, 1.08), 0.55), [(S("h2-uniek", 4), ON("In Veldhoven gebouwd, in delen per vliegtuig naar de klant"))])),
 (T("h2-china"), fasen(F("ai-china", (1.0, 1.08), 0.55), [(S("h2-china"), ON("Politiek belangrijk")), (S("h2-china", 1), EN(ST("2019"), ON("Geen EUV-machines naar China"))),
                                                        (S("h2-china", 2), EN(ST("2023"), ON("Ook Nederlandse exportregels voor andere machines"))),
                                                        (S("h2-china", 3), ON("Midden in de techstrijd tussen Amerika en China"))])),
 # --- h3: de keten ---
 (T("h3-keten"), lijst("ai-keten", "De keten", [(S("h3-keten", 1), "AI-bedrijven kopen chips bij Nvidia"), (S("h3-keten", 2), "Nvidia laat ze maken bij TSMC"),
                                                (S("h3-keten", 3), "TSMC koopt machines bij ASML")])),
 (T("h3-twijfel"), fasen(F("ai-twijfel", (1.08, 1.0), 0.5), [(S("h3-twijfel"), ON("Zolang AI groeit: een gouden keten")), (S("h3-twijfel", 2), ON("Minder AI-geld → minder chipfabrieken")),
                                                          (S("h3-twijfel", 3), ON("Minder fabrieken → minder bestellingen in Veldhoven"))])),
 (T("h3-goed"), fasen(F("asml-hq", (1.08, 1.0), 0.5, pan=(0.6, 0.45, 0.45, 0.4)), [(S("h3-goed"), ON("Met ASML zelf gaat het juist heel goed")),
                                                                                (S("h3-goed", 1), GR("€11,7 MLD", "recordomzet, derde kwartaal 2026", GROEN, 160)),
                                                                                (S("h3-goed", 2), GR("€5,0 MLD", "nettowinst, derde kwartaal", GROEN, 160)),
                                                                                (S("h3-goed", 3), ON("Vraag groter dan wat ASML in 2027 en 2028 kan maken"))])),
 (T("h3-verwachting"), fasen(F("ai-zandloper", (1.0, 1.08), 0.55), [(S("h3-verwachting", 1), ON("Een koers gaat over de toekomst")),
                                                                   (S("h3-verwachting", 3), ON("En over die toekomst is nu twijfel"))])),
 (T("h3-eerder"), koersgrafiek("asml5j", "2024-01-02", "2026-11-20", "ASML (AMSTERDAM)", "Slotkoers in euro, januari 2024 t/m 20 november 2026", YB,
                               markers=[("2024-10-15", "Cijfers te vroeg online: -16%")], teken=0.85, eenheid="€", eind_label=False)),
 # --- h4: bubbel? ---
 (T("h4-bubbel"), fasen(F("ai-bubbel", (1.08, 1.0), 0.5), [(S("h4-bubbel"), GR("BARST DE AI-BUBBEL?", None, ORANJE, 120)), (S("h4-bubbel", 1), ON("Er zijn twee kanten"))])),
 (T("h4-voor"), fasen(F("ai-datacenter", (1.0, 1.08), 0.5), [(S("h4-voor"), ST("WEL EEN BUBBEL")), (S("h4-voor", 1), GR("$700+ MLD", "AI-uitgaven van de vier grootste techbedrijven, dit jaar", ORANJE, 150)),
                                                           (S("h4-voor", 2), ON("Wordt dat geld ooit terugverdiend?"))])),
 (T("h4-voor", 3), fasen(F("sec", (1.08, 1.0), 0.5), [(S("h4-voor", 3), ON("Twijfel over de boekhouding van Nvidia"))])),
 (T("h4-tegen"), fasen(F("nvidia-hq", (1.08, 1.0), 0.5), [(S("h4-tegen"), ST("GEEN BUBBEL", GROEN)), (S("h4-tegen", 1), GR("+103%", "omzet Nvidia in een jaar", GROEN, 180))])),
 (T("h4-tegen", 2), fasen(F("asml-hq", (1.0, 1.08), 0.5), [(S("h4-tegen", 2), ON("ASML: recordomzet, interesse in orders voor 2029 en 2030")),
                                                          (S("h4-tegen", 3), ON("Bij een echte bubbel verdienen bedrijven weinig"))])),
 (T("h4-eerlijk"), fasen(F("beurs-b", (1.0, 1.08), 0.5), [(S("h4-eerlijk"), GR("NIEMAND WEET HET ZEKER", None, WIT, 100)),
                                                        (S("h4-eerlijk", 1), ON("Een goed bedrijf is niet altijd een goedkoop aandeel"))])),
 # --- h5: jij ---
 (T("h5-jij"), fasen(F("beurs-a", (1.08, 1.0), 0.5), [(S("h5-jij"), GR("Wat betekent dit voor jou?", None, WIT, 100)), (S("h5-jij", 1), LT("AEX", "ASML is het grootste bedrijf"))])),
 (T("h5-jij", 2), fasen(F("ai-pensioen", (1.0, 1.08), 0.55), [(S("h5-jij", 2), ON("Vaak indirect: via pensioenfonds of indexfonds"))])),
 (T("h5-tijd"), fasen(F("ai-zandloper", (1.08, 1.0), 0.5), [(S("h5-tijd"), ON("Het hangt af van je tijd")), (S("h5-tijd", 1), ON("Geld volgende maand nodig: een daling voel je direct")),
                                                         (S("h5-tijd", 2), ON("Twintig jaar beleggen: kijk naar het bedrijf zelf")),
                                                         (S("h5-tijd", 3), ON("Spreiding: één aandeel bepaalt niet alles"))])),
 (T("h5-letop"), lijst("beurs-b", "Waar moet je op letten?", [(S("h5-letop", 1), "Het onderzoek naar Nvidia"), (S("h5-letop", 2), "De AI-uitgaven van grote techbedrijven"),
                                                            (S("h5-letop", 3), "27 januari: ASML over 2027")])),
 (T("h5-letop", 4), fasen(F("beurs-b", (1.0, 1.06), 0.35), [(S("h5-letop", 4), GR("GEEN BELEGGINGSADVIES", None, WIT, 90))])),
 # --- slot ---
 (T("slot"), fasen(F("asml-hq", (1.0, 1.1), 0.5), [(S("slot"), ON("ASML: onmisbaar voor de hele AI-wereld")), (S("slot", 2), ON("Vrijdag was een dag van twijfel"))])),
 (T("slot", 3), slot_fade("asml-tower", "Dip, of het begin van iets groters?")),
]
