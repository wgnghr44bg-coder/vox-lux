# Tombstone opnieuw vanaf de beweging (9 nov 2026): de eerste montage gebruikte het oude effectenbestand.
# Daarna controles, volume, 16mm, QC en (als alles goed is) uploaden en de oude 4RjjJh-j5a0 vervangen.
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
$O = 'C:/Users/rane/omnivoice-venv/Scripts/python.exe'
$M = 'stories/tombstone-1881'; $V = "$M/video"; $N = 'tombstone-1881'
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
$MDB = (Get-Content "$V/muziek-db.txt").Trim()
Stap 'beweging (goede effecten)'
python "$M/maak_motion.py"
python tools/motion.py "$V/$N.mp4" "$V/$N-motion.mp4" --plan "$M/motion.json" --effecten "$M/effecten.tsv" 2>&1 | Select -Last 2
Stap 'tikjes'
python tools/stil_tikjes.py $M "$V/$N-motion.mp4" "$V/$N-schoon.mp4" --muziek-db $MDB 2>&1 | Select -Last 2
Stap 'check'
$chk = python tools/check_video.py $M "video/$N-schoon.mp4" --muziek-db $MDB 2>&1; $chk | Select -Last 6
Stap 'tekst'
$tek = & $O tools/check_stem_tekst.py $M 2>&1 | Select-String 'zinnen gecontroleerd|TEKST' | % Line; $tek
Stap 'volume'
python tools/eind_volume.py "$V/$N-schoon.mp4" "$V/$N-14.mp4" 2>&1 | Select -Last 1
Stap '16mm'
python tools/film16.py "$V/$N-14.mp4" "$V/$N-16mm.mp4" 2>&1 | Select -Last 1
Stap 'qc'
$qc = python tools/qc_video.py $M "video/$N-16mm.mp4" --titel "How Did Ordinary People Really Live in Tombstone? | History for Sleep" --thumbnail "$M/thumbnail-gekozen.jpg" --beschrijving "$M/youtube-beschrijving.txt" --muziek-db $MDB --beelden ok --teksten ok --historisch ok --kijker ok 2>&1
$qc | Select-String 'Overall|ÔØî|❌|Problem' | % Line
$alles = (($chk + $tek + $qc) -join "`n")
if ($alles -match 'CONTROLE GOED' -and $alles -match 'TEKST GOED' -and $alles -match 'APPROVED') {
    Stap 'alles goed: uploaden en oude vervangen'
    python tools/vervang_video.py $M --video "$V/$N-16mm.mp4" --publish-at 2026-11-11T20:00:00Z --thumbnail "$M/thumbnail-gekozen.jpg" --soort mysterie --oud 4RjjJh-j5a0 --tags 'tombstone, tombstone arizona, wyatt earp, ok corral, wild west history'
} else { Stap 'CONTROLES NIET GOED: niet geüpload (de oude versie blijft staan)' }
Stap 'KLAAR'
