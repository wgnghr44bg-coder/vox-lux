<#
.SYNOPSIS
  Maakt een What-If video op de pc: (optioneel) nieuwe animatie via OpenCode -> ondertitels -> MP4 renderen
  met geluidseffecten -> stem (Chatterbox, gratis) -> stem onder de video.

.EXAMPLE
  # bestaande animatie
  .\tools\threejs\make-whatif.ps1 -Html tools\threejs\never-stopped-raining.html

.EXAMPLE
  # nieuw verhaal: OpenCode schrijft eerst de animatie (kan geld kosten, het script vraagt eerst toestemming)
  .\tools\threejs\make-whatif.ps1 -Story "What if the Moon disappeared?"

.NOTES
  Draai vanuit PowerShell. Lukt starten niet: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  Uitkomst: <naam>\<naam>.mp4 (geluidseffecten) en <naam>\<naam>-voice.mp4 (met stem), naast de HTML.
#>
param(
  [string]$Html,              # bestaande animatie (.html)
  [string]$Story,             # nieuw verhaal, bv. "What if the Moon disappeared?"
  [string]$Model = "",        # OpenCode-model, bv. anthropic/claude-sonnet-4-5 (leeg = standaard van OpenCode)
  [string]$StemEnv = "",      # map van de stem-omgeving (met Scripts\python.exe); leeg = zelf zoeken
  [switch]$NoVoice,           # alleen video met geluidseffecten
  [switch]$NoGpu,             # renderen zonder videokaart (traag)
  [switch]$SkipRender,        # bestaande MP4 hergebruiken
  [int]$Fps = 30
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Set-Location $Root

function Step($text) { Write-Host "`n== $text ==" -ForegroundColor Cyan }
function Need($cmd, $hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "'$cmd' niet gevonden. $hint" }
}
function Run($exe, [string[]]$arguments) {
  & $exe @arguments
  if ($LASTEXITCODE -ne 0) { throw "Mislukt: $exe $($arguments -join ' ')" }
}

Need node   "Installeer Node.js: https://nodejs.org"
Need ffmpeg "Installeer ffmpeg en zet het in PATH."
Need python "Installeer Python: https://python.org"

# ---------- 1. Nieuw verhaal via OpenCode (optioneel) ----------
if ($Story) {
  $slug = ($Story.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
  if ($slug.StartsWith('what-if-')) { $slug = $slug.Substring(8) }
  if ($slug.Length -gt 40) { $slug = $slug.Substring(0, 40).Trim('-') }
  if (-not $Html) { $Html = "tools/threejs/$slug.html" }
  if (Test-Path $Html) {
    Write-Host "Animatie bestaat al: $Html (wordt niet opnieuw gemaakt)."
  } else {
    Step "Nieuwe animatie laten schrijven door OpenCode"
    Need opencode "Installeer OpenCode: https://opencode.ai"
    Write-Warning "OpenCode gebruikt een AI-model. Met een betaald model (bv. Claude via een API-sleutel) kost dit geld."
    $ok = Read-Host "Doorgaan? (j/n)"
    if ($ok -ne 'j') { Write-Host "Gestopt."; exit 1 }
    $prompt = (Get-Content "tools/threejs/whatif-prompt.md" -Raw -Encoding UTF8).Replace('{{STORY}}', $Story).Replace('{{FILE}}', ($Html -replace '\\', '/'))
    $oc = @('run')
    if ($Model) { $oc += @('-m', $Model) }
    $oc += $prompt
    Run opencode $oc
    if (-not (Test-Path $Html)) { throw "OpenCode heeft $Html niet gemaakt." }
  }
}
if (-not $Html) { throw "Geef -Html <pagina.html> of -Story 'What if ...?'." }
$Html = (Resolve-Path $Html).Path
$name = [IO.Path]::GetFileNameWithoutExtension($Html)
$dir = Join-Path (Split-Path $Html) $name
New-Item -ItemType Directory -Force $dir | Out-Null
$mp4 = Join-Path $dir "$name.mp4"

# ---------- 2. Ondertitels -> cues.tsv + script-cues.txt ----------
Step "Ondertitels uit de animatie halen"
Run python @("tools/threejs/make_cues.py", $Html, $dir)

# ---------- 3. Video renderen (met geluidseffecten) ----------
if ($SkipRender -and (Test-Path $mp4)) {
  Write-Host "Bestaande video wordt gebruikt: $mp4"
} else {
  Step "Playwright klaarzetten (alleen de eerste keer)"
  if (-not (Test-Path "tools/threejs/node_modules/playwright")) {
    Push-Location "tools/threejs"
    try {
      Run npm @('install', '--no-save', 'playwright@1.56.0')
      Run npx @('playwright', 'install', 'chromium')
    } finally { Pop-Location }
  }
  Step "Video renderen: $name.mp4"
  $render = @("tools/threejs/export_mp4.mjs", $Html, $mp4, "--fps", "$Fps")
  if (-not $NoGpu) { $render += "--gpu" }
  Run node $render
}

# ---------- 4. Stem maken en onder de video zetten ----------
if ($NoVoice) {
  Write-Host "`nKlaar (zonder stem): $mp4" -ForegroundColor Green
  try { Invoke-Item $dir } catch { }
  exit 0
}
Step "Stem maken (Chatterbox als bm_george, gratis)"
$candidates = @($StemEnv, (Join-Path $Root 'stem-env'), (Join-Path (Split-Path $Root) 'stem-env'), (Join-Path $HOME 'stem-env')) | Where-Object { $_ }
$stemPy = $candidates | ForEach-Object { Join-Path $_ 'Scripts\python.exe' } | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $stemPy) {
  Write-Warning "Stem-omgeving (stem-env) niet gevonden. Geef de map op met -StemEnv, zie tools\comfy\voice_test_local.py."
  Write-Host "Video zonder stem staat klaar: $mp4" -ForegroundColor Yellow
  exit 1
}
Run $stemPy @("tools/comfy/make_voice_local.py", $dir)

Step "Stem op de ondertitels zetten en onder de video mixen"
Run python @("tools/threejs/place_voice.py", $dir, "--video", $mp4)

$final = Join-Path $dir "$name-voice.mp4"
Write-Host "`nKlaar!" -ForegroundColor Green
Write-Host "  Met stem:            $final"
Write-Host "  Alleen geluidseffecten: $mp4"
try { Invoke-Item $dir } catch { }
