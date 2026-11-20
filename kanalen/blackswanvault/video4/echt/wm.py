"""Wikimedia-hulp met nette User-Agent (eigenaar 19 nov: kanaallink mag mee) en respect voor rate limits."""
import json, time, urllib.request, urllib.parse, urllib.error
UA = {"User-Agent": "BlackSwanVault-research/1.0 (https://www.youtube.com/@blackswanvault)"}
def get(url, raw=False):
    for poging in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
            time.sleep(2)
            return r if raw else json.loads(r)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            w = int(e.headers.get("Retry-After") or 60); print(f"429, wacht {w} s", flush=True); time.sleep(min(w, 300))
    raise RuntimeError("blijft 429")
