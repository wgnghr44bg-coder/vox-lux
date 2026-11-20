# Bronnen video 5: storingen in Amerika (12-17 nov 2026), gelezen 20 nov

Tijdlijn (CNBC 17 nov "Widespread outages hit banks, air travel, the NSA and Apple"; AP via KSAT 18/19 nov "Tech outages are piling up, and AI is raising the stakes"):
- do 12 nov: Microsoft 365 (Outlook, Teams, Copilot) wereldwijd plat, over twee werkdagen (ABC 16 nov). CNBC: "millions of users lost access to email".
- vr 13 nov: FAA nationwide ground stop. AP: "the longest nationwide ground stop in 25 years", "more than four hours". Wikipedia: 20:54-01:19 UTC (15:54 Eastern), bijna 8.000 annuleringen en 10.000+ vertragingen die dag; za/zo nog duizenden. Eurocontrol schortte vluchten naar de VS op.
- ma 16 nov: JPMorgan Chase: "software bug in on-premise hardware systems", vertraagde transacties. United: systeemstoring, vertrekkende vluchten kort vertraagd.
- di 17 nov: NSA: intern netwerk voor geheime communicatie offline, "scheduled routine maintenance". Apple: Apple Music, App Store, AppleCare verstoord na "an internal update". Marriott: inlogproblemen.
- CNBC: vier grote storingen op vier werkdagen op rij.

Microsoft (ABC 16 nov, Charles Lamanna, EVP Copilot, Agents and Platform):
- "A latent defect caused servers to become overwhelmed and unresponsive under certain load conditions." Fout in een fix voor de netwerkgateways, uit juli; plus "a surge in load" en minder servercapaciteit. Verzoeken stapelden op tot servers stopten; herstel duurde lang omdat terugkerende servers meteen weer overspoeld werden.
- "We are deeply sorry for the impact to all our customers". Geen hack.

FAA (Wikipedia "2026 FAA nationwide ground stop"; CNBC; CNN 17 nov; PBS; GV Wire 19 nov):
- Werk van aannemer L3Harris (eigenaar FTI-netwerk) in het zuiden van Arkansas: oude koperverbindingen naar glasvezel (± 70% klaar).
- Duffy: nieuw geplaatste router (Juniper) stuurde "a thousand connection attempts every four to five seconds" over het netwerk; radar en communicatie bij 17 luchtverkeerscentra verstoord.
- HPE (eigenaar Juniper): apparatuur werkte zoals ingesteld. FAA stopte verdere installaties. Oorzaak 20 nov officieel nog niet bekend (Bedford: "deze week").
- GAO (twee maanden eerder): FAA hield niet goed toezicht op aannemers. Duffy vraagt $50 mld extra.

Was het een aanval? (CNBC 17 nov; AP):
- DNI Jay Clayton (CNBC Closing Bell, di): "This is not cyberattack, and this is not a coordinated effort by a nation state."
- Jeffries: "too premature" om kwaadwillig handelen te concluderen; wil briefing.
- Warner: "based on what we know today, there is good reason to believe these disruptions are the unintended consequences of efforts to make our systems safer."
- Clayton tegen Fox News: patchen na de PHP-waarschuwing liet systemen niet goed terugkomen: "That is what has happened at the NSA today." (NSA zelf: routineonderhoud.)

AI en lekken:
- The Register 13 nov: VulnCheck telde 100.222 CVE's in 2026, meer dan het dubbele van 2025; Bressers: AI-gedreven zoeken drijft de stijging.
- Google Threat Intelligence: per maand van 5.045 (jan) naar 10.740 (aug).
- Microsoft juni-Patch Tuesday: record 206 CVE's (Dark Reading).
- PHP2Shell (okt): twee kritieke PHP-lekken, gevonden door Calif met hulp van een OpenAI-model; CISA: updaten of offline halen; hackers misbruiken ze (TechCrunch 27 okt). Censys: 1,5 mln van 2,6 mln servers nog niet bijgewerkt.
- Hegel (SentinelOne): "We're in the weird teenage phase of technology". Cappos (NYU): "AI is absolutely making it way easier for attackers to go and launch cyber attacks."
- Rajarajan (City St George's): "As AI adoption accelerates, we are likely to witness more incidents of this nature."

Hamsteren (CNBC 18 nov, Mizuho, David Bellinger):
- 21 van de 26 dure aggregaten op Costco.com uitverkocht (zo-avond). Mizuho: vergelijkbare omzet VS kan in november 10%+ groeien. Ook Sam's Club, Home Depot, Lowe's. Costco cijfers 10 dec. TikTok-oproepen om in te slaan.
