# Keten 8 nov 2026 (eigenaar: "ik wil alles automatisch en via pc"): Tombstone afmaken en vervangen, dan Egypte maken
# en vervangen. Zonder Claude, alleen de vaste gereedschappen. Log: C:\Users\rane\keten-tombstone-egypte.log
$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
$env:REPO = 'C:/Users/rane/Documents/vox-lux-routine'
$O = 'C:/Users/rane/omnivoice-venv/Scripts/python.exe'
$bash = 'C:\Program Files\Git\bin\bash.exe'
$tomblog = $args[0]   # log van de lopende Tombstone-montage
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
function WachtOpRoutine {   # de routine (zo/di/do 09:00) en deze keten mogen niet tegelijk de videokaart gebruiken
    while (Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | ? { $_.CommandLine -like '*PROMPT-ROUTINE-PC*' }) {
        Stap 'routine bezig, wachten'; Start-Sleep 600 }
}

# 1. Tombstone: wachten tot de montage klaar is, controles nakijken, dan vervangen (los proces: wachten op YouTube duurt uren)
Stap 'Tombstone: wachten op montage'
while (-not (Select-String $tomblog -Pattern '=== KLAAR' -Quiet)) { Start-Sleep 60 }
$t = Get-Content $tomblog -Raw
if ($t -match 'CONTROLE GOED' -and $t -match 'TEKST GOED' -and $t -match 'APPROVED' -and (Test-Path 'stories/tombstone-1881/video/tombstone-1881-16mm.mp4')) {
    Stap 'Tombstone: controles goed, uploaden en oude vervangen'
    Start-Process python -ArgumentList 'tools/vervang_video.py','stories/tombstone-1881','--video','stories/tombstone-1881/video/tombstone-1881-16mm.mp4','--publish-at','2026-11-11T20:00:00Z','--thumbnail','stories/tombstone-1881/thumbnail-gekozen.jpg','--soort','mysterie','--oud','4RjjJh-j5a0','--tags','tombstone, tombstone arizona, wyatt earp, ok corral, wild west history' -RedirectStandardOutput 'C:\Users\rane\keten-tombstone-upload.log' -NoNewWindow
} else { Stap 'Tombstone: CONTROLES NIET GOED, niet geüpload (zie montage-log)' }

# 2. Egypte: eerst de vaste controles, dan stem, tekstcontrole met herstel, montage
WachtOpRoutine
Stap 'Egypte: B1-controle en afwisseling'
& $O tools/b1_check.py 2>$null
if ($LASTEXITCODE -ne 0) { Stap 'Egypte: B1 AFWIJKING, gestopt'; exit 1 }
python tools/check_afwisseling.py stories/egypte-toetanchamon
if ($LASTEXITCODE -ne 0) { Stap 'Egypte: AFWISSELING FOUT, gestopt'; exit 1 }
Stap 'Egypte: stem'
& $O tools/engine_stem.py stories/egypte-toetanchamon 2>$null | Select-String 'afgekapt|woorden/min' | % Line
for ($r = 1; $r -le 4; $r++) {
    Stap "Egypte: voorbereiding ronde $r"
    $uit = & $bash tools/prep_engine.sh egypte-toetanchamon 2>&1
    $uit | Select-String '^zin|gecontroleerd|TEKST' | % Line
    $fout = ($uit | Select-String 'TEKST FOUT.*egypte-toetanchamon (.+)$').Matches
    if (-not $fout) { break }
    if ($r -eq 4) { Stap 'Egypte: NOG TEKSTFOUTEN na 3 rondes, gestopt'; exit 1 }
    $nrs = ($fout[0].Groups[1].Value.Trim() -split '\s+') -join ','
    WachtOpRoutine
    & $O tools/engine_stem.py stories/egypte-toetanchamon --hergebruik --opnieuw $nrs --seed-extra (3000 * $r) 2>$null | Select -Last 2
}
WachtOpRoutine
Stap 'Egypte: montage'
$mont = & $bash tools/montage_engine.sh egypte-toetanchamon "What Did People Actually Do When Tutankhamun Was King? | History for Sleep" thumbnail-gekozen.jpg 2>&1
$mont
$mt = $mont -join "`n"
if ($mt -match 'CONTROLE GOED' -and $mt -match 'TEKST GOED' -and $mt -match 'APPROVED') {
    Stap 'Egypte: controles goed, uploaden en oude vervangen'
    python tools/vervang_video.py stories/egypte-toetanchamon --video stories/egypte-toetanchamon/video/egypte-toetanchamon-16mm.mp4 --publish-at 2026-11-14T20:00:00Z --thumbnail stories/egypte-toetanchamon/thumbnail-gekozen.jpg --soort oudheid --oud ctC36HRFIac --tags 'tutankhamun, ancient egypt, egypt history for sleep, valley of the kings, pharaoh'
} else { Stap 'Egypte: CONTROLES NIET GOED, niet geüpload' }
Stap 'KETEN KLAAR'
