# Trading bot voor Bitvavo (crypto)

## Aanbevolen: trendfilter-bot (`trend_bot.py`)
Na het testen van 14 handelsstrategieën (zie `onderzoek/`) bleek geen enkele betrouwbaar winstgevend
op Bitvavo. Deze eenvoudige aanpak beperkte wel de grote dalingen:

- Jij stort elke week een bedrag op Bitvavo (iDEAL).
- Eén keer per dag kijkt de bot per munt: staat het slot boven het **200-daags gemiddelde**?
  Ja → vrij geld gaat naar die munt, tot zijn deel (standaard **70% BTC, 30% ETH**).
  Nee → die munt wordt verkocht en het geld blijft in euro's.
- **Limietorders** (0,15% kosten); niet gevuld binnen 15 minuten → marktorder (0,25%).
- Geen stop-loss en geen doelen. Ongeveer 6-11 wissels per jaar per munt.

Backtest op echte Bitvavo-dagkoersen (dec 2021 – nov 2026, `python trend_bot.py --backtest`):
BTC vasthouden +52% (grootste daling 66%) tegen trendfilter +131% (grootste daling 35%);
ETH vasthouden −48% (daling 76%) tegen trendfilter +23% (daling 43%). Verleden is geen garantie.

```powershell
python trend_bot.py --backtest     # test op echte koersen
.\start.ps1                        # oefenstand (nepgeld €1000 + €100 per maandag) + dashboard
.\start.ps1 -EchtGeld              # echt geld (eerst BITVAVO_KEY en BITVAVO_SECRET zetten, zie onder)
```
Instellingen in `instellingen_trend.json` (verdeling, aantal dagen, reserve in euro's).

---

## Handelsbot (`bitvavo_bot.py`): alleen voor proeven

Automatische handelsbot met dashboard voor Bitvavo. **Start altijd in de oefenstand** (echte koersen, nepgeld).
Geen garantie op winst: test eerst wekenlang in de oefenstand.

## Wat zit erin
| Bestand | Wat |
|---|---|
| `bitvavo_bot.py` | De bot: kijkt elke minuut, handelt BTC, ETH en SOL in euro's. |
| `bitvavo.py` | Koppeling met Bitvavo, plus de **oefenstand** (nepgeld €1000, geen sleutel nodig). |
| `sweep_cisd.py` | Strategie **HTF sweep CISD** (standaard), naar het TradingView-script van WillyAlgoTrader. |
| `smc.py` | Strategie **smart money**: toppen/bodems, BOS en CHoCH, kopen in de vraagzone, boven SMA 200. |
| `strategie.py` | Strategie **trend**: EMA 20/50-kruising omhoog boven de EMA 200; stop 2×ATR, doel 4×ATR. |
| `risico.py` | Max 0,5% risico per trade, stopt na 2% dagverlies, max 3 posities, noodstop. |
| `backtest.py` | Test de strategie op oude koersen (kosten 0,25% per order meegerekend). |
| `dashboard.py` | Webpagina: saldo, open posities, logboek, noodstop, "alles verkopen". |
| `instellingen_bitvavo.json` | Markten en alle getallen (ook max 25% van je geld per trade). |

**Hoe het handelt**
- Alleen kopen en weer verkopen (bij Bitvavo kun je niet op een daling inzetten).
- Na elke aankoop zet de bot meteen een **stop-loss-order op Bitvavo zelf**: die werkt ook als je pc uit staat.
- Het koersdoel bewaakt de bot zelf; staat de pc uit, dan wordt er niet op het doel verkocht (de stop blijft wel staan).

## Strategie kiezen
In `instellingen_bitvavo.json` bij `"strategie"`: `"soort": "sweep"`, `"smc"` (smart money) of `"trend"`.

**HTF sweep CISD** (standaard) werkt zo, met de standaardinstellingen van het TradingView-script:
1. Grote tijdschaal automatisch: bij uur-candles is dat de **dag** (15m → 4h, 4h → week).
2. **Sweep**: de koers zakt onder de bodem van de vorige dag, of onder een nog niet geraakte dagbodem
   van de laatste 10 dagen.
3. **Breaker**: daarna sluit een sterke groene candle (lijf ≥ 0,5×ATR) boven de laatste swing-top van vóór
   het laagste punt.
4. **Instap** met een limiet op het slot van die swing-top-candle (de bot koopt zelf als de koers daar komt;
   staat de koers er al onder, dan direct). Vervalt na 60 candles, of als TP1 eerder geraakt wordt.
5. **Stop-loss** op het laagste punt van de sweep (op Bitvavo zelf). **TP1 = 1R** → stop naar de instap
   (break-even). **TP3 = 3R** → alles verkopen. Stop-afstand tussen 0,25 en 3×ATR, en minstens 1%
   (`min_risico_pct`), anders eten de kosten de winst op.
6. Niet overgenomen: andere instapmodellen (OB/FVG/IFVG/Unicorn), tijd- en nieuwsfilters, SMT, short.

Let op: de "Win Rate" op het TradingView-dashboard telt een trade als gewonnen zodra TP1 is geraakt,
ook als hij daarna op break-even (0R, en bij Bitvavo dus een klein verlies door kosten) sluit.
Kijk daarom naar **totaal_R** in de backtest, niet alleen naar het winstpercentage.

**Smart money** werkt zo:
1. De bot zoekt toppen en bodems (5 candles links en rechts).
2. Slot boven de laatste top = breuk omhoog: **CHoCH** als de trend omlaag was (wending), anders **BOS**.
3. Bij die breuk onthoudt hij de **vraagzone**: de candle met de laagste bodem vóór de breuk.
4. Hij **koopt** als de trend omhoog is, de koers boven de **SMA 200** staat en de koers terugzakt in de zone
   maar erboven sluit. Elke zone één keer. (`"sma_kruis": true` = ook SMA 20 boven SMA 50 eisen.)
5. Stop-loss net onder de zone, doel 2,5× het risico. Ligt de stop minder dan 1,5% weg, dan koopt hij niet:
   anders eten de kosten (2× 0,25%) de winst op.

Gebruik geen 1-minuut-candles: de bewegingen zijn dan kleiner dan de kosten. `"interval": "1h"` of `"4h"`.

## Stap 1: backtest en oefenstand (geen sleutel nodig)
```powershell
cd vox-lux\trading
pip install requests
python backtest.py BTC-EUR --vergelijk      # smart money en trend naast elkaar
python backtest.py ETH-EUR --vergelijk
.\start.ps1 -Bot handel           # handelsbot + dashboard op http://localhost:8788
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
3. Zet eerst een klein bedrag op Bitvavo (bv. €100) en start: `.\start.ps1 -Bot handel -EchtGeld`.
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
