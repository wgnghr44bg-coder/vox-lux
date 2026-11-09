# Nachttest zonder Claude (eigenaar 9 nov 2026: "uiteindelijk moet hij toch helemaal zelf draaien op de pc").
# Wacht tot Egypte (testvolgorde) en Tombstone (tombstone_herstel) klaar zijn; dan één voor één:
# 1 Gettysburg ombouwen uit het originele script, 2 nieuw script Salem 1692 (Wikipedia, boeken, YouTube),
# 3 als Gettysburg goed is: routine-lokaal tot en met beelden/beeldcontrole/thumbnail. Niets gaat online.
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
function Klaar($f, $p) { (Test-Path $f) -and (Select-String $f -Pattern $p -Quiet -Encoding unicode -ErrorAction SilentlyContinue) -or (Select-String $f -Pattern $p -Quiet -ErrorAction SilentlyContinue) }
Stap 'wachten op Egypte en Tombstone'
while (-not ((Klaar 'C:\Users\rane\testvolgorde.log' 'ALLES KLAAR|gestopt|NIET GOED, niet') -and (Klaar 'C:\Users\rane\tombstone-herstel.log' '=== .* KLAAR'))) { Start-Sleep 300 }
Stap '1. Gettysburg ombouwen zonder Claude (uit het originele script)'
if (Test-Path 'stories/gettysburg-1863/afbeeldingen') { Move-Item 'stories/gettysburg-1863/afbeeldingen' "stories/gettysburg-1863/afbeeldingen-vorigetest-$(Get-Date -Format yyyyMMddHHmm)" }
python tools/scriptgen/generator.py --map stories/gettysburg-1863 --test
$g = $LASTEXITCODE
Stap "1. klaar (exitcode $g)"
Stap '2. Nieuw script Salem 1692 zonder Claude'
python tools/scriptgen/generator.py --map stories/_test-nieuw --test
Stap "2. klaar (exitcode $LASTEXITCODE)"
if ($g -eq 0) {
    Stap '3. routine-lokaal op Gettysburg tot en met beelden'
    python tools/routine_lokaal.py --test-tot-beelden stories/gettysburg-1863
    Stap "3. klaar (exitcode $LASTEXITCODE)"
} else { Stap '3. overgeslagen: Gettysburg-script niet goed' }
python tools/dashboard_bijwerken.py
Stap 'NACHTTEST KLAAR'