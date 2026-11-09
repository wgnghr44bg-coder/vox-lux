# Na de test (9 nov): Gettysburg opnieuw ombouwen met de verbeterde generator (bijvullen tot 85+ feitjes), dan beelden.
$env:PYTHONUTF8 = 1
while (Get-Process -Id 7740 -ErrorAction SilentlyContinue) { Start-Sleep 60 }
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
git pull -q --rebase --autostash
Stap '1b. TEST Gettysburg opnieuw ombouwen (generator vult nu bij tot 85+ feitjes)'
python tools/scriptgen/generator.py --map stories/gettysburg-1863 --test
$g = $LASTEXITCODE
Stap "1b. klaar (exitcode $g)"
if ($g -eq 0) {
    Stap '3. TEST routine-lokaal op Gettysburg tot en met beelden'
    python tools/routine_lokaal.py --test-tot-beelden stories/gettysburg-1863
    Stap "3. klaar (exitcode $LASTEXITCODE)"
} else { Stap '3. overgeslagen: Gettysburg-script niet goed' }
Stap 'TEST KLAAR'