"""Lokaal taalmodel via Ollama (gratis, op de pc, zonder Claude). Eigenaar 8 nov 2026: "iets bouwen dat net zo goed is
maar dan zonder Claude"."""
import json, re, time

import requests

MODEL = "qwen3:14b"
URL = "http://127.0.0.1:11434/api/chat"


def vraag(prompt, systeem="", temp=0.7, max_tokens=1800, ctx=12288):
    """Eén vraag aan het model; geeft de tekst terug (zonder <think>-deel)."""
    berichten = ([{"role": "system", "content": systeem}] if systeem else []) + [{"role": "user", "content": prompt}]
    for poging in range(3):
        try:
            r = requests.post(URL, json={"model": MODEL, "messages": berichten, "stream": False, "think": False,
                                         "options": {"temperature": temp, "num_predict": max_tokens, "num_ctx": ctx,
                                                     "repeat_penalty": 1.08, "top_p": 0.9}}, timeout=1800)
            r.raise_for_status()
            t = r.json()["message"]["content"]
            return re.sub(r"<think>.*?</think>", "", t, flags=re.S).strip()
        except Exception as e:                             # Ollama nog aan het opstarten of even bezet
            print(f"  model-fout ({e}), opnieuw", flush=True)
            time.sleep(20 * (poging + 1))
    raise RuntimeError("Ollama antwoordt niet")


def json_vraag(prompt, systeem="", temp=0.4, max_tokens=2500, ctx=12288):
    """Vraag om JSON; probeert tot het geldig is."""
    for _ in range(4):
        t = vraag(prompt + "\n\nAnswer with valid JSON only, no other text.", systeem, temp, max_tokens, ctx)
        t = re.sub(r"^```(json)?|```$", "", t.strip(), flags=re.M).strip()
        m = re.search(r"[\[{].*[\]}]", t, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        temp = min(temp + 0.1, 0.9)
    raise ValueError("geen geldige JSON van het model")
