# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv waar de shot begint, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None)
# beweging: in, out, up (camera glijdt omhoog), shake (trillen), punch (harde inzoom)
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"L12","out","eq=brightness=-0.12",None),(3,"L01","in","",None),(5,"L02","in","",None),(6,"L03","shake",FLASH,None),
 (7,"L04","in","",("THE STRIKE","300,000,000 V")),(8,"L03","punch","",("AIR TEMPERATURE","30,000 °C")),
 (9,"L05","out","",("SURFACE OF THE SUN","5,500 °C")),(10,"L06","in","",None),
 (12,"L07","in","",("HEART RATE","0")),(13,"L08","up","",None),(14,"L09","in","",None),
 (16,"L10","out","",("SURVIVAL RATE","90%")),(17,"L11","in","",("PARK RANGER","7 STRIKES")),
 (18,"L12","in","",None)]
BANG = 3   # shot-index (vanaf 0) met flits + donderknal; None = geen
