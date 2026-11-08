# Eén voor één (eigenaar 8 nov 2026: "1 voor 1 ivm geheugen pc" en "alles testen zodat alles via de pc kan zonder Claude"):
# 1 test beeldmodel, 2 Tombstone uploaden + generator-test Gettysburg, 3 routine-lokaal test tot en met beelden,
# 4 Egypte maken en vervangen. Log: C:\Users\rane\testvolgorde.log
$ErrorActionPreference = 'Continue'
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
$env:REPO = 'C:/Users/rane/Documents/vox-lux-routine'
$O = 'C:/Users/rane/omnivoice-venv/Scripts/python.exe'
$bash = 'C:\Program Files\Git\bin\bash.exe'
$tomblog = $args[0]
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
function Vrij { foreach ($m in 'qwen3:14b', 'qwen2.5vl:7b') { try { Invoke-RestMethod -Uri http://127.0.0.1:11434/api/generate -Method Post -Body (@{model = $m; keep_alive = 0} | ConvertTo-Json) -ContentType 'application/json' | Out-Null } catch {} } }
function WachtOpRoutine { while (Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | ? { $_.CommandLine -like '*PROMPT-ROUTINE-PC*' }) { Stap 'routine bezig, wachten'; Start-Sleep 600 } }

Stap '1. TEST beeldmodel (30 foute + 30 goede beelden)'
python tools/beeldcheck_vlmtest.py 30
Vrij

Stap '2a. Tombstone: wachten op montage'
while (-not (Select-String $tomblog -Pattern '=== KLAAR' -Quiet)) { Start-Sleep 60 }
$t = Get-Content $tomblog -Raw
if ($t -match 'CONTROLE GOED' -and $t -match 'TEKST GOED' -and $t -match 'APPROVED' -and (Test-Path 'stories/tombstone-1881/video/tombstone-1881-16mm.mp4')) {
    Stap '2a. Tombstone: controles goed, uploaden en oude vervangen (los proces)'
    Start-Process python -ArgumentList 'tools/vervang_video.py','stories/tombstone-1881','--video','stories/tombstone-1881/video/tombstone-1881-16mm.mp4','--publish-at','2026-11-11T20:00:00Z','--thumbnail','stories/tombstone-1881/thumbnail-gekozen.jpg','--soort','mysterie','--oud','4RjjJh-j5a0','--tags','tombstone, tombstone arizona, wyatt earp, ok corral, wild west history' -RedirectStandardOutput 'C:\Users\rane\keten-tombstone-upload.log' -NoNewWindow
} else { Stap '2a. Tombstone: CONTROLES NIET GOED, niet geüpload' }

Stap '2b. TEST generator op Gettysburg (zonder Claude, testmodus)'
WachtOpRoutine
python tools/scriptgen/generator.py --map stories/gettysburg-1863 --test
Vrij

Stap '3. TEST routine-lokaal op Gettysburg tot en met beelden, beeldcontrole en thumbnail'
WachtOpRoutine
python tools/routine_lokaal.py --test-tot-beelden stories/gettysburg-1863
Vrij

Stap '4. Egypte: B1-controle en afwisseling'
WachtOpRoutine
& $O tools/b1_check.py 2>$null
if ($LASTEXITCODE -ne 0) { Stap 'Egypte: B1 AFWIJKING, gestopt'; exit 1 }
python tools/check_afwisseling.py stories/egypte-toetanchamon
if ($LASTEXITCODE -ne 0) { Stap 'Egypte: AFWISSELING FOUT, gestopt'; exit 1 }
Stap '4. Egypte: stem'
& $O tools/engine_stem.py stories/egypte-toetanchamon 2>$null | Select-String 'afgekapt|woorden/min' | % Line
for ($r = 1; $r -le 4; $r++) {
    Stap "4. Egypte: voorbereiding ronde $r"
    $uit = & $bash tools/prep_engine.sh egypte-toetanchamon 2>&1
    $uit | Select-String '^zin|gecontroleerd|TEKST' | % Line
    $fout = ($uit | Select-String 'TEKST FOUT.*egypte-toetanchamon (.+)$').Matches
    if (-not $fout) { break }
    if ($r -eq 4) { Stap 'Egypte: NOG TEKSTFOUTEN na 3 rondes, gestopt'; exit 1 }
    $nrs = ($fout[0].Groups[1].Value.Trim() -split '\s+') -join ','
    WachtOpRoutine
    & $O tools/engine_stem.py stories/egypte-toetanchamon --hergebruik --opnieuw $nrs --seed-extra (3000 * $r) 2>$null | Select -Last 2
}
Stap '4. Egypte: montage'
$mont = & $bash tools/montage_engine.sh egypte-toetanchamon "What Did People Actually Do When Tutankhamun Was King? | History for Sleep" thumbnail-gekozen.jpg 2>&1
$mont
$mt = $mont -join "`n"
if ($mt -match 'CONTROLE GOED' -and $mt -match 'TEKST GOED' -and $mt -match 'APPROVED') {
    Stap '4. Egypte: controles goed, uploaden en oude vervangen'
    python tools/vervang_video.py stories/egypte-toetanchamon --video stories/egypte-toetanchamon/video/egypte-toetanchamon-16mm.mp4 --publish-at 2026-11-14T20:00:00Z --thumbnail stories/egypte-toetanchamon/thumbnail-gekozen.jpg --soort oudheid --oud ctC36HRFIac --tags 'tutankhamun, ancient egypt, egypt history for sleep, valley of the kings, pharaoh'
} else { Stap 'Egypte: CONTROLES NIET GOED, niet geüpload' }
Stap 'ALLES KLAAR'
