"""Dashboard in de browser: saldo, open trades, logboek, noodstop.

Oefenstand:                 python dashboard.py               -> http://localhost:8788
Echt geld:                  python dashboard.py --echt-geld
Ook op je telefoon (wifi):  set DASHBOARD_WACHTWOORD=...  en  python dashboard.py --host 0.0.0.0
                            -> http://<ip-van-pc>:8788  (gebruikersnaam mag alles zijn)
"""
import argparse
import base64
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import risico

MAP = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(MAP, "data", "log_bitvavo.jsonl")
WACHTWOORD = os.environ.get("DASHBOARD_WACHTWOORD", "")
INSTELLING = {"echt_geld": False}

PAGINA = """<!doctype html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Trading Bot</title>
<style>
:root{--bg:#f6f7f9;--kaart:#fff;--tekst:#1b1f24;--zacht:#6a737d;--groen:#1a7f37;--rood:#cf222e;--rand:#d8dee4}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--kaart:#161b22;--tekst:#e6edf3;--zacht:#8b949e;--groen:#3fb950;--rood:#f85149;--rand:#30363d}}
body{margin:0;background:var(--bg);color:var(--tekst);font:15px/1.4 system-ui,sans-serif}
main{max-width:900px;margin:auto;padding:16px}
.rij{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.kaart{background:var(--kaart);border:1px solid var(--rand);border-radius:10px;padding:14px;margin-bottom:12px}
.label{color:var(--zacht);font-size:13px}.groot{font-size:22px;font-weight:600;font-variant-numeric:tabular-nums}
.plus{color:var(--groen)}.min{color:var(--rood)}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}td,th{padding:6px 4px;border-bottom:1px solid var(--rand);text-align:left}
.log{font:12px/1.5 ui-monospace,monospace;max-height:340px;overflow:auto;white-space:pre-wrap}
button{font:inherit;padding:10px 14px;border-radius:8px;border:1px solid var(--rand);background:var(--kaart);color:var(--tekst);cursor:pointer}
button.gevaar{background:var(--rood);color:#fff;border:0}.knoppen{display:flex;gap:8px;flex-wrap:wrap}
.status{display:inline-block;padding:2px 10px;border-radius:99px;font-size:13px;font-weight:600}
</style></head><body><main>
<h1 style="font-size:20px">Trading Bot <span id="omg" class="status"></span></h1>
<div class="kaart rij">
 <div><div class="label">Saldo</div><div class="groot" id="saldo">–</div></div>
 <div><div class="label">Waarde (NAV)</div><div class="groot" id="nav">–</div></div>
 <div><div class="label">Open winst/verlies</div><div class="groot" id="upl">–</div></div>
 <div><div class="label">Bot</div><div class="groot" id="bot">–</div></div>
</div>
<div class="kaart"><div class="knoppen">
 <button id="stopknop" onclick="noodstop()">Noodstop</button>
 <button class="gevaar" onclick="sluitAlles()">Alles verkopen</button>
</div><p class="label" id="fout"></p></div>
<div class="kaart"><b>Open posities</b><table><thead><tr><th>Markt</th><th>Aantal</th><th>Instap</th><th>W/V</th></tr></thead><tbody id="trades"></tbody></table></div>
<div class="kaart"><b>Logboek</b><div class="log" id="log"></div></div>
</main><script>
let stopAan=false;
const geld=(v,c)=>v==null?'–':Number(v).toLocaleString('nl-NL',{style:'currency',currency:c||'EUR'});
async function laad(){
 const r=await fetch('api/status');const d=await r.json();
 document.getElementById('fout').textContent=d.fout||'';
 const a=d.account||{};const c=a.currency;
 saldo.textContent=geld(a.balance,c);nav.textContent=geld(a.NAV,c);
 upl.textContent=geld(a.unrealizedPL,c);upl.className='groot '+(+a.unrealizedPL>=0?'plus':'min');
 omg.textContent=(d.broker||'')+' '+(d.omgeving==='live'?'ECHT GELD':'oefengeld');
 omg.style.background=d.omgeving==='live'?'var(--rood)':'var(--groen)';omg.style.color='#fff';
 stopAan=d.noodstop;bot.textContent=stopAan?'gestopt':'actief';bot.className='groot '+(stopAan?'min':'plus');
 stopknop.textContent=stopAan?'Bot weer aanzetten':'Noodstop';
 trades.innerHTML=(d.trades||[]).map(t=>`<tr><td>${t.instrument}</td><td>${t.currentUnits}</td><td>${t.price}</td><td class="${+t.unrealizedPL>=0?'plus':'min'}">${geld(t.unrealizedPL,c)}</td></tr>`).join('')||'<tr><td colspan=4 class=label>geen</td></tr>';
 log.textContent=(d.log||[]).map(l=>`${l.tijd}  ${l.soort}  ${JSON.stringify(Object.fromEntries(Object.entries(l).filter(([k])=>k!=='tijd'&&k!=='soort')))}`).reverse().join('\\n');
}
async function post(p,b){const r=await fetch(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b||{})});const d=await r.json();if(d.fout)alert(d.fout);laad();}
function noodstop(){post('api/noodstop',{aan:!stopAan});}
function sluitAlles(){if(confirm('Alle munten nu verkopen én de bot stoppen?'))post('api/sluit-alles');}
laad();setInterval(laad,15000);
</script></body></html>"""


