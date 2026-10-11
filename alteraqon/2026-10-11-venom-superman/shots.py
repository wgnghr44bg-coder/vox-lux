# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv waar de shot begint, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None)
# beweging: in, out, up (camera glijdt omhoog), shake (trillen), punch (harde inzoom)
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"V01","out","eq=brightness=-0.12",None),(3,"V02","in","",None),(5,"V03","in","",None),(6,"V04","shake",FLASH,None),
 (7,"V05","in","",("VENOM, FIRST FULL ISSUE","1988")),(8,"V06","out","",None),(9,"V07","in","",None),(10,"V08","in","",None),
 (12,"V09","in","",None),(13,"V10","in","",("SYMBIOTE WEAKNESSES","2")),(15,"V11","in","",None),
 (17,"V06","punch","",("SPEED OF SOUND","1,235 km/h")),(18,"V12","out","",None),
 (19,"V13","in","",("ACTION COMICS #1","1938")),(20,"V13","punch","",("RECORD SALE, 2024","$6,000,000")),
 (21,"V02","out","eq=brightness=-0.08",None)]
BANG = 3   # shot-index (vanaf 0) met flits + klap; None = geen
