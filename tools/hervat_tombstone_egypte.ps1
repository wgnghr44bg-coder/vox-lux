# Hervatten na de gestopte test (9 nov 2026, eigenaar: "ik laat het script wel hier maken en de rest via pc").
# Eerst Tombstone afmaken + vervangen (ma 16 nov), dan Egypte montage + vervangen (ma 23 nov). Stem en muziek van Egypte zijn al klaar.
# Log: C:\Users\rane\hervat.log (ook op de website)
$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
$env:REPO = 'C:/Users/rane/Documents/vox-lux-routine'
$bash = 'C:\Program Files\Git\bin\bash.exe'
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
function WachtOpRoutine {
    while (Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | ? { $_.CommandLine -like '*PROMPT-ROUTINE-PC*' }) {
        Stap 'routine bezig, wachten'; Start-Sleep 600 }
}
git pull -q --rebase --autostash
Stap 'Tombstone: opnieuw vanaf de beweging'
& 'C:\Users\rane\Documents\vox-lux-routine\tools\tombstone_herstel.ps1'
WachtOpRoutine
Stap 'Egypte: montage'
$mont = & $bash tools/montage_engine.sh egypte-toetanchamon "What Did People Actually Do When Tutankhamun Was King? | History for Sleep" thumbnail-gekozen.jpg 2>&1
$mont | Select -Last 40
$mt = $mont -join "`n"
if ($mt -match 'CONTROLE GOED' -and $mt -match 'TEKST GOED' -and $mt -match 'APPROVED') {
    Stap 'Egypte: controles goed, uploaden en oude vervangen'
    python tools/vervang_video.py stories/egypte-toetanchamon --video stories/egypte-toetanchamon/video/egypte-toetanchamon-16mm.mp4 --publish-at 2026-11-23T20:00:00Z --thumbnail stories/egypte-toetanchamon/thumbnail-gekozen.jpg --soort oudheid --oud ctC36HRFIac --tags 'tutankhamun, ancient egypt, egypt history for sleep, valley of the kings, pharaoh'
} else { Stap 'Egypte: CONTROLES NIET GOED, niet geüpload (de oude versie blijft staan)' }
Stap 'HERVAT KLAAR'