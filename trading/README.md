# Trading bot voor OANDA (forex) en Bitvavo (crypto)

Automatische handelsbot met dashboard. **Standaard op oefengeld.**
OANDA staat hieronder; Bitvavo staat onderaan.
Geen garantie op winst: test eerst wekenlang op oefengeld.

## Wat zit erin
| Bestand | Wat |
|---|---|
| `bot.py` | De bot: kijkt elke minuut naar nieuwe uur-candles en plaatst orders, altijd met stop-loss en take-profit. |
| `strategie.py` | Trendvolger: EMA 20/50-kruising, alleen in de richting van de EMA 200; stop 1,5×ATR, doel 3×ATR. |
| `risico.py` | Max 0,5% risico per trade, stopt na 2% dagverlies, max 3 trades tegelijk, noodstop. |
| `backtest.py` | Test de strategie op oude koersen. |
| `dashboard.py` | Webpagina: saldo, open trades, logboek, noodstop-knop, "alles sluiten". |
| `instellingen.json` | Welke paren, en alle getallen hierboven. |

## Stap 1: oefenaccount en sleutel
1. Maak een gratis **demo-account** op oanda.com.
2. Log in → *Mijn account* → *API-toegang beheren* → **token aanmaken**.
3. Noteer het rekeningnummer (bv. `101-004-1234567-001`).
4. Zet op de pc (PowerShell, eenmalig):
   ```powershell
   setx OANDA_TOKEN "jouw-token"
   setx OANDA_ACCOUNT "101-004-1234567-001"
   setx OANDA_OMGEVING "practice"
   ```
   Open daarna een nieuw PowerShell-venster. Deel de token nooit in een chat.

## Stap 2: installeren en testen
```powershell
cd vox-lux\trading
pip install requests
python backtest.py EUR_USD --spread 0.00012
python bot.py --een-keer
```

## Stap 3: draaien
```powershell
.\start.ps1           # start bot + dashboard, elk in een eigen venster
```
Dashboard: http://localhost:8787. Op je telefoon (zelfde wifi):
`setx DASHBOARD_WACHTWOORD "iets-sterks"`, dan `python dashboard.py --host 0.0.0.0`
en open `http://<ip-van-pc>:8787`.

## Veiligheid
- **Noodstop**: knop op het dashboard, of maak een leeg bestand `trading\NOODSTOP`. Bestaande trades houden hun stop-loss.
- **Echt geld** kan alleen met `OANDA_OMGEVING=live` **én** `python bot.py --echt-geld`.
- Logboek: `trading\data\log.jsonl`.

## Tests
`python -m pytest -q tests` (werkt zonder internet).

---

# Bitvavo (crypto)

| Bestand | Wat |
|---|---|
| `bitvavo.py` | Koppeling met Bitvavo, plus een **oefenstand** (echte koersen, nepgeld €1000). |
| `bitvavo_bot.py` | De bot voor BTC, ETH en SOL in euro's. |
| `instellingen_bitvavo.json` | Markten en getallen (stop 2×ATR, doel 4×ATR, max 25% van je geld per trade). |

**Verschillen met OANDA**
- Bitvavo heeft geen oefenaccount, daarom een eigen oefenstand. **Daarvoor is geen sleutel nodig.**
- Alleen kopen en weer verkopen (geen "short").
- Na elke aankoop zet de bot meteen een **stop-loss-order op Bitvavo zelf**, dus die werkt ook als je pc uit staat.
  Het koersdoel bewaakt de bot zelf: staat de pc uit, dan wordt er niet op het doel verkocht (de stop blijft wel).
- Kosten ±0,25% per aankoop en per verkoop; die rekent de backtest mee.

## Stap 1: backtest en oefenstand (geen sleutel nodig)
```powershell
cd vox-lux\trading
python backtest.py BTC-EUR --broker bitvavo
python backtest.py ETH-EUR --broker bitvavo
.\start.ps1 -Broker bitvavo                 # bot + dashboard op http://localhost:8788
```
Het nepgeld staat in `data\papier_bitvavo.json` (verwijderen = opnieuw beginnen met €1000).

## Stap 2: echt geld (pas na weken goede resultaten)
1. Bitvavo → Instellingen → **API** → nieuwe sleutel. Vink **alleen "Handelen"** aan, **nooit "Opnemen"**.
   Zet eventueel een IP-beperking op het IP-adres van je pc.
2. Op de pc (PowerShell):
   ```powershell
   setx BITVAVO_KEY "..."
   setx BITVAVO_SECRET "..."
   ```
3. Zet eerst een klein bedrag op Bitvavo (bv. €100) en start: `.\start.ps1 -Broker bitvavo -EchtGeld`.

Noodstop en "Alle trades sluiten" werken op het dashboard ook voor Bitvavo
(sluiten = stop-orders weghalen en de munten verkopen).
