"""Los seintje op de telefoon via ntfy (zelfde kanaal als de andere seintjes; kanaalnaam alleen op de pc in ~/.swan-ntfy.json).
Eigenaar 24 nov 2026: "geef seintje via ntfy als video klaar is".

  python tools/seintje.py "Titel" "Tekst" [tag]
"""
import json, sys
from pathlib import Path
import requests

def seintje(titel, tekst, tag="clapper"):
    topic = json.loads((Path.home() / ".swan-ntfy.json").read_text())["topic"]
    r = requests.post(f"https://ntfy.sh/{topic}", data=tekst.encode("utf-8"),
                      headers={"Title": titel.encode("utf-8"), "Tags": tag}, timeout=20)
    return r.status_code

if __name__ == "__main__":
    print(seintje(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "clapper"))
