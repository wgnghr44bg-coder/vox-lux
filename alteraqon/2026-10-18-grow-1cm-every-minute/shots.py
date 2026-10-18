# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Test (eigenaar 18 okt 2026): alleen foto's M01-M16 + Ken Burns + gratis effecten uit fx.py, geen clips. Harde opening, geen titeltekst.
# Regelnummers volgen make_voice_local.py --dry-run (32 regels); na de stem controleren tegen voice-times.tsv.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [
    (1,"M01","in","",None),
    (3,"M02","in","",None,"dust"),
    (5,"M03","out","",None),
    (7,"M04","in",FLASH,None),
    (8,"M05","in","",("GROWING","1 MINUTE")),
    (10,"M06","in","",("GROWING","1 HOUR")),
    (13,"M07","in","",("GROWING","1 DAY")),
    (16,"M08","in","",("HEART STRUGGLES","14.4 M")),
    (18,"M09","in","",("GROWING","1 WEEK")),
    (21,"M10","in","",("SQUARE CUBE LAW","100 M")),
    (23,"M11","in","",None),
    (24,"M12","in","",("TALLEST EVER","2.72 M")),
    (27,"M13","in","",("HEART FAILS","2.72 M")),
    (28,"M14","in","",("HARD LIMIT","3 M")),
    (30,"M15","in","",None),
    (32,"M16","out","",None),
]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.") -> M04 is de 4e shot (index 3)
FADE_IN = 0    # meteen beeld