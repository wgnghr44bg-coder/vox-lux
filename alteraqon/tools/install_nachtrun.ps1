# Alteraqon: Windows-taak "Alteraqon-Nachtrun" aanmaken (elke nacht auto_run.ps1).
# Gebruik (eenmalig, door OpenCode op de pc):
#   powershell -ExecutionPolicy Bypass -File alteraqon\tools\install_nachtrun.ps1 -ComfyStart <pad naar ComfyUI-startbestand> -OpenCode <pad naar opencode.exe> [-Time 01:00]
# Schrijft %USERPROFILE%\alteraqon-auto.json, zet slaapstand op netstroom uit en maakt de taak (wekt de pc, draait ook
# als niemand is ingelogd als dat mag; anders alleen als de eigenaar ingelogd is).
param(
    [Parameter(Mandatory)] [string]$ComfyStart,
    [Parameter(Mandatory)] [string]$OpenCode,
    [string]$Time = '01:00',
    [string]$Videos = 'C:\Users\rane\Videos\alteraqon'
)
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
foreach ($f in $ComfyStart, $OpenCode) { if (-not (Test-Path $f)) { throw "Bestaat niet: $f" } }

@{ repo = $repo; comfy_start = $ComfyStart; opencode = $OpenCode; videos = $Videos } |
    ConvertTo-Json | Set-Content (Join-Path $env:USERPROFILE 'alteraqon-auto.json') -Encoding utf8
Write-Output "Instellingen: $env:USERPROFILE\alteraqon-auto.json"

# pc niet laten slapen op netstroom (anders mist hij de nacht)
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -WorkingDirectory $repo `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$repo\alteraqon\tools\auto_run.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 20) -MultipleInstances IgnoreNew
$user = "$env:USERDOMAIN\$env:USERNAME"
try {
    $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType S4U -RunLevel Limited
    Register-ScheduledTask -TaskName 'Alteraqon-Nachtrun' -Action $action -Trigger $trigger -Settings $settings `
        -Principal $principal -Force -ErrorAction Stop | Out-Null
    Write-Output "Taak gemaakt: elke dag $Time, ook als niemand is ingelogd (S4U), wekt de pc."
} catch {
    $principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName 'Alteraqon-Nachtrun' -Action $action -Trigger $trigger -Settings $settings `
        -Principal $principal -Force | Out-Null
    Write-Output "Taak gemaakt: elke dag $Time, wekt de pc - LET OP: alleen als de eigenaar ingelogd is (S4U mocht niet: $($_.Exception.Message))."
}
