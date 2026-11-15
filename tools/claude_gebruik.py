"""Claude-gebruik meten en uitrekenen wat er nog kan (eigenaar 15 nov 2026: "programma dat kan zien en monitoren hoeveel
Claude usage ik nog heb en kan uitrekenen wat ik er nog mee kan").

Wat de pc weet: elk bericht van Claude staat in ~/.claude*/projects/**/*.jsonl, met het aantal tokens (usage).
Wat de pc NIET weet: hoe hoog de limiet van het abonnement is. Die staat alleen bij Anthropic en is te zien met /usage
in Claude Code. Daarom stel je dit programma één keer af met wat /usage zegt (--ijk), en rekent het daarna zelf.

Gewicht per token (ongeveer de prijsverhouding, want limieten volgen het rekenwerk): gewone invoer 1, cache schrijven 1,25
(1 uur: 2), cache lezen 0,1, uitvoer 5. Dat heet hier 'eenheden'.

  python tools/claude_gebruik.py                       # overzicht per account: laatste 5 uur, laatste 7 dagen, per taak
  python tools/claude_gebruik.py --ijk account2 week 35   # /usage zegt: deze week 35% gebruikt (ook: 5uur 60)
  python tools/claude_gebruik.py --json                 # voor de website (docs/status)
"""
import datetime as dt, json, re, sys
from pathlib import Path

HOME = Path.home()
HIER = Path(__file__).resolve().parent
IJK = HOME / "claude-gebruik-ijk.json"            # alleen op de pc, niet in git
UTC = dt.timezone.utc

# Hoeveel eenheden een taak gemiddeld kost; bijgewerkt met metingen uit het logboek (15 nov 2026, hoofdsessie Opus):
# een heel script (± 85 blokken, schrijven + controles) en een kleine taak (vraag beantwoorden, iets aanpassen).
TAKEN = {"script (± 85 blokken)": None, "kleine taak / vraag": None}


def accounts():
    for d in sorted(HOME.glob(".claude*")):
        if d.is_dir() and (d / "projects").exists():
            yield d.name.replace(".claude-", "").replace(".claude", "hoofd") or "hoofd", d


def eenheden(u):
    cc = u.get("cache_creation") or {}
    w1h = cc.get("ephemeral_1h_input_tokens", 0) or 0
    w5m = cc.get("ephemeral_5m_input_tokens", 0) or 0
    rest_w = max(0, (u.get("cache_creation_input_tokens", 0) or 0) - w1h - w5m)
    return ((u.get("input_tokens", 0) or 0) + 1.25 * (w5m + rest_w) + 2 * w1h
            + 0.1 * (u.get("cache_read_input_tokens", 0) or 0) + 5 * (u.get("output_tokens", 0) or 0))


def berichten(d, sinds):
    """(tijd, eenheden, model) van elk antwoord van Claude sinds `sinds`; dubbele regels (zelfde id) één keer."""
    gezien = set()
    for f in (d / "projects").rglob("*.jsonl"):
        if dt.datetime.fromtimestamp(f.stat().st_mtime, UTC) < sinds:
            continue
        for regel in f.open(encoding="utf-8", errors="replace"):
            if '"usage"' not in regel:
                continue
            try:
                r = json.loads(regel)
            except ValueError:
                continue
            m = r.get("message") or {}
            u = m.get("usage")
            ts = r.get("timestamp")
            if not u or not ts:
                continue
            key = (m.get("id"), r.get("requestId"))
            if key in gezien:
                continue
            gezien.add(key)
            t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if t >= sinds:
                yield t, eenheden(u), m.get("model", "?")


def meet(d):
    nu = dt.datetime.now(UTC)
    rij = list(berichten(d, nu - dt.timedelta(days=7)))
    vijf = sum(e for t, e, _ in rij if t >= nu - dt.timedelta(hours=5))
    week = sum(e for t, e, _ in rij)
    per_dag = {}
    for t, e, _ in rij:
        k = t.astimezone().strftime("%a %d-%m")
        per_dag[k] = per_dag.get(k, 0) + e
    return {"5uur": vijf, "week": week, "per_dag": per_dag, "berichten": len(rij)}


