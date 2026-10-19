# Shots voor alteraqon/tools/make_video.py – LANGE video (16:9)
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Regels komen uit make_voice_local.py --dry-run (49 zinnen; "Then." = regel 17); na de stem gecontroleerd tegen voice-times.tsv.
# Tijdstempels: stem zegt "After …", in beeld alleen label + groot getal (max 13 tekens, zonder AFTER).
LONG = True                # 1920x1080 + mix van music.mp3
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [
 (1,"M01","in","",None),                (2,"M02","out","",None),            (4,"M03","in","",None),
 (5,"M04","up","",None,"rain"),         (6,"M05","out","",None),            (7,"M06","punch","",None),
 (8,"M07","in","",None),                (10,"M08","out","",None),           (12,"M09","up","",None),
 (13,"M10","in","",None),               (15,"M11","out","",None),           (16,"M12","shake","",None),
 (17,"M13","in",FLASH,None),            (18,"M14","up","",None),
 (19,"M15","in","",("LOW TIDE","1 HOUR")),          (20,"M16","out","",None),
 (21,"M17","in","",("LEAVES BACK","1 DAY")),        (22,"M18","up","",None),
 (23,"M19","in","",("THE WALLS","1 WEEK")),         (24,"M20","punch","",None,"dust"),
 (25,"M21","in","",("LIGHTS OUT","1 MONTH")),       (26,"M22","out","",None),
 (27,"M23","in","",("DESERT","1 YEAR")),            (28,"M24","up","",None),
 (29,"M25","in","",("TEN YEARS","10 YEARS")),       (30,"M26","out","",None),
 (31,"M27","in","",("A CENTURY","100 YEARS")),      (32,"M28","up","",None),
 (34,"M29","in","",None),                (35,"M30","shake","",None),        (36,"M31","out","",None,"embers"),
 (38,"M32","in","",None),                (39,"M33","up","",None),           (40,"M34","punch","",None),
 (41,"M35","in","",None),                (42,"M36","out","",None),          (43,"M37","up","",None),
 (44,"M38","in","",None),                (45,"M39","out","",None),          (46,"M40","up","",None),
 (47,"M41","in","",None),                (49,"M42","out","",None),
]
BANG = 12    # shot-index (vanaf 0) met flits + knal: M13 bij "Then." (regel 17)
FADE_IN = 0  # meteen beeld, harde opening (zoals sky-countdown)
