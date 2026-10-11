# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Mix-stijl (eigenaar okt 2026): 2 xAI-lite-clips (K01, K04 -> afbeeldingen/*.mp4) + gratis effecten uit fx.py op de foto's.
# Atlas-stem tempo 1.0, harde opening zonder fade-in, geen titeltekst.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"K01","in","",None),(2,"K02","in","",None,"dust"),(4,"K03","in","",None,"dust+embers"),
 (5,"K04","in",FLASH,("LAVA","1,000+ °C")),(7,"K06","out","",None,"ash"),(9,"K07","in","",None,"dust"),
 (11,"K08","shake","",("PYROCLASTIC FLOW","700 km/h"),"ash"),(12,"K09","in","",None,"embers"),
 (14,"K10","in","",("PARÍCUTIN, 1943","50 m IN 1 DAY"),"ash"),(16,"K11","out","",("AUCKLAND VOLCANIC FIELD","53 VOLCANOES"))]
BANG = 3       # shot-index (vanaf 0) met flits + klap
FADE_IN = 0    # meteen beeld
