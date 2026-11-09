import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import strategie  # noqa: E402
import sweep_cisd  # noqa: E402

T0 = 1767571200000          # ma 5 jan 2026 00:00 UTC
UUR = 3_600_000


def kaars(i, o, c, h=None, l=None):
    return {"tijd": T0 + i * UUR, "o": o, "c": c,
            "h": h if h is not None else max(o, c) + 0.1, "l": l if l is not None else min(o, c) - 0.1}


def scenario():
    """3 rustige dagen (99,5-100,5), dan: swing-top, sweep onder de dagbodem, breaker, terugtest, stijging."""
    k = []
    for i in range(72):                                   # dag 0, 1, 2
        o, c = (100.2, 99.8) if i % 2 else (99.8, 100.2)
        k.append(kaars(i, o, c, 100.5, 99.5))
    for i in range(72, 78):
        o, c = (100.2, 99.8) if i % 2 else (99.8, 100.2)
        k.append(kaars(i, o, c, 100.5, 99.5))
    k.append(kaars(78, 100.2, 100.5, 100.8, 100.1))       # swing-top 100,8; slot 100,5 = instap
    prijs = 100.5
    for c in [100.2, 99.9, 99.6, 99.4, 99.2, 99.1]:       # 79-84: daling, sweep onder 99,5
        k.append(kaars(len(k), prijs, c))
        prijs = c
    k.append(kaars(85, 99.1, 99.0, 99.2, 98.8))           # laagste punt 98,8 = stop
    k.append(kaars(86, 99.0, 99.8, 99.9, 98.95))
    k.append(kaars(87, 99.8, 101.2, 101.3, 99.7))         # breaker: sterk groen, slot boven 100,8
    k.append(kaars(88, 101.2, 100.9, 101.3, 100.7))
    k.append(kaars(89, 100.9, 100.7, 101.0, 100.4))       # terug naar 100,5: limiet gevuld
    prijs = 100.7
    for _ in range(12):                                   # stijging naar > 105,6 (TP3)
        k.append(kaars(len(k), prijs, prijs + 0.6))
        prijs += 0.6
    return k


def test_setup_gevonden():
    k = scenario()
    plannen = sweep_cisd.Motor(k, {}, "1h").alles()
    assert len(plannen) == 1
    pl = plannen[0]
    assert pl["index"] == 87 and not pl["markt"]
    assert pl["instap"] == 100.5 and pl["stop"] == 98.8
    assert abs(pl["tp1"] - 102.2) < 1e-9 and abs(pl["tp3"] - 105.6) < 1e-9


def test_signaal_op_laatste_candle():
    k = scenario()
    s = strategie.signaal(k[:88], {"soort": "sweep"})
    assert s and s["limiet"] and s["instap"] == 100.5 and s["stop"] == 98.8
    assert strategie.signaal(k[:87], {"soort": "sweep"}) is None
    assert strategie.signaal(k[:89], {"soort": "sweep"}) is None     # alleen op de setup-candle zelf


def test_backtest_tp3_na_break_even():
    trades = sweep_cisd.backtest(scenario(), {}, kosten_pct=0.0)
    assert len(trades) == 1
    t = trades[0]
    assert t["reden"] == "TP3" and t["gewonnen"] and abs(t["R"] - 3.0) < 1e-6
    met_kosten = sweep_cisd.backtest(scenario(), {}, kosten_pct=0.25)[0]["R"]
    assert abs(met_kosten - (3.0 - 100.5 * 0.005 / 1.7)) < 1e-3


def test_break_even_na_tp1():
    k = scenario()[:92]
    prijs = k[-1]["c"]
    k.append(kaars(92, prijs, 102.4, 102.5, prijs - 0.1))   # TP1 (102,2) geraakt
    k += [kaars(93 + j, 102.4 - j, 101.4 - j) for j in range(4)]   # terug onder de instap
    t = sweep_cisd.backtest(k, {}, kosten_pct=0.0)
    assert t and t[0]["reden"] == "BE" and t[0]["gewonnen"] and abs(t[0]["R"]) < 1e-9


def test_kleine_stop_overgeslagen():
    plannen = sweep_cisd.Motor(scenario(), {"min_risico_pct": 2.0}, "1h").alles()
    assert plannen == []


