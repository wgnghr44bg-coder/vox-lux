# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv waar de shot begint, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None)
# beweging: in, out, up (camera glijdt omhoog), shake (trillen), punch (harde inzoom)
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"I01","out","eq=brightness=-0.12",None),(3,"I02","in","",None),(4,"I03","in","",None),(6,"I02","shake",FLASH,None),
 (7,"I04","punch","",None),(8,"I05","in","",("STEEL","98% IRON")),(9,"I06","in","",None),(10,"I07","out","",None),
 (11,"I08","in","",None),(13,"I09","in","",("UNTIL BLACKOUT","~10 SEC")),
 (15,"I10","in","",None),(16,"I10","punch","",("EARTH'S MASS","−32%")),(17,"I11","out","",("MAGNETIC FIELD","0")),
 (18,"I12","out","",None),(20,"I12","punch","",("FORGED IN","SUPERNOVAE")),
 (22,"I13","in","",("IRON IN YOUR BODY","4 g"))]
BANG = 3   # shot-index (vanaf 0) met flits + klap; None = geen
