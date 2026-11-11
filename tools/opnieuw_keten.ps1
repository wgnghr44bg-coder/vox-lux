# Alle geplande video's opnieuw maken volgens de nieuwe regels (eigenaar 11 nov 2026: nieuwe stem en toon, "alle video's
# moeten opnieuw"), één voor één op datum, elk met stories/PROMPT-OPNIEUW.md. Log: C:\Users\rane\opnieuw-keten.log
# Een video die al "opnieuw gemaakt" in ROUTINE-LOG.md heeft, wordt overgeslagen (dus de keten kan veilig opnieuw starten).
Set-Location 'C:\Users\rane\Documents\vox-lux-routine'
$env:CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS = '0'
$volgorde = @('babylon-600-vc', 'tombstone-1881', 'gettysburg-1863', 'dallas-1963', 'egypte-toetanchamon',
              'scott-antarctica-1912', 'pearl-harbor-1941', 'rome-44-vc', 'zwarte-dood-1348')
function Stap($t) { "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm') $t" }
while (Get-CimInstance Win32_Process | ? { $_.CommandLine -like '*PROMPT-ROUTINE-PC*' }) { Stap 'routine nog bezig, wachten'; Start-Sleep 600 }
foreach ($m in $volgorde) {
    git checkout -q main; git pull -q --rebase --autostash
    if (Select-String stories/ROUTINE-LOG.md -Pattern "$m`: opnieuw gemaakt" -Quiet) { Stap "$m al opnieuw gemaakt, overslaan"; continue }
    Stap "$m opnieuw maken (nieuwe toon, eigen stem)"
    & 'C:\Users\rane\.local\bin\claude.exe' -p "Lees stories/PROMPT-OPNIEUW.md op main en voer het helemaal uit voor stories/$m." --dangerously-skip-permissions
    Stap "$m klaar (exitcode $LASTEXITCODE)"
}
Stap 'KETEN KLAAR'
