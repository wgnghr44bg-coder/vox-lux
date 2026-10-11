# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv waar de shot begint, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None)
# beweging: in, out, up (camera glijdt omhoog), shake (trillen), punch (harde inzoom)
# Snelle stijl (eigenaar okt 2026): Atlas-stem tempo 1.0, harde opening zonder fade-in, geen titeltekst.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"C01","punch","",None),(2,"C02","in","eq=brightness=0.04",None),(4,"C03","in","",None),(6,"C04","shake",FLASH,None),
 (7,"C05","out","",("CLONES ON EARTH","8,000,000,000+")),(8,"C06","in","",("DOLLY THE SHEEP","1996")),
 (9,"C07","punch","",("ATTEMPTS","277")),(10,"C08","in","",("SHARED MEMORIES","0")),
 (11,"C09","in","",("CLONE'S AGE","0 YEARS")),(12,"C10","in","",("MATCHING FINGERPRINTS","0")),
 (13,"C11","in","",None),(15,"C12","out","",None),(17,"C13","in","",None),(19,"C01","out","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap; None = geen
FADE_IN = 0    # meteen beeld
