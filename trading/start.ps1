# Start de bot en het dashboard, elk in een eigen venster.
#   .\start.ps1                       trendfilter-bot (wekelijks inleggen + SMA200), oefenstand
#   .\start.ps1 -EchtGeld             trendfilter-bot met echt geld
#   .\start.ps1 -Bot handel           de handelsbot (sweep / smc / trend), oefenstand
# Draai maar één bot tegelijk: ze delen hetzelfde dashboard en Bitvavo-saldo.
param([ValidateSet("trend", "handel")][string]$Bot = "trend", [switch]$EchtGeld)
$map = Split-Path -Parent $MyInvocation.MyCommand.Path
$extra = if ($EchtGeld) { " --echt-geld" } else { "" }
$script = if ($Bot -eq "trend") { "trend_bot.py" } else { "bitvavo_bot.py" }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; python $script$extra" -WindowStyle Minimized
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; python dashboard.py$extra" -WindowStyle Minimized
Start-Sleep 2
Start-Process "http://localhost:8788"