def lees_log(n=60):
    if not os.path.exists(LOG):
        return []
    with open(LOG) as f:
        regels = f.readlines()[-n:]
    uit = []
    for r in regels:
        try:
            uit.append(json.loads(r))
        except ValueError:
            pass
    return uit


def bitvavo_api():
    import bitvavo_bot
    from bitvavo import BitvavoFout
    try:
        return bitvavo_bot.maak_api(INSTELLING["echt_geld"], bitvavo_bot.laad_instellingen()), None
    except BitvavoFout as e:
        return None, str(e)


def bitvavo_status(d):
    """Saldo, waarde en open posities voor de pagina."""
    import bitvavo_bot
    api, fout = bitvavo_api()
    d["omgeving"] = "live" if INSTELLING["echt_geld"] else "practice"
    if not api:
        d["fout"] = fout
        return
    try:
        cfg = bitvavo_bot.laad_instellingen()
        pos = bitvavo_bot.lees_posities(api)
        nav, saldi, koersen = bitvavo_bot.waarde(api, cfg["markten"], pos)
        trades, upl = [], 0.0
        for m, p in pos.items():
            w = (koersen[m]["bid"] - p["instap"]) * p["aantal"]
            upl += w
            trades.append({"instrument": m, "currentUnits": f"{p['aantal']:.6g}",
                           "price": f"{p['instap']:.6g}", "unrealizedPL": round(w, 2)})
        d["account"] = {"currency": "EUR", "balance": round(sum(saldi.get("EUR", (0, 0))), 2),
                        "NAV": round(nav, 2), "unrealizedPL": round(upl, 2)}
        d["trades"] = trades
    except (OSError, ValueError, KeyError, RuntimeError) as e:
        d["fout"] = str(e)[:300]


def bitvavo_sluit_alles():
    import bitvavo_bot
    from bitvavo import hoeveelheid_decimalen
    api, fout = bitvavo_api()
    if not api:
        return {"fout": fout}
    pos = bitvavo_bot.lees_posities(api)
    gesloten, fouten = [], []
    for m, p in list(pos.items()):
        try:
            api.annuleer(m, p["stop_id"])
            vrij = api.saldi().get(m.split("-")[0], (0, 0))[0]
            api.verkoop_markt(m, vrij, hoeveelheid_decimalen(api.market_info(m)))
            gesloten.append(m)
            del pos[m]
        except (OSError, ValueError, KeyError, RuntimeError) as e:
            fouten.append(f"{m}: {e}"[:200])
    bitvavo_bot.bewaar_posities(api, pos)
    bitvavo_bot.log("alles gesloten via dashboard", markten=gesloten)
    return {"gesloten": gesloten, "fout": "; ".join(fouten) or None}


class Handler(BaseHTTPRequestHandler):
    def _toegestaan(self):
        if not WACHTWOORD:
            return True
        kop = self.headers.get("Authorization", "")
        if kop.startswith("Basic "):
            try:
                _, _, ww = base64.b64decode(kop[6:]).decode().partition(":")
                if hmac.compare_digest(ww, WACHTWOORD):
                    return True
            except (ValueError, UnicodeDecodeError):
                pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="trading"')
        self.end_headers()
        return False

    def _stuur(self, code, inhoud, soort="application/json"):
        data = inhoud if isinstance(inhoud, bytes) else json.dumps(inhoud).encode()
        self.send_response(code)
        self.send_header("Content-Type", soort)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._toegestaan():
            return
        if self.path in ("/", "/index.html"):
            return self._stuur(200, PAGINA.encode(), "text/html; charset=utf-8")
        if self.path == "/api/status":
            d = {"noodstop": risico.noodstop_aan(), "log": lees_log(), "broker": "Bitvavo"}
            bitvavo_status(d)
            return self._stuur(200, d)
            api, fout = api_of_fout()
            if api:
                d["omgeving"] = api.omgeving
                try:
                    d["account"] = api.samenvatting()
                    d["trades"] = api.open_trades()
                except (OandaFout, OSError) as e:
                    d["fout"] = str(e)[:300]
            else:
                d["fout"] = fout
            return self._stuur(200, d)
        self._stuur(404, {"fout": "niet gevonden"})

    def do_POST(self):
        if not self._toegestaan():
            return
        lengte = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(lengte) or b"{}")
        except ValueError:
            body = {}
        if self.path == "/api/noodstop":
            risico.zet_noodstop(bool(body.get("aan")))
            return self._stuur(200, {"noodstop": risico.noodstop_aan()})
        if self.path == "/api/sluit-alles":
            risico.zet_noodstop(True)
            return self._stuur(200, bitvavo_sluit_alles())
        self._stuur(404, {"fout": "niet gevonden"})

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--poort", type=int, default=8788)
    ap.add_argument("--echt-geld", action="store_true", help="echte Bitvavo-rekening tonen")
    a = ap.parse_args()
    INSTELLING.update(echt_geld=a.echt_geld)
    if a.host not in ("127.0.0.1", "localhost") and not WACHTWOORD:
        raise SystemExit("Zet eerst DASHBOARD_WACHTWOORD als het dashboard buiten deze pc bereikbaar is.")
    print(f"Dashboard: http://{'localhost' if a.host == '127.0.0.1' else a.host}:{a.poort}")
    ThreadingHTTPServer((a.host, a.poort), Handler).serve_forever()


if __name__ == "__main__":
    main()
