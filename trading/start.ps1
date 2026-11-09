# Start de trading bot en het dashboard, elk in een eigen venster.
#   .\start.ps1                         OANDA (oefen- of live-rekening volgens OANDA_OMGEVING)
#   .\start.ps1 -Broker bitvavo         Bitvavo oefenstand (nepgeld)
#   .\start.ps1 -Broker bitvavo -EchtGeld
param([ValidateSet("oanda", "bitvavo")][string]$Broker = "oanda", [switch]$EchtGeld)
$map = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($Broker -eq "bitvavo") {
    $extra = if ($EchtGeld) { " --echt-geld" } else { "" }
    $bot = "python bitvavo_bot.py$extra"
    $dash = "python dashboard.py --broker bitvavo$extra"
    $poort = 8788
} else {
    $extra = if ($EchtGeld) { " --echt-geld" } else { "" }
    $bot = "python bot.py$extra"
    $dash = "python dashboard.py"
    $poort = 8787
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; $bot" -WindowStyle Minimized
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$map'; $dash" -WindowStyle Minimized
Start-Sleep 2
Start-Process "http://localhost:$poort"
