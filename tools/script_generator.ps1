# Scriptgenerator (eigenaar 8 nov 2026): elke dag één script ombouwen naar de nieuwe opbouw of nieuw schrijven.
# Gestart door Windows Taakplanner ("Sleep Archives scriptgenerator", dagelijks 06:00). Alleen tekst, geen kosten.
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
git checkout main
git pull
$env:CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS = '0'
"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') scriptgenerator" | Out-File -Append -Encoding utf8 'C:\Users\rane\sleep-archives-scripts-log.txt'
& 'C:\Users\rane\.local\bin\claude.exe' -p 'Lees stories/PROMPT-SCRIPT-PC.md op main en voer het helemaal uit.' --dangerously-skip-permissions *>> 'C:\Users\rane\sleep-archives-scripts-log.txt'