def taak_kosten(d):
    """Meet wat een script kost uit het logboek: de tijd tussen twee opeenvolgende 'script ... geschreven/omgebouwd'
    regels van Claude op dezelfde dag, en het gebruik in die tijd. Geen metingen -> vaste schatting."""
    log = HIER.parent / "stories" / "ROUTINE-LOG.md"
    regels = []                                         # (tijd, is_script) van elke regel die Claude schreef
    if log.exists():
        for l in log.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) Claude", l)
            if m:
                regels.append((dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M").astimezone(),
                               bool(re.search(r"omgebouwd naar opbouw Sleepy|NIEUW script geschreven", l))))
    rij = sorted(berichten(d, dt.datetime.now(UTC) - dt.timedelta(days=7)))
    metingen = []
    for (a, _), (b, script) in zip(regels, regels[1:]):  # van de vorige Claude-regel tot de script-regel
        if script and dt.timedelta(minutes=5) < b - a < dt.timedelta(hours=4):
            metingen.append(sum(e for t, e, _ in rij if a < t <= b))
    metingen = [x for x in metingen if x > 0]
    script = sorted(metingen)[len(metingen) // 2] if metingen else None
    return {"script (± 85 blokken)": script, "kleine taak / vraag": (script / 25) if script else None,
            "metingen": len(metingen)}


def main():
    ijk = json.loads(IJK.read_text(encoding="utf-8")) if IJK.exists() else {}
    if "--ijk" in sys.argv:
        i = sys.argv.index("--ijk")
        acc, soort, pct = sys.argv[i + 1], sys.argv[i + 2], float(sys.argv[i + 3])
        d = dict(accounts())[acc]
        gebruikt = meet(d)["week" if soort == "week" else "5uur"]
        ijk.setdefault(acc, {})[soort] = {"limiet": gebruikt / max(pct, 0.5) * 100, "op": dt.datetime.now().isoformat(timespec="minutes"),
                                         "pct": pct}
        IJK.write_text(json.dumps(ijk, indent=1), encoding="utf-8")
        print(f"afgesteld: {acc} {soort} {pct}% = {gebruikt:,.0f} eenheden -> limiet ± {ijk[acc][soort]['limiet']:,.0f}")
        return
    uit = []
    for acc, d in accounts():
        g = meet(d)
        if not g["berichten"]:
            continue
        kost = taak_kosten(d)
        r = {"account": acc, "5uur": round(g["5uur"]), "week": round(g["week"]), "per_dag": {k: round(v) for k, v in g["per_dag"].items()},
             "script_kost": round(kost["script (± 85 blokken)"] or 0), "metingen": kost["metingen"]}
        for soort in ("5uur", "week"):
            lim = ijk.get(acc, {}).get(soort, {}).get("limiet")
            if lim:
                over = max(0, lim - g[soort])
                r[f"{soort}_pct"] = round(100 * g[soort] / lim)
                r[f"{soort}_scripts_over"] = round(over / kost["script (± 85 blokken)"], 1) if kost["script (± 85 blokken)"] else None
        uit.append(r)
    if "--json" in sys.argv:
        print(json.dumps({"bijgewerkt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "accounts": uit}, ensure_ascii=False))
        return
    for r in uit:
        print(f"## {r['account']}")
        print(f"  laatste 5 uur: {r['5uur']:,} eenheden" + (f"  = {r['5uur_pct']}% van de 5-uurslimiet" if '5uur_pct' in r else ""))
        print(f"  laatste 7 dagen: {r['week']:,} eenheden" + (f"  = {r['week_pct']}% van de weeklimiet" if 'week_pct' in r else ""))
        if r["script_kost"]:
            print(f"  een script kost ± {r['script_kost']:,} eenheden (gemeten over {r['metingen']} scripts)")
        for soort, naam in (("5uur", "in dit 5-uursblok"), ("week", "deze week")):
            if r.get(f"{soort}_scripts_over") is not None:
                print(f"  nog ± {r[f'{soort}_scripts_over']} scripts {naam}")
        if "week_pct" not in r:
            print(f"  (nog niet afgesteld: kijk in Claude met /usage en draai: python tools/claude_gebruik.py --ijk {r['account']} week <procent>)")
        print("  per dag: " + ", ".join(f"{k} {v:,}" for k, v in r["per_dag"].items()))


if __name__ == "__main__":
    main()
