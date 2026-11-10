# Tombstone opnieuw (10 nov 2026, eigenaar: zelfde begin/reactievraag als WW2 + haperingen gehoord).
# Nieuw begin en slot (alleen die zinnen opnieuw ingesproken, B1), hele montage opnieuw, strenge haperingcontrole
# (tools/vergelijk_bron.py), pas bij alles goed de versie 03VXrW2gb7g vervangen. Log: C:\Users\rane\tombstone-opnieuw.log
$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
$env:REPO = 'C:/Users/rane/Documents/vox-lux-routine'
$O = 'C:/Users/rane/omnivoice-venv/Scripts/python.exe'
$bash = 'C:\Program Files\Git\bin\bash.exe'
$M = 'stories/tombstone-1881'; $N = 'tombstone-1881'
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
function WachtOpRoutine {
    while (Get-CimInstance Win32_Process | ? { $_.CommandLine -like '*PROMPT-ROUTINE-PC*' -or $_.CommandLine -like '*egypte_af.ps1*' }) {
        Stap 'routine of Egypte bezig, wachten'; Start-Sleep 600 }
}
WachtOpRoutine
git pull -q --rebase --autostash
Stap 'afwisseling'
python tools/check_afwisseling.py $M
if ($LASTEXITCODE -ne 0) { Stap 'AFWISSELING FOUT, gestopt'; exit 1 }
Stap 'stem: alleen de veranderde zinnen opnieuw (B1)'
& $O tools/engine_stem.py $M --hergebruik 2>$null | Select-String 'hergebruikt|afgekapt|woorden/min' | % Line
for ($r = 1; $r -le 4; $r++) {
    Stap "voorbereiding ronde $r"
    $uit = & $bash tools/prep_engine.sh $N 2>&1
    $uit | Select-String '^zin|gecontroleerd|TEKST' | % Line
    $fout = ($uit | Select-String "TEKST FOUT.*$N (.+)$").Matches
    if (-not $fout) { break }
    if ($r -eq 4) { Stap 'NOG TEKSTFOUTEN na 3 rondes, gestopt'; exit 1 }
    $nrs = ($fout[0].Groups[1].Value.Trim() -split '\s+') -join ','
    & $O tools/engine_stem.py $M --hergebruik --opnieuw $nrs --seed-extra (3000 * $r) 2>$null | Select -Last 2
}
WachtOpRoutine
Stap 'montage'
$mont = & $bash tools/montage_engine.sh $N "How Did Ordinary People Really Live in Tombstone? | History for Sleep" thumbnail-gekozen.jpg 2>&1
$mont | Select-String 'GOED|FOUT|APPROVED|REJECTED|Problem|===' | % Line
$mt = $mont -join "`n"
Stap 'strenge haperingcontrole (video tegen bron, ook zachte stukjes)'
$vb = python tools/vergelijk_bron.py $M "$M/video/$N-16mm.mp4" 2>&1; $vb
$slecht = 0; if (($vb -join "`n") -match '<0\.6: (\d+)') { $slecht = [int]$Matches[1] }
if ($mt -match 'CONTROLE GOED' -and $mt -match 'TEKST GOED' -and $mt -match 'APPROVED' -and $slecht -eq 0) {
    Stap 'alles goed: uploaden en 03VXrW2gb7g vervangen'
    python tools/vervang_video.py $M --video "$M/video/$N-16mm.mp4" --publish-at 2026-11-16T20:00:00Z --thumbnail "$M/thumbnail-gekozen.jpg" --soort mysterie --oud 03VXrW2gb7g --tags 'tombstone, tombstone arizona, wyatt earp, ok corral, wild west history'
} else { Stap "NIET geupload (haperingen: $slecht plekken; zie hierboven). De versie 03VXrW2gb7g blijft staan." }
Stap 'KLAAR'