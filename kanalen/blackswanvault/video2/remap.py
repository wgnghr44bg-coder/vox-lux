"""Na het invoegen van zinnen in script.txt: alle zinnummers in render3.py omzetten (op tekst gematcht).
Gebruik: python remap.py <oud-script> <oud-render3> (schrijft render3.py)"""
import re, sys
def zinnen(s):
    out = []
    for l in s.replace("{SLOT}", "SLOT-A\nSLOT-B").splitlines():
        l = l.strip()
        if l and not l.startswith(("#", "@")): out.append(l)
    return out
oud = zinnen(open(sys.argv[1], encoding="utf-8").read()); nieuw = zinnen(open("script.txt", encoding="utf-8").read())
pos = {z: i for i, z in enumerate(nieuw)}; M = {i: pos[z] for i, z in enumerate(oud)}
r = open(sys.argv[2], encoding="utf-8").read()
def m(n):
    n = int(n); return str(M.get(n, n))
pat = r'(?P<pre>ZR\(|na\(|sinds\(|mark_na=)(?P<n>\d+)|(?P<pre2>\()(?P<n2>\d+)(?=, (?:[A-Z"(]|lambda))|(?P<pre3>(?:GROEN|ROOD), )(?P<n3>\d+)(?=\))|(?P<lijst>\[\d+(?:, \d+)+\])'
f = lambda x: (x.group("pre") + m(x.group("n"))) if x.group("pre") else (x.group("pre2") + m(x.group("n2"))) if x.group("pre2") else (x.group("pre3") + m(x.group("n3"))) if x.group("pre3") else "[" + ", ".join(m(v) for v in x.group("lijst")[1:-1].split(", ")) + "]"
open("render3.py", "w", encoding="utf-8").write(re.sub(pat, f, r)); print(len(oud), "->", len(nieuw))
