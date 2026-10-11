# Shots voor alteraqon/tools/make_video.py
# (regel in voice-times.tsv, afbeelding, beweging, extra ffmpeg-filter, (label, groot getal) of None, [effectlaag])
# Mix-stijl (eigenaar okt 2026): 2 xAI-lite-clips (K01, K03 -> afbeeldingen/*.mp4) + gratis effecten uit fx.py op de foto's.
# Atlas-stem tempo 1.0, harde opening zonder fade-in, geen titeltekst.
FLASH = "fade=t=in:st=0:d=0.7:color=white"   # witte flits bij de klap
SH = [(1,"K01","in","",None),(2,"K02","in","",None,"dust+embers"),(4,"K03","in",FLASH,None),
 (5,"K04","out","",("WORLD POPULATION","8.2 BILLION"),"embers"),(6,"K05","in","",None,"dust"),
 (8,"K06","in","",None,"dust"),(10,"K07","shake","",None,"dust"),(13,"K08","in","",None,"embers"),
 (15,"K09","in","",("BAJAU SPLEEN","+50%"),"dust"),(16,"K10","in","",("FEELS NO PAIN","1 GENE")),
 (17,"K11","in","",("TETRACHROMACY","4 CONE TYPES")),(19,"K12","out","",None,"embers")]
BANG = 2       # shot-index (vanaf 0) met flits + klap
FADE_IN = 0    # meteen beeld
