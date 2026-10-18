# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# 19 okt 2026 (cloudsessie): script herschreven (feiten: geen "regen stopt"/"60 m zeespiegel"/Venus; twist = middernachtzon Svalbard),
# "Right now." eruit, tijdstappen "After …", 12 nieuwe beeldprompts (geen thermometers). Regelnummers volgen --dry-run (30 regels).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"M01","in","",None),(2,"M02","in","",None,"dust"),(4,"M03","out","",None),(7,"M04","punch",FLASH,None),
 (8,"M05","in","",("NO SUNSET","AFTER 1 DAY")),(10,"M06","out","",None,"dust"),
 (11,"M07","in","",("NO SUNSET","AFTER 1 WEEK")),(14,"M08","out","",None),
 (15,"M09","in","",("NO SUNSET","AFTER 1 MONTH")),(18,"M10","up","",None),
 (19,"M11","in","",("NO SUNSET","AFTER 1 YEAR"),"dust"),(21,"M12","in","",None),
 (22,"M13","in","",None),(23,"M14","in","",None),(24,"M15","in","",("SVALBARD, NORWAY","4 MONTHS")),
 (25,"M16","out","",None),(27,"M17","in","",None),(30,"M18","out","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld
