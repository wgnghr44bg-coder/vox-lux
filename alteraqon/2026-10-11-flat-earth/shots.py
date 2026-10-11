# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv of (regel, extra s), afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Snelle stijl (test, okt 2026): alleen foto's, ca. elke 1-1,5 s een nieuw beeld, ook binnen een zin; geen clips.
# Atlas-stem tempo 1.0, harde opening zonder fade-in, geen titeltekst.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"F01","in","",None),(2,"F02","punch","",None,"dust"),((2,0.9),"F03","in","",None,"dust"),((2,1.8),"F04","out","",None),
 (3,"F05","in",FLASH,None),(4,"F06","punch","",None,"dust"),((4,1.0),"F07","in","",None),(5,"F08","shake","",None,"dust"),
 (6,"F09","punch","",None),(7,"F10","in","",None),((7,0.8),"F11","out","",None),
 (8,"F12","in","",("EARTH'S EQUATOR","40,075 km")),(9,"F13","shake","",None,"embers"),(10,"F14","out","",None),(11,"F15","in","",None)]
BANG = 4       # shot-index (vanaf 0) met flits + klap
FADE_IN = 0    # meteen beeld
