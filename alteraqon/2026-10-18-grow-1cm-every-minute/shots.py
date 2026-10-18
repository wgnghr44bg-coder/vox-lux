# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Test (eigenaar 18 okt 2026): alleen foto's M01-M16 + Ken Burns + gratis effecten uit fx.py, geen clips. Harde opening, geen titeltekst.
# Regelnummers volgen voice-times.tsv (30 regels); "Then." op regel 6.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [
    (1,"M01","in","",None),
    (2,"M02","in","",None,"dust"),
    (4,"M03","out","",None),
    (6,"M04","in",FLASH,None),
    (7,"M06","in","",("GROWING","AFTER 1 HOUR")),
    (10,"M07","in","",("GROWING","AFTER 1 DAY")),
    (13,"M08","in","",("HEART STRUGGLES","14 M")),
    (14,"M09","in","",("GROWING","AFTER 1 WEEK")),
    (17,"M10","in","",("SQUARE CUBE LAW","100 M")),
    (20,"M11","in","",None),
    (21,"M12","in","",("TALLEST EVER","2.72 M")),
    (24,"M13","in","",("BRACES","1940")),
    (25,"M14","in","",("DIED AT","22")),
    (28,"M15","in","",None),
    (30,"M16","out","",None),
]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.") -> M04 is de 4e shot (index 3)
FADE_IN = 0    # meteen beeld