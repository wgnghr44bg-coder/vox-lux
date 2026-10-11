# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv waar de shot begint, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None)
# beweging: in, out, up (camera glijdt omhoog), shake (trillen), punch (harde inzoom)
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"J01","out","eq=brightness=-0.12",None),(3,"J02","in","",None),(4,"J03","in","",None),(5,"J04","shake",FLASH,None),
 (6,"J05","in","",None),(7,"J06","in","",("DEEP BLUE VS KASPAROV","1997")),(8,"J07","in","",("ALPHAGO, MOVE 37","1 IN 10,000")),
 (9,"J08","out","",("PROTEIN STRUCTURES","200,000,000+")),(10,"J09","in","",None),
 (12,"J10","in","",("HUMAN BRAIN","20 W")),(13,"J11","out","",("AI DATA CENTER","100+ MW")),
 (14,"J01","in","",None),(16,"J12","in","",None),
 (19,"J13","in","",("I. J. GOOD","1965"))]
BANG = 3   # shot-index (vanaf 0) met flits + klap; None = geen
