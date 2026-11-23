# Lange video 'Swapped lives' (23 nov): stemmen -> woordtijden. Los proces (lang), log: C:\Users\rane\swap-stem.log
Set-Location 'C:\Users\rane\Documents\vox-lux-routine\kanalen\marketdoodle\video-swap'
$env:PYTHONUTF8 = 1
$py = 'C:\Users\rane\omnivoice-venv\Scripts\python.exe'
"=== $(Get-Date -Format 'HH:mm') stemmen" | Out-File -Encoding utf8 'C:\Users\rane\swap-stem.log'
& $py stem.py script.txt *>> 'C:\Users\rane\swap-stem.log'
"=== $(Get-Date -Format 'HH:mm') woordtijden" | Out-File -Append -Encoding utf8 'C:\Users\rane\swap-stem.log'
& $py woordtijden.py en *>> 'C:\Users\rane\swap-stem.log'
"=== STEM-KLAAR $(Get-Date -Format 'HH:mm')" | Out-File -Append -Encoding utf8 'C:\Users\rane\swap-stem.log'
