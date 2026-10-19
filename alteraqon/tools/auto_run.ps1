# Alteraqon nachtrun: maakt elke nacht zelf de video's en zet ze op het schema.
# Wordt gestart door de Windows-taak "Alteraqon-Nachtrun" (zie install_nachtrun.ps1).
# Instellingen van deze pc staan in %USERPROFILE%\alteraqon-auto.json (NIET in git):
#   {"repo": "...\\vox-lux-alteraqon", "comfy_start": "...\\run_nvidia_gpu.bat", "opencode": "...\\opencode.exe",
#    "videos": "C:\\Users\\rane\\Videos\\alteraqon"}
# Elke video krijgt een eigen, verse OpenCode-sessie (opencode run). Rapport: <videos>\rapport-<datum>.txt,
# te lezen op de iPhone via de kijkserver (http://<tailscale-ip>:8765/).
$ErrorActionPreference = 'Continue'
$cfg = Get-Content (Join-Path $env:USERPROFILE 'alteraqon-auto.json') -Raw | ConvertFrom-Json
$videos = if ($cfg.videos) { $cfg.videos } else { 'C:\Users\rane\Videos\alteraqon' }
# OpenCode-desktop zet de CLI in een map per versie (…\cli\2.0.30-x64\); na een update de nieuwste nemen
if (-not (Test-Path $cfg.opencode)) {
    $new = Get-ChildItem (Join-Path $env:APPDATA 'ai.opencode.desktop\cli') -Recurse -Filter 'opencode-cli.exe' -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($new) { $cfg.opencode = $new.FullName }
}
$date = Get-Date -Format 'yyyy-MM-dd'
$logDir = Join-Path $videos 'logs'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir "nachtrun-$date.log"
$rapport = Join-Path $videos "rapport-$date.txt"
function Log($m) { "$(Get-Date -Format 'HH:mm:ss') $m" | Out-File $log -Append -Encoding utf8 }
function Rapport($m) { $m | Out-File $rapport -Append -Encoding utf8 }

# niet twee runs tegelijk
$lock = Join-Path $env:TEMP 'alteraqon-nachtrun.lock'
if (Test-Path $lock) {
    $old = Get-Content $lock
    if ($old -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) { Log "Vorige run loopt nog (pid $old) - overgeslagen."; exit 0 }
}
$PID | Set-Content $lock

