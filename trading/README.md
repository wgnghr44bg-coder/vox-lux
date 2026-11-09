# Trading bot voor Bitvavo (crypto)

Automatische handelsbot met dashboard voor Bitvavo. **Start altijd in de oefenstand** (echte koersen, nepgeld).
Geen garantie op winst: test eerst wekenlang in de oefenstand.

## Wat zit erin
| Bestand | Wat |
|---|---|
| `bitvavo_bot.py` | De bot: kijkt elke minuut, handelt BTC, ETH en SOL in euro's. |
| `bitvavo.py` | Koppeling met Bitvavo, plus de **oefenstand** (nepgeld €1000, geen sleutel nodig). |
| `strategie.py` | Trendvolger: EMA 20/50-kruising omhoog, alleen boven de EMA 200; stop 2×ATR, doel 4×ATR. |
| `risico.py` | Max 0,5% risico per trade, stopt na 2% dagverlies, max 3 posities, noodstop. |
| `backtest.py` | Test de strategie op oude koersen (kosten 0,25% per order meegerekend). |
| `dashboard.py` | Webpagina: saldo, open posities, logboek, noodstop, "alles verkopen". |
| `instellingen_bitvavo.json` | Markten en alle getallen (ook max 25% van je geld per trade). |

**Hoe het handelt**
- Alleen kopen en weer verkopen (bij Bitvavo kun je niet op een daling inzetten).
- Na elke aankoop zet de bot meteen een **stop-loss-order op Bitvavo zelf**: die werkt ook als je pc uit staat.
- Het koersdoel bewaakt de bot zelf; staat de pc uit, dan wordt er niet op het doel verkocht (de stop blijft wel staan).

## Stap 1: backtest en oefenstand (geen sleutel nodig)
```powershell
cd vox-lux\trading
pip install requests
python backtest.py BTC-EUR
python backtest.py ETH-EUR
.\start.ps1                      # bot + dashboard op http://localhost:8788
```
Het nepgeld staat in `data\papier_bitvavo.json` (verwijderen = opnieuw beginnen met €1000).

## Stap 2: echt geld (pas na weken goede resultaten)
1. Bitvavo → Instellingen → **API** → nieuwe sleutel. Vink **alleen "Handelen"** aan, **nooit "Opnemen"**.
   Zet eventueel een IP-beperking op het IP-adres van je pc.
2. Op de pc (PowerShell, eenmalig; daarna een nieuw venster openen):
   ```powershell
   setx BITVAVO_KEY "..."
   setx BITVAVO_SECRET "..."
   ```
   Deel deze sleutels nooit in een chat.
3. Zet eerst een klein bedrag op Bitvavo (bv. €100) en start: `.\start.ps1 -EchtGeld`.
   Het dashboard toont dan in rood **ECHT GELD**.

## Dashboard op je telefoon
`setx DASHBOARD_WACHTWOORD "iets-sterks"`, dan `python dashboard.py --host 0.0.0.0` (plus `--echt-geld` indien nodig)
en open `http://<ip-van-pc>:8788` op je telefoon (zelfde wifi).

## Veiligheid
- **Noodstop**: knop op het dashboard, of een leeg bestand `trading\NOODSTOP`. Stop-loss-orders blijven staan.
- **Alles verkopen**: knop op het dashboard (haalt de stop-orders weg en verkoopt de munten).
- Echt geld alleen met `--echt-geld` / `-EchtGeld`; zonder sleutels weigert de bot.
- Logboek: `trading\data\log_bitvavo.jsonl`.

## Tests
`python -m pytest -q tests` (werkt zonder internet).
