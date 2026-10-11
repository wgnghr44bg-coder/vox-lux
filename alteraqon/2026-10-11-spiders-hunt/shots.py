# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv waar de shot begint, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None)
# beweging: in, out, up (camera glijdt omhoog), shake (trillen), punch (harde inzoom)
# Snelle stijl (eigenaar okt 2026): Atlas-stem tempo 1.0, harde opening zonder fade-in, geen titeltekst.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"W01","punch","",None),(2,"W02","in","eq=brightness=0.06",None),(4,"W03","in","",None),(6,"W04","shake",FLASH,None),
 (7,"W05","in","",("SPIDER SPECIES","50,000+")),(8,"W06","out","",("TOTAL WEIGHT","25,000,000 t")),
 (9,"W07","punch","",("PREY PER YEAR","800,000,000 t")),(10,"W08","in","",("VS. ALL HUMANS","2×")),
 (11,"W09","in","",None),(12,"W01","in","",None),(13,"W10","out","",None),
 (14,"W11","in","",("ONE COLONY","20,000+")),(15,"W12","out","",None),(17,"W13","in","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap; None = geen
FADE_IN = 0    # meteen beeld