def test_week_begint_op_maandag():
    assert sweep_cisd.periode_sleutel(T0, "1w") != sweep_cisd.periode_sleutel(T0 - 1, "1w")
    assert sweep_cisd.periode_sleutel(T0, "1w") == sweep_cisd.periode_sleutel(T0 + 6 * 86_400_000, "1w")


def test_bot_limiet_vullen_en_break_even(tmp_path, monkeypatch):
    import json
    import time as _t

    import bitvavo_bot
    import risico
    from test_bitvavo import NepPapier

    monkeypatch.setattr(bitvavo_bot, "LOG", str(tmp_path / "log.jsonl"))
    monkeypatch.setattr(bitvavo_bot, "MAP", str(tmp_path))
    monkeypatch.setattr(risico, "NOODSTOP", str(tmp_path / "NOODSTOP"))
    # tijden naar nu verschuiven (hele dagen, zodat de dagindeling gelijk blijft)
    dag = 86_400_000
    verschuif = (int(_t.time() * 1000) // dag - 3) * dag - T0
    k = [{**c, "tijd": c["tijd"] + verschuif} for c in scenario()[:88]]
    api = NepPapier(k, str(tmp_path / "papier.json"))
    api.prijs_ = 101.2
    cfg = json.load(open(os.path.join(os.path.dirname(bitvavo_bot.__file__), "instellingen_bitvavo.json")))
    cfg["markten"] = ["BTC-EUR"]
    cfg["strategie"] = {"soort": "sweep", "sweep": {}}

    bitvavo_bot.ronde(api, cfg, {})
    p = bitvavo_bot.lees_posities(api)["BTC-EUR"]
    assert p["status"] == "wacht" and p["limiet"] == 100.5 and api.st["EUR"] == 1000

    laatste = {"BTC-EUR": k[-1]["tijd"]}
    api.prijs_ = 100.3                                    # koers onder de limiet -> kopen
    bitvavo_bot.ronde(api, cfg, laatste)
    p = bitvavo_bot.lees_posities(api)["BTC-EUR"]
    assert p["status"] == "open" and p["stop"] == 98.8 and p["stop_id"] in api.st["orders"]
    verlies_bij_stop = p["aantal"] * (p["instap"] - p["stop"])
    assert verlies_bij_stop <= 5.01                         # 0,5% van €1000

    api.prijs_ = 102.4                                    # TP1 (±102,2) geraakt
    bitvavo_bot.ronde(api, cfg, laatste)
    p = bitvavo_bot.lees_posities(api)["BTC-EUR"]
    assert p["be"] and p["stop"] == p["instap"]

    api.prijs_ = p["instap"] * 0.99                       # terug: uitgestopt op instap
    bitvavo_bot.ronde(api, cfg, laatste)
    assert bitvavo_bot.lees_posities(api) == {}
    assert 990 < api.st["EUR"] < 1000                      # alleen kosten verloren
    log = open(tmp_path / "log.jsonl").read()
    for woord in ["limiet geplaatst", "gekocht", "stop naar instap", "stop geraakt"]:
        assert woord in log


def test_bot_limiet_vervalt_als_tp1_eerst(tmp_path, monkeypatch):
    import json
    import time as _t

    import bitvavo_bot
    import risico
    from test_bitvavo import NepPapier

    monkeypatch.setattr(bitvavo_bot, "LOG", str(tmp_path / "log.jsonl"))
    monkeypatch.setattr(bitvavo_bot, "MAP", str(tmp_path))
    monkeypatch.setattr(risico, "NOODSTOP", str(tmp_path / "NOODSTOP"))
    dag = 86_400_000
    verschuif = (int(_t.time() * 1000) // dag - 3) * dag - T0
    k = [{**c, "tijd": c["tijd"] + verschuif} for c in scenario()[:88]]
    api = NepPapier(k, str(tmp_path / "papier.json"))
    api.prijs_ = 101.2
    cfg = json.load(open(os.path.join(os.path.dirname(bitvavo_bot.__file__), "instellingen_bitvavo.json")))
    cfg["markten"] = ["BTC-EUR"]
    cfg["strategie"] = {"soort": "sweep", "sweep": {}}
    bitvavo_bot.ronde(api, cfg, {})
    api.prijs_ = 102.5
    bitvavo_bot.ronde(api, cfg, {"BTC-EUR": k[-1]["tijd"]})
    assert bitvavo_bot.lees_posities(api) == {} and api.st["EUR"] == 1000
