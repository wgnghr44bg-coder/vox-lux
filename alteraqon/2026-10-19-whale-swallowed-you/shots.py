# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# 19 okt 2026 (cloudsessie): script herschreven – eerst was het tegenstrijdig (eerst verteerd, dan "kan niet") met foute feiten;
# nu: echte twist Michael Packard (Cape Cod, juni 2021). geen clips meer (eigenaar 19 okt). Regelnummers volgen --dry-run (25 regels).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"M01","in","",None),(2,"M02","up","",None),(4,"M03","in","",None),(5,"M04","in",FLASH,None),
 (6,"M05","in","",("INSIDE THE WHALE","1 SECOND")),(8,"M06","shake","",None),
 (10,"M07","in","",("INSIDE THE WHALE","10 SECONDS")),(12,"M08","out","",None),
 (14,"M09","in","",("INSIDE THE WHALE","30 SECONDS")),
 (16,"M10","in","",None),(17,"M11","in","",("CAPE COD, USA","2021")),(18,"M12","in","",None),
 (19,"M13","punch","",None),(21,"M14","out","",None),(22,"M15","out","",None),(25,"M16","in","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld
