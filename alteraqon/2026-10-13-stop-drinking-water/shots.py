# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Mix (eigenaar 13 okt 2026): 6 Wan-clips (clips/: S00 S03 S05 S07 S08 S11) + foto's met Ken Burns en gratis effect uit fx.py,
# plus opvulbeelden (xxb/S09a) waar één beeld anders 6-7 s blijft staan.
# Clips met vervorming/nieuwe objecten (S02 S04 S09: er schuift een hand in beeld) staan in clips-ongebruikt/.
# Harde opening zonder fade-in, geen titeltekst. Regelnummers volgen voice-times.tsv (hangen alleen van het script af).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"S00","in","",None),(4,"S01","in","",None,"dust"),(6,"S01b","out","",None,"dust"),(8,"S02","in",FLASH,None),
 (9,"S03","in","",("NO WATER","6 HOURS")),(11,"S03b","in","",None,"dust"),
 (12,"S04","shake","",("NO WATER","12 HOURS"),"dust"),(15,"S04b","shake","",None),
 (16,"S05","in","",("NO WATER","1 DAY")),(19,"S05b","shake","",None),
 (20,"S06","out","",("NO WATER","3 DAYS"),"dust"),(22,"S06b","in","",None),
 (23,"S07","in","",None),(24,"S08","in","",None),(25,"S08b","in","",None,"dust"),
 (26,"S09a","in","",None,"dust"),(28,"S09","in","",("WORLD RECORD","18 DAYS")),
 (29,"S10","out","",None),(31,"S11","in","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap
FADE_IN = 0    # meteen beeld
