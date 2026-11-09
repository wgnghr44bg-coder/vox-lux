Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
Stap '1. TEST Gettysburg ombouwen zonder Claude (uit het originele script)'
if (Test-Path 'stories/gettysburg-1863/afbeeldingen') { Move-Item 'stories/gettysburg-1863/afbeeldingen' "stories/gettysburg-1863/afbeeldingen-vorigetest-$(Get-Date -Format yyyyMMddHHmm)" }
python tools/scriptgen/generator.py --map stories/gettysburg-1863 --test
$g = $LASTEXITCODE
Stap "1. klaar (exitcode $g)"
Stap '2. TEST nieuw script Salem 1692 zonder Claude'
python tools/scriptgen/generator.py --map stories/_test-nieuw --test
Stap "2. klaar (exitcode $LASTEXITCODE)"
if ($g -eq 0) {
    Stap '3. TEST routine-lokaal op Gettysburg tot en met beelden'
    python tools/routine_lokaal.py --test-tot-beelden stories/gettysburg-1863
    Stap "3. klaar (exitcode $LASTEXITCODE)"
} else { Stap '3. overgeslagen: Gettysburg-script niet goed' }
Stap 'TEST KLAAR'