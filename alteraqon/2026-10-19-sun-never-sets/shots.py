# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Test (eigenaar 18 okt 2026): alleen foto's M01-M18 + Ken Burns + gratis effecten uit fx.py, geen clips. Harde opening, geen titeltekst.
# Regelnummers volgen voice-times.tsv (39 regels); "Then." op regel 9.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [
    (1,"M01","in","",None),
    (3,"M02","in","",None,"dust"),
    (5,"M03","out","",None),
    (9,"M04","in",FLASH,None),
    (10,"M05","in","",("ETERNAL DAY","AFTER 1 HOUR")),
    (13,"M06","in","",("ETERNAL DAY","AFTER 1 DAY")),
    (16,"M07","in","",("PLANTS BURN","40°C")),
    (18,"M08","in","",("ETERNAL DAY","AFTER 1 WEEK")),
    (21,"M09","in","",("ETERNAL DAY","AFTER 1 MONTH")),
    (24,"M10","in","",("WATER CYCLE","BROKEN")),
    (26,"M11","in","",("ETERNAL DAY","AFTER 1 YEAR")),
    (29,"M12","in","",("SEA LEVEL","+60 M")),
    (31,"M13","in","",None),
    (32,"M14","in","",("VENUS","5832 HOUR DAY")),
    (34,"M15","in","",("VENUS DAY","5832 HOURS")),
    (35,"M16","in","",("VENUS TEMP","462°C")),
    (36,"M17","in","",None),
    (39,"M18","out","",None),
]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.") -> M04 is de 4e shot (index 3)
FADE_IN = 0    # meteen beeld