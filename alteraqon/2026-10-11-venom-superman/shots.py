# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv waar de shot begint, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None)
# beweging: in, out, up (camera glijdt omhoog), shake (trillen), punch (harde inzoom)
# Snelle versie (eigenaar okt 2026): Atlas-stem, ~35 s, harde opening zonder fade-in, hook-tekst in beeld.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"V05","punch","",None),(2,"V03","in","",None),(3,"V04","shake",FLASH,None),
 (4,"V02","punch","",None),(5,"V06","out","",None),(6,"V08","in","",None),(7,"V07","punch","",None),
 (8,"V09","in","",None),(9,"V10","in","",("SYMBIOTE WEAKNESSES","2")),(11,"V11","in","",None),
 (13,"V06","punch","",("SPEED OF SOUND","1,235 km/h")),(14,"V12","out","",None),
 (15,"V13","in","",("ACTION COMICS #1, 1938","$6,000,000")),(16,"V05","out","eq=brightness=-0.08",None)]
BANG = 2       # shot-index (vanaf 0) met flits + klap; None = geen
FADE_IN = 0    # meteen beeld
HOOK = ("VENOM\\Nvs SUPERMAN", 2.2)   # grote tekst in beeld vanaf 0 s
