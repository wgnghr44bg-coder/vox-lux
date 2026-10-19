# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Test (eigenaar 18 okt 2026): alleen foto's M01-M19 + Ken Burns + gratis effecten uit fx.py, geen clips. Harde opening, geen titeltekst.
# Regelnummers volgen make_voice_local.py --dry-run (30 regels; 18 okt: "Right now." eruit, tijdstappen beginnen met "After …"); na de stem controleren tegen voice-times.tsv.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"M01","in","",None),(3,"M02","in","",None,"dust"),(5,"M03","out","",None),(7,"M04","in",FLASH,None),
 (8,"M05","in","",("NO MOON","1 NIGHT")),(10,"M06","out","",None),
 (12,"M07","in","",("NO MOON","1 DAY")),(15,"M08","out","",None),
 (16,"M09","in","",("NO MOON","1 MONTH"),"dust"),(18,"M10","in","",None),
 (19,"M11","in","",("NO MOON FOR MILLIONS OF","YEARS")),(21,"M12","out","",None),
 (22,"M13","in","",None),(23,"M14","in","",None),(24,"M15","in","",None,"dust"),(25,"M16","in","",None),
 (26,"M17","in","",("DRIFTING AWAY EVERY YEAR","3.8 CM")),(27,"M18","out","",None),(29,"M19","in","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld
