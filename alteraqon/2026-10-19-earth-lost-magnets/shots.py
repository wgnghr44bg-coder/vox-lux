# Shots voor alteraqon/tools/make_video.py – LANGE video (16:9)
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Regels komen uit make_voice_local.py --dry-run (49 zinnen; "Then." = regel 10); na de stem gecontroleerd tegen voice-times.tsv.
# Let op: "Cold. Silent. Unbreathable." en "So remember. That shield is not a wall." zijn gesplitst ->
# die beelden (M28, M42) staan op hun EERSTE regel en blijven staan tot de volgende shot.
# Tijdstempels: stem zegt "After …", in beeld alleen label + groot getal (max 13 tekens, zonder AFTER).
LONG = True                # 1920x1080 + mix van music.mp3
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [
 (1,"M01","in","",None),                (2,"M02","out","",None),            (3,"M03","up","",None),
 (4,"M04","in","",None),                (5,"M05","out","",None),            (6,"M06","in","",None),
 (7,"M07","out","",None),               (8,"M08","up","",None),             (9,"M09","shake","",None),
 (10,"M10","punch",FLASH,None),         (11,"M11","in","",("COMPASSES SPIN","1 HOUR")),      (12,"M12","out","",None),
 (13,"M13","in","",("AURORA DIES","1 DAY")),        (14,"M14","out","",None),
 (15,"M15","in","",("SATELLITES DIE","1 WEEK")),    (16,"M16","up","",None),
 (17,"M17","out","",("GRIDS FAIL","1 MONTH")),      (18,"M18","shake","",None,"embers"),
 (19,"M19","in","",("AIR LEAKS","1 YEAR")),         (20,"M20","up","",None),
 (21,"M21","punch","",None),            (22,"M22","out","",None,"dust"),
 (23,"M23","in","",("SEAS SHRINK","100 YEARS")),    (24,"M24","out","",None,"dust"),
 (25,"M25","up","",("LAST WATER","1,000 YEARS")),   (26,"M26","in","",None,"dust"),
 (27,"M27","punch","",None),            (28,"M28","out","",None),           (31,"M29","in","",None,"dust"),
 (32,"M30","up","",None),               (33,"M31","in","",None),            (34,"M32","out","",None),
 (35,"M33","in","",None),               (36,"M34","out","",None),           (37,"M35","punch","",None),
 (38,"M36","in","",None),               (39,"M37","up","",None),            (40,"M38","in","",None),
 (41,"M39","out","",None),              (42,"M40","in","",None),            (43,"M41","out","",None),
 (44,"M42","up","",None),               (46,"M43","in","",None),            (47,"M44","out","",None),
 (48,"M45","up","",None),               (49,"M46","in","",None),
]
BANG = 9     # shot-index (vanaf 0) met flits + knal: M10 bij "Then." (regel 10)
FADE_IN = 0  # meteen beeld, harde opening (zoals sky-countdown)
