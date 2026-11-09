# Onderzoek: TradingView Editors' Picks op Bitvavo

`kandidaten.py` bevat Python-versies (alleen long) van PMax, SuperTrend, Grover Llorens Activator,
Keltner Channel, Bjorgum Double Tap (dubbele bodem) en TASC One Percent A Week.

```powershell
python haal_koersen.py     # 2 jaar uur- en 4-uurskoersen BTC/ETH/SOL van Bitvavo
python vergelijk.py        # rendement jaar 1 en jaar 2 apart, met Bitvavo-kosten (0,25% / 0,15% limiet)
```

Uitkomst 9 nov 2026 (nov 2024 – nov 2026): geen enkele strategie maakte in beide jaren winst op de drie munten.
Een filter "alleen boven het 200-daags gemiddelde" beperkte de verliezen, maar gaf ook geen voordeel.

## Tweede ronde (alle Editors' Picks, nov 2026)
 / : Adaptive SuperSmoother (Ehlers), RedK MMTStop als Chandelier en Donchian,
Dual-Phase Reversal 9 (stop/doel zelf ingevuld) en Katsanos RSMK (ETH/SOL t.o.v. BTC).
Uitkomst: ook hier geen strategie die in beide jaren op alle drie de munten winst maakte.
