"""Seintje op de telefoon (ntfy) op ma/wo/vr 10:00: tijd voor de Market Doodle What If-video (eigenaar 23 nov).
Daarna opent de eigenaar een sessie: "maak de What If-video". Geen privégegevens in het bericht."""
import json
from pathlib import Path
import requests
topic = json.loads((Path.home() / ".swan-ntfy.json").read_text())["topic"]
requests.post(f"https://ntfy.sh/{topic}", data="Tijd voor de What If-video van vandaag (17:00 online). Open een sessie en zeg: maak de What If-video.".encode("utf-8"),
              headers={"Title": "Market Doodle".encode("utf-8"), "Tags": "pencil2"}, timeout=20)
print("seintje verstuurd")
