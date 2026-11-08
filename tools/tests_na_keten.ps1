# Wachter (eigenaar 8 nov 2026: "alles 1 voor 1 ivm geheugen pc"): pas na de keten Tombstone + Egypte de tests.
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:PYTHONUTF8 = 1
while (-not (Select-String 'C:\Users\rane\keten-tombstone-egypte.log' -Pattern 'KETEN KLAAR|gestopt|NIET GOED' -Quiet)) { Start-Sleep 300 }
"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') test beeldmodel" | Out-File -Append -Encoding utf8 'C:\Users\rane\tests-na-keten.log'
python tools/beeldcheck_vlmtest.py 30 *>> 'C:\Users\rane\tests-na-keten.log'
"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') test generator gettysburg" | Out-File -Append -Encoding utf8 'C:\Users\rane\tests-na-keten.log'
python tools/scriptgen/generator.py --map stories/gettysburg-1863 --test *>> 'C:\Users\rane\tests-na-keten.log'
"=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') TESTS KLAAR" | Out-File -Append -Encoding utf8 'C:\Users\rane\tests-na-keten.log'