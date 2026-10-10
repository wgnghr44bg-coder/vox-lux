# IfScape3D - installation from scratch on a Windows pc (phase 1-3).
#
# Run in PowerShell (no admin needed; winget asks for permission itself when a program needs it):
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#   powershell -ExecutionPolicy Bypass -File setup.ps1 -CheckOnly        # only the overview, installs nothing
#
# Safe to run again: it checks first, installs only what is missing, never deletes or overwrites
# files, and never uploads anything.

param(
  [string]$Root = "C:\AI",
  [string]$Branch = "claude/whatif-machine",
  [switch]$CheckOnly,
  [switch]$Yes
)

$ErrorActionPreference = "Stop"
$EngineUrl  = "https://github.com/wgnghr44bg-coder/vox-lux.git"
$ArchiveUrl = "https://github.com/wgnghr44bg-coder/ifscape3d-videos.git"
$PlaywrightVersion = "1.56.1"     # same version as the cloud sessions
$PyPackages = @("numpy", "scipy", "requests", "imageio-ffmpeg", "pillow", "fonttools", "tzdata")

function Say($text, $color = "Gray") { Write-Host $text -ForegroundColor $color }
function Step($text) { Write-Host ""; Write-Host "=== $text ===" -ForegroundColor Cyan }
function Ask($question) {
  if ($Yes) { return $true }
  $a = Read-Host "$question [j/n]"
  return ($a -match '^(j|y)')
}
function RefreshPath {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Find($exe) {
  $c = Get-Command $exe -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1
  if ($c) { return $c.Source } else { return $null }
}
function Version($exe, $arg = "--version") {
  try { return ((& $exe $arg 2>&1) | Select-Object -First 1).ToString().Trim() } catch { return "?" }
}
function PythonExe {
  $p = Find "python"
  if ($p) { return $p }
  $py = Find "py"
  if ($py) { try { return (& $py -3 -c "import sys; print(sys.executable)").Trim() } catch {} }
  return $null
}

# ---------------------------------------------------------------- phase 1: the pc
Step "Fase 1 - Overzicht van deze pc"
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Say ("Windows : {0} (build {1})" -f $os.Caption, $os.BuildNumber)
Say ("CPU     : {0} ({1} kernen / {2} threads)" -f $cpu.Name.Trim(), $cpu.NumberOfCores, $cpu.NumberOfLogicalProcessors)
Say ("RAM     : {0:N0} GB" -f ($cs.TotalPhysicalMemory / 1GB))
$drive = Split-Path -Qualifier $Root
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$drive'" -ErrorAction SilentlyContinue
if ($disk) { Say ("Schijf {0}: {1:N0} GB vrij" -f $drive, ($disk.FreeSpace / 1GB)) }
foreach ($g in Get-CimInstance Win32_VideoController) {
  $vram = if ($g.AdapterRAM -gt 0) { "{0:N1} GB" -f ($g.AdapterRAM / 1GB) } else { "?" }
  Say ("GPU     : {0} (driver {1}, geheugen {2}; Windows meldt max. 4 GB)" -f $g.Name, $g.DriverVersion, $vram)
}
$cores = [int]$cpu.NumberOfLogicalProcessors
$workers = [Math]::Max(1, [Math]::Min(6, [Math]::Floor($cores / 3)))
Say "Advies render-workers: $workers (make_whatif.py --workers $workers)"

$tools = [ordered]@{
  "Git"     = @{ exe = "git";    winget = "Git.Git" }
  "Node.js" = @{ exe = "node";   winget = "OpenJS.NodeJS.LTS" }
  "Python"  = @{ exe = "python"; winget = "Python.Python.3.12" }
  "FFmpeg"  = @{ exe = "ffmpeg"; winget = "Gyan.FFmpeg" }
}
function Report {
  $missing = @()
  foreach ($name in $tools.Keys) {
    $t = $tools[$name]
    $path = if ($t.exe -eq "python") { PythonExe } else { Find $t.exe }
    if ($path) {
      $v = if ($t.exe -eq "ffmpeg") { Version $path "-version" } else { Version $path }
      Say ("  OK       {0,-8} {1}" -f $name, $v) Green
    } else {
      Say ("  ONTBREEKT {0,-8} (winget: {1})" -f $name, $t.winget) Yellow
      $missing += $name
    }
  }
  $ffprobe = Find "ffprobe"
  if (-not $ffprobe -and (Find "ffmpeg")) { Say "  ONTBREEKT ffprobe (hoort bij FFmpeg; installeer Gyan.FFmpeg)" Yellow; $missing += "FFmpeg" }
  $pwDir = Join-Path $env:LOCALAPPDATA "ms-playwright"
  if (Test-Path (Join-Path $pwDir "chromium-*")) { Say "  OK       Chromium (Playwright, $pwDir)" Green }
  else { Say "  ONTBREEKT Chromium voor Playwright (wordt in fase 3 geinstalleerd)" Yellow }
  $unique = @($missing | Select-Object -Unique)
  return ,$unique
}
Say ""
Say "Software:"
$missing = Report
if ($CheckOnly) { Say ""; Say "Alleen controle (-CheckOnly): niets geinstalleerd."; exit 0 }

if ($missing.Count -gt 0) {
  if (-not (Find "winget")) {
    Say "winget ontbreekt. Installeer 'App Installer' uit de Microsoft Store en start dit script opnieuw." Red
    exit 1
  }
  Say ""
  Say ("Ontbreekt: {0}" -f ($missing -join ", ")) Yellow
  Say "Installatie via winget (officiele pakketten, gratis). Windows kan per programma om toestemming (UAC) vragen: klik dan Ja."
  if (-not (Ask "Ontbrekende programma's nu installeren?")) { Say "Gestopt op verzoek. Niets geinstalleerd."; exit 0 }
  foreach ($name in $missing) {
    $id = $tools[$name].winget
    Say "winget install $id ..." Cyan
    winget install --id $id -e --source winget --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { Say "Installatie van $name gaf code $LASTEXITCODE. Rond een eventueel venster af en start dit script opnieuw." Red; exit 1 }
  }
  RefreshPath
  Say ""
  Say "Na installatie:"
  $missing = Report
  if ($missing.Count -gt 0) {
    Say "Nog niet gevonden: $($missing -join ', '). Sluit PowerShell, open een nieuw venster en start dit script opnieuw." Red
    exit 1
  }
}

# ---------------------------------------------------------------- phase 2: the projects
Step "Fase 2 - Projecten in $Root"
New-Item -ItemType Directory -Force -Path $Root | Out-Null
$engine  = Join-Path $Root "vox-lux"
$archive = Join-Path $Root "ifscape3d-videos"

if (-not (Test-Path (Join-Path $engine ".git"))) {
  if (Test-Path $engine) { Say "$engine bestaat al maar is geen git-map. Niets overschreven; hernoem of verwijder hem zelf." Red; exit 1 }
  $remote = git ls-remote --heads $EngineUrl $Branch
  if (-not $remote) { Say "Branch $Branch bestaat niet (meer) op GitHub. Kies er een met -Branch." Red; git ls-remote --heads $EngineUrl; exit 1 }
  Say "Clone engine ($Branch) ..."
  git clone --branch $Branch $EngineUrl $engine
  if ($LASTEXITCODE -ne 0) { Say "Clone mislukt." Red; exit 1 }
} else {
  Say "Engine staat er al: $engine (niet overschreven)"
  git -C $engine fetch origin --prune
  $cur = (git -C $engine rev-parse --abbrev-ref HEAD).Trim()
  $dirty = git -C $engine status --porcelain
  Say "  huidige branch: $cur"
  if ($dirty) { Say "  let op: er zijn lokale wijzigingen; niets bijgewerkt." Yellow }
  elseif ($cur -eq $Branch) { git -C $engine pull --ff-only origin $Branch }
}
if (-not (Test-Path (Join-Path $archive ".git"))) {
  if (Test-Path $archive) { Say "$archive bestaat al maar is geen git-map. Niets overschreven." Red; exit 1 }
  Say "Clone videoarchief ..."
  git clone $ArchiveUrl $archive
} else {
  Say "Videoarchief staat er al: $archive (niet overschreven)"
  if (-not (git -C $archive status --porcelain)) { git -C $archive pull --ff-only }
}

# ---------------------------------------------------------------- phase 3: dependencies
Step "Fase 3 - Afhankelijkheden"
$wd = Join-Path $engine "whatif-demo"
Push-Location $wd
try {
  Say "npm ci (three.js, lettertypes) ..."
  npm ci --no-audit --no-fund
  if ($LASTEXITCODE -ne 0) { throw "npm ci mislukt" }
  $pwOk = $false
  try { $pwOk = ((npm ls -g playwright 2>$null) -match "playwright@$PlaywrightVersion") } catch {}
  if (-not $pwOk) {
    Say "Playwright $PlaywrightVersion (globaal) ..."
    npm install -g "playwright@$PlaywrightVersion" --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw "Playwright installeren mislukt" }
  }
  Say "Chromium voor Playwright (eenmalig ~150 MB) ..."
  npx -y "playwright@$PlaywrightVersion" install chromium
  if ($LASTEXITCODE -ne 0) { throw "Chromium installeren mislukt" }

  $py = PythonExe
  Say "Python-pakketten: $($PyPackages -join ', ') ..."
  & $py -m pip install --user --quiet --disable-pip-version-check @PyPackages
  if ($LASTEXITCODE -ne 0) { throw "pip install mislukt" }

  # Codex CLI: writes the scenario when you run  whatif "What if ..."  (uses your ChatGPT plan, no extra service)
  if (-not (Find "codex")) {
    if (Ask "Codex CLI installeren (npm, gratis; werkt met je ChatGPT-account)?") {
      npm install -g @openai/codex --no-audit --no-fund
      if ($LASTEXITCODE -ne 0) { throw "Codex CLI installeren mislukt" }
      RefreshPath
    }
  }
  if (Find "codex") {
    $logged = $false
    try { & codex login status *> $null; $logged = ($LASTEXITCODE -eq 0) } catch {}
    if (-not $logged) {
      Say "Codex is nog niet ingelogd. Er opent zo een browser: log in met je ChatGPT-account." Yellow
      if (Ask "Nu inloggen bij Codex?") { codex login }
    } else { Say "Codex CLI: ingelogd" Green }
  }

  # the command  whatif  in every new PowerShell window
  $ps1 = Join-Path $wd "windows\whatif.ps1"
  $fn = "function whatif { & '$ps1' @args }"
  $has = (Test-Path $PROFILE) -and (Select-String -Path $PROFILE -SimpleMatch $fn -Quiet)
  if (-not $has -and (Ask "Commando 'whatif' toevoegen aan PowerShell (overal te gebruiken)?")) {
    $pol = Get-ExecutionPolicy -Scope CurrentUser
    if ($pol -eq "Undefined" -or $pol -eq "Restricted") {
      Say "PowerShell mag nu lokale scripts draaien (CurrentUser: RemoteSigned)."
      Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
    }
    if (-not (Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force | Out-Null }
    Add-Content -Path $PROFILE -Value $fn
    Say "Toegevoegd aan $PROFILE" Green
  }

  # keys: local .env file, never in git (whatif-demo/.gitignore)
  $envFile = Join-Path $wd ".env"
  if (-not (Test-Path $envFile)) { Copy-Item (Join-Path $wd ".env.example") $envFile; Say "Aangemaakt: $envFile (staat niet in git)" }
  $hasKey = Select-String -Path $envFile -Pattern '^\s*XAI_API_KEY\s*=\s*\S' -Quiet
  if (-not $hasKey) {
    Say ""
    Say "De stem (xAI 'atlas') heeft een xAI API-sleutel nodig: https://console.x.ai -> API Keys." Yellow
    Say "Kosten: betaald per gebruik, ongeveer 1 cent per Short-stem. Zonder sleutel werkt alles behalve de stem." Yellow
    $sec = Read-Host "Plak je XAI_API_KEY (Enter = later)" -AsSecureString
    $key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
    if ($key) {
      $lines = Get-Content $envFile | Where-Object { $_ -notmatch '^\s*XAI_API_KEY\s*=' }
      Set-Content -Path $envFile -Value ($lines + "XAI_API_KEY=$key") -Encoding ASCII
      Say "Sleutel opgeslagen in $envFile" Green
    } else { Say "Later invullen in $envFile" }
  }

  # ------------------------------------------------------------ self-test without costs
  Step "Zelftest - 1 testbeeld van een bestaande plek (geen API-kosten)"
  node engine/render.mjs "preview:street:wind" stills 5
  $img = Join-Path $wd "engine\previews\street-wind\stills\still-5.jpg"
  if ((Test-Path $img) -and ((Get-Item $img).Length -gt 20000)) { Say "Renderer werkt: $img" Green }
  else { throw "Zelftest mislukt: geen testbeeld ($img)" }
  & $py -c "import imageio_ffmpeg, numpy, scipy, requests; print('Python OK')"
} catch {
  Say "FOUT: $_" Red
  Pop-Location
  exit 1
}
Pop-Location

Step "Klaar"
Say "Engine : $engine  (branch $(git -C $engine rev-parse --abbrev-ref HEAD))"
Say "Archief: $archive"
Say "Volgende stap: open een NIEUW PowerShell-venster en typ bijvoorbeeld:"
Say '  whatif "What if the Sun disappeared?"' Green
Say "Dat doet alles: scenario (Codex), stem, 6 testbeelden, jouw akkoord, video met geluid, controle, archief."
Say "Handleiding: $wd\windows\HANDLEIDING.md"
