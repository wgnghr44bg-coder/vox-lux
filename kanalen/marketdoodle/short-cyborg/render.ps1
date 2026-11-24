Set-Location 'C:\Users\rane\Documents\vox-lux-routine\kanalen\marketdoodle\short-cyborg'
$env:PYTHONUTF8 = 1
& 'C:\Users\rane\omnivoice-venv\Scripts\python.exe' -u maak.py *> 'C:\Users\rane\short-cyborg.log'
"RENDER-KLAAR" | Out-File -Append -Encoding utf8 'C:\Users\rane\short-cyborg.log'
