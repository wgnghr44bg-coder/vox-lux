# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# 19 okt 2026 (nachtrun): "What if the Amazon rainforest burned down?" - twist: het Amazon was nooit onze longen
# (minder dan 10% van de zuurstof; de helft komt uit oceaanplankton) - het echte gevolg is de regen.
# Geen clips, alleen foto's + Ken Burns. Regelnummers volgen voice-times.tsv (26 regels).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"M01","in","",None,"embers"),
 (2,"M02","in","",None),
 (3,"M03","up","",None),
 (5,"M04","punch",FLASH,None,"embers"),
 (6,"M05","in","",("AMAZON FIRES","1 DAY")),
 (8,"M06","out","",None,"ash"),
 (9,"M07","in","",("AMAZON FIRES","1 WEEK"),"embers"),
 (11,"M08","out","",None,"ash"),
 (12,"M09","in","",("AMAZON FIRES","1 MONTH")),
 (14,"M10","in","",None,"dust"),
 (15,"M11","out","",("AMAZON FIRES","1 YEAR"),"dust"),
 (17,"M12","up","",None),
 (18,"M13","in","",None),
 (19,"M14","out","",None),
 (20,"M15","in","",("AMAZON OXYGEN","< 10%")),
 (21,"M16","in","",("OCEAN PLANKTON","50%")),
 (22,"M17","up","",None),
 (23,"M18","in","",None,"rain"),
 (26,"M19","out","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld
