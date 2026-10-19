# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Alleen foto's M01-M18 + Ken Burns + gratis effecten uit fx.py, geen clips. Harde opening, geen titeltekst.
# Regelnummers volgen make_voice_local.py --dry-run (26 regels; "Then." = regel 6; tijdstappen op regel 7/10/13/16).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"M01","in","",None),(2,"M02","out","",None),(4,"M03","up","",None,"dust"),
 (6,"M04","punch",FLASH,None),(7,"M05","out","",("NO SEA","1 HOUR")),(9,"M06","in","",None),
 (10,"M07","in","",("NO SEA","1 DAY")),(12,"M08","up","",None),
 (13,"M09","out","",("NO SEA","1 WEEK")),(15,"M10","shake","",None,"dust"),
 (16,"M11","up","",("NO SEA","1 MONTH")),(18,"M12","in","",None),(19,"M13","in","",None),
 (20,"M14","in","",("MEDITERRANEAN DRIED UP","6 MILLION YRS")),(21,"M15","out","",None,"dust"),
 (22,"M16","up","",None),(23,"M17","shake","",None,"dust"),(24,"M18","out","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld
