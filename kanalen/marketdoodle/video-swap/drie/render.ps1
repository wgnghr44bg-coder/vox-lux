Set-Location 'C:\Users\rane\Documents\vox-lux-routine\kanalen\marketdoodle\video-swap\drie'
$env:PYTHONUTF8 = 1
& 'C:\Users\rane\omnivoice-venv\Scripts\python.exe' -u maak3.py *> 'C:\Users\rane\swap3-render.log'
"RENDER-KLAAR" | Out-File -Append -Encoding utf8 'C:\Users\rane\swap3-render.log'