try {
    Set-Location $cfg.repo
    Log "Start nachtrun"
    git pull origin alteraqon 2>&1 | ForEach-Object { Log "git: $_" }

    # ComfyUI
    function ComfyUp { try { Invoke-WebRequest 'http://127.0.0.1:8188/queue' -UseBasicParsing -TimeoutSec 5 | Out-Null; $true } catch { $false } }
    if (-not (ComfyUp)) {
        Log "ComfyUI starten: $($cfg.comfy_start)"
        Start-Process -FilePath $cfg.comfy_start -WorkingDirectory (Split-Path $cfg.comfy_start) -WindowStyle Minimized
        for ($i = 0; $i -lt 60 -and -not (ComfyUp); $i++) { Start-Sleep 5 }
    }
    if (-not (ComfyUp)) {
        Log "FOUT: ComfyUI reageert niet"
        Rapport "NACHTRUN $date MISLUKT: ComfyUI start niet ($($cfg.comfy_start)). Er is vannacht niets gemaakt."
        exit 1
    }

    # kijkserver (alleen op het Tailscale-IP)
    $ip = (& tailscale ip -4 | Select-Object -First 1)
    if ($ip) {
        $ip = $ip.Trim()
        $ok = $false
        try { $ok = (Invoke-WebRequest "http://${ip}:8765/" -UseBasicParsing -TimeoutSec 5).Content -match "serve-v2" } catch {}   # oude versie? dan herstarten
        if (-not $ok) {
            Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
            Start-Process python -ArgumentList 'alteraqon\tools\serve_videos.py', $ip, '8765', $videos -WindowStyle Hidden
            Log "Kijkserver gestart op ${ip}:8765"
        }
    } else { Log "Tailscale-IP niet gevonden (kijkserver niet gestart)" }

    # kanalen: Alteraqon (deze repo, map alteraqon/) en IfScape3D (repo ifscape3d-videos naast deze repo: echte 3D-scènes
    # met de gedownloade modellen; regels in die repo, AGENTS.md "NACHTRUN"; eigenaar akkoord 19 okt 2026)
    $ifs = if ($cfg.ifscape_repo) { $cfg.ifscape_repo } else { Join-Path (Split-Path $cfg.repo) 'ifscape3d-videos' }
    $chan = @(
        @{ naam = 'Alteraqon'; repo = $cfg.repo; branch = 'alteraqon'; plan = 'alteraqon';
           regels = 'Lees AGENTS.md (vooral 0a, 10 en 11) en volg alle regels. Doe alle stappen tot en met 8 en daarna stap 10 (automatisch inplannen, alleen als alles klopt).' },
        @{ naam = 'IfScape3D'; repo = $ifs; branch = 'main'; plan = $ifs;
           regels = 'Lees AGENTS.md, vooral het hoofdstuk NACHTRUN bovenaan, en volg het van begin tot eind (alle controles, geen STOP-momenten, inplannen alleen als alles klopt).' }
    )
    if (-not (Test-Path (Join-Path $ifs 'AGENTS.md'))) { Log "IfScape3D-repo niet gevonden ($ifs) - IfScape3D overgeslagen"; $chan = @($chan[0]) }
    $plans = @{}
    foreach ($c in $chan) {
        if ($c.repo -ne $cfg.repo) { Push-Location $c.repo; git pull origin $c.branch 2>&1 | ForEach-Object { Log "git $($c.naam): $_" }; Pop-Location }
        $plans[$c.naam] = python alteraqon\tools\auto_plan.py $c.plan | ConvertFrom-Json
        $pl = $plans[$c.naam]
        Log "Plan $($c.naam): $($pl.shorts) Shorts, $($pl.long) lange video (al ingepland: $($pl.shorts_ingepland) Shorts, $($pl.long_ingepland) lang)"
    }
    # Shorts van beide kanalen om en om, daarna de lange video's
    $jobs = @()
    for ($i = 1; $i -le 3; $i++) {
        foreach ($c in $chan) {
            if ($i -le $plans[$c.naam].shorts) { $jobs += @{ c = $c; wat = "Maak een $($c.naam)-short (nr $i van $($plans[$c.naam].shorts) vannacht)" } }
        }
    }
    foreach ($c in $chan) { if ($plans[$c.naam].long -eq 1) { $jobs += @{ c = $c; wat = "Maak een lange $($c.naam)-video" } } }
    if (-not $jobs) { Rapport "NACHTRUN ${date}: wachtrij is vol genoeg, niets nieuws gemaakt."; exit 0 }

    $n = 0
    foreach ($job in $jobs) {
        $n++; $c = $job.c
        Push-Location $c.repo; git pull origin $c.branch 2>&1 | ForEach-Object { Log "git $($c.naam): $_" }; Pop-Location
        $prompt = @"
NACHTRUN (automatisch gestart; de eigenaar slaapt en kan NIETS beantwoorden - beslis alles zelf, stel geen vragen).
$($c.regels)
Opdracht: $($job.wat). Kies zelf het onderwerp (anders dan alle bestaande, ook die van eerder vannacht).
Voeg aan het eind je korte rapport ONDERAAN toe aan $rapport (nooit overschrijven, UTF-8), begin met de kanaalnaam.
"@
        $out = Join-Path $logDir "nachtrun-$date-$n.log"
        Log "Start opdracht ${n}: $($job.wat)"
        $p = Start-Process -FilePath $cfg.opencode -ArgumentList 'run', ('"' + (($prompt -replace "\r?\n", ' ') -replace '"', '\"') + '"') `
            -WorkingDirectory $c.repo -RedirectStandardOutput $out -RedirectStandardError "$out.err" -WindowStyle Hidden -PassThru
        $uren = if ($job.wat -like '*lange*') { 8 } else { 4 }      # lange video (IfScape3D: 3 hoofdstukken) mag langer
        if (-not $p.WaitForExit($uren * 3600 * 1000)) {
            Log "Opdracht $n duurt langer dan $uren uur - afgebroken"
            Stop-Process -Id $p.Id -Force
            Rapport "Opdracht $n ($($job.wat)): afgebroken na $uren uur. Log: logs/nachtrun-$date-$n.log"
        } else { Log "Opdracht $n klaar (exitcode $($p.ExitCode))" }
    }
    Log "Nachtrun klaar"
} finally {
    Remove-Item $lock -ErrorAction SilentlyContinue
}
