# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Regels volgen make_voice_local.py output (voice-times.tsv); na de stem controleren.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [
    (1,"M01","in","",None),                          # What if a whale swallowed you?
    (3,"M02","in","",None,"dust"),                   # You float... shadow rises
    (4,"M03","out","",None),                         # Mouth opens... you slide in
    (6,"M04","in",FLASH,None),                       # Then. (BANG)
    (7,"M05","in","",("WHALE","1 MINUTE")),          # One minute.
    (9,"M06","out","",("WHALE","1 HOUR")),           # One hour.
    (12,"M07","in","",("WHALE","1 DAY")),            # One day.
    (15,"M08","in","",("WHALE","1 WEEK")),           # One week.
    (18,"M09","in","",None),                         # But here is the twist.
    (19,"M10","in","",None,"dust"),                  # No whale can swallow...
    (21,"M11","in","",("BLUE WHALE THROAT","GRAPEFRUIT")),  # grapefruit-sized
    (22,"M12","in","",None),                         # sperm whale throat
    (23,"M13","in","",None,"dust"),                  # James Bartley story fake
    (24,"M14","in","",("SPERM WHALE DEPTH","2000 M")), # dive 2000 meters
    (25,"M15","in","",("BREATH HOLD","90 MINUTES")),  # hold breath 90 min
    (26,"M16","out","",None),                        # So remember.
    (28,"M17","in","",None),                         # Would you still swim...
]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld