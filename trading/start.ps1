# Start de trading bot en het dashboard, elk in een eigen venster.
$map = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; python bot.py" -WindowStyle Minimized
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; python dashboard.py" -WindowStyle Minimized
Start-Sleep 2
Start-Process "http://localhost:8787"
