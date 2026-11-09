# Start de Bitvavo-bot en het dashboard, elk in een eigen venster.
#   .\start.ps1             oefenstand (nepgeld, echte koersen)
#   .\start.ps1 -EchtGeld   echte Bitvavo-rekening
param([switch]$EchtGeld)
$map = Split-Path -Parent $MyInvocation.MyCommand.Path
$extra = if ($EchtGeld) { " --echt-geld" } else { "" }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; python bitvavo_bot.py$extra" -WindowStyle Minimized
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; python dashboard.py$extra" -WindowStyle Minimized
Start-Sleep 2
Start-Process "http://localhost:8788"
