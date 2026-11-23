# Render hele lange video (los proces), log C:\Users\rane\swap-render.log
Set-Location 'C:\Users\rane\Documents\vox-lux-routine\kanalen\marketdoodle\video-swap'
$env:PYTHONUTF8 = 1
& 'C:\Users\rane\omnivoice-venv\Scripts\python.exe' -u maak_heel.py *> 'C:\Users\rane\swap-render.log'
"RENDER-KLAAR" | Out-File -Append -Encoding utf8 'C:\Users\rane\swap-render.log'
