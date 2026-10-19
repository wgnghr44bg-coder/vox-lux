# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# 19 okt 2026 (nachtrun): "What if the internet disappeared overnight?"
# twist: het internet zit niet in de lucht maar op de zeebodem (1,5 miljoen km kabel);
# in 2008 werden twee kabels bij Alexandrie doorgeknipt (Egypte 70%, India 60%) en in 2011
# sneed een vrouw met een spade Armenie offline.
# Geen clips, alleen foto's + Ken Burns. Regelnummers volgen voice-times.tsv (29 regels).
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"M01","in","",None),
 (2,"M02","in","",None,"dust"),
 (4,"M03","out","",None),
 (7,"M04","punch",FLASH,None),
 (8,"M05","in","",("NO INTERNET","1 HOUR")),
 (10,"M06","out","",None),
 (11,"M07","in","",("NO INTERNET","1 DAY")),
 (13,"M08","out","",None,"dust"),
 (14,"M09","in","",("NO INTERNET","1 WEEK")),
 (16,"M10","in","",None),
 (17,"M11","up","",("NO INTERNET","1 MONTH")),
 (19,"M12","in","",None),
 (20,"M13","out","",None),
 (21,"M14","in","",("CABLE ON THE SEABED","1.5M KM")),
 (23,"M15","in","",("CABLES CUT","2008")),
 (24,"M16","out","",("NETWORK DOWN","70%")),
 (26,"M17","in","",None,"dust"),
 (27,"M18","in","",None),
 (29,"M19","out","",None)]
BANG = 3       # shot-index (vanaf 0) met flits + klap ("Then.")
FADE_IN = 0    # meteen beeld
