# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Nieuwe set W01-W25 (eigenaar 13 okt 2026: elk beeld toont letterlijk wat er gezegd wordt, "wow"-beelden).
# Mix: 13 clips (W01 W02 W03 W04 W08 W09 W11 W14 W16 W22 W23 W24 W25, clips/), de rest foto + Ken Burns + gratis effect uit fx.py.
# Oude set staat in afbeeldingen-oud/ en clips-ongebruikt/. Harde opening, geen titeltekst.
# Regelnummers volgen voice-times.tsv (hangen alleen van het script af).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"W01","in","",None),(2,"W02","in","",None),(3,"W03","in","",None),(4,"W04","in","",None,"dust"),
 (5,"W05","in","",None),(6,"W06","in","",None),(8,"W07","in",FLASH,None),
 (9,"W08","in","",("NO WATER","6 HOURS")),(11,"W09","in","",None),
 (12,"W10","in","",("NO WATER","12 HOURS")),(14,"W11","out","",None),(15,"W12","shake","",None),
 (16,"W13","in","",("NO WATER","1 DAY")),(18,"W14","in","",None),(19,"W15","shake","",None,"dust"),
 (20,"W16","in","",("NO WATER","3 DAYS")),(22,"W17","out","",None,"dust"),
 (23,"W18","in","",None),(24,"W19","in","",None,"dust"),(25,"W20","in","",None,"dust"),(26,"W21","in","",None,"dust"),
 (28,"W22","in","",("WORLD RECORD","18 DAYS")),(29,"W23","in","",None),(31,"W24","in","",None),(33,"W25","in","",None)]
BANG = 6       # shot-index (vanaf 0) met flits + klap
FADE_IN = 0    # meteen beeld
