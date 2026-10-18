# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Alleen foto's + Ken Burns + gratis effecten. Harde opening, geen titeltekst.
# 18 okt 2026 (cloudsessie): twist gecorrigeerd (Wadlow stierf aan een ontstoken blaar door een beenbeugel, niet aan zijn hart),
# "Right now." eruit, tijdstappen "After …". Regelnummers volgen make_voice_local.py --dry-run (30 regels).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"M01","in","",None),(2,"M02","in","",None,"dust"),(4,"M03","in","",None),(6,"M04","in",FLASH,None),
 (7,"M06","in","",("1 CM PER MINUTE","AFTER 1 HOUR")),(10,"M07","out","",("1 CM PER MINUTE","AFTER 1 DAY")),
 (13,"M08","in","",None),(14,"M09","up","",("1 CM PER MINUTE","AFTER 1 WEEK")),(17,"M10","shake","",None),
 (20,"M11","in","",None),(21,"M12","in","",("TALLEST MAN EVER","2.72 M"),"dust"),(24,"M13","in","",None,"dust"),
 (25,"M14","out","",None),(28,"M15","in","",None),(30,"M16","out","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld
