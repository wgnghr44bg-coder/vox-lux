# Niche-scan elke maandag 10:30 (eigenaar 22 nov 2026). Na 09:00, want dan begint de YouTube-quota opnieuw.
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') niche-scan" | Out-File -Append -Encoding utf8 'C:\Users\rane\niche-scan.log'
& 'C:\Users\rane\AppData\Local\Programs\Python\Python312\python.exe' tools/niche_scan.py --git *>> 'C:\Users\rane\niche-scan.log'
