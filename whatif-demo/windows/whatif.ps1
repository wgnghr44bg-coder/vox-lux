# IfScape3D - short commands on Windows (run from anywhere).
#
#   .\whatif.ps1 stills 45      6 test frames + overview (makes the voice first: xAI, about 1 cent)
#   .\whatif.ps1 render 45      full video after approval (voice already made) -> topics\<slug>\<slug>.mp4
#   .\whatif.ps1 check 45       is the mp4 there, playable, right size, picture + sound (CONTROLE GOED)
#   .\whatif.ps1 archive 45     source files -> C:\AI\ifscape3d-videos\<date>-<slug>\ (commit, no push)
#   .\whatif.ps1 preview street wind    one frame of a place + force, no topic, no costs
#
# Nothing is ever uploaded or published.

param(
  [Parameter(Mandatory = $true, Position = 0)][ValidateSet("stills", "render", "check", "archive", "preview")][string]$Cmd,
  [Parameter(Position = 1)][string]$Arg1,
  [Parameter(Position = 2)][string]$Arg2,
  [int]$Workers = 0,
  [string]$Times = ""
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$wd = Split-Path -Parent $PSScriptRoot          # whatif-demo
$repo = Split-Path -Parent $wd                   # vox-lux
$py = (Get-Command python -ErrorAction SilentlyContinue | Where-Object { $_.Source -notmatch 'WindowsApps' } | Select-Object -First 1).Source
if (-not $py) { $py = "py" }
if ($Workers -le 0) { $Workers = [Math]::Max(1, [Math]::Min(6, [Math]::Floor([Environment]::ProcessorCount / 3))) }

function Py { & $py @args; if ($LASTEXITCODE -ne 0) { throw "python $($args -join ' ') failed (exit $LASTEXITCODE)" } }
function TopicDir($nr) {
  $p = & $py -c "import sys; sys.path.insert(0, r'$wd'); from make_whatif import find_topic; print(find_topic($nr))"
  if ($LASTEXITCODE -ne 0 -or -not $p) { throw "Topic $nr not found (no topics\<slug>\scenario.js with number: $nr)" }
  return $p.Trim()
}

Push-Location $repo
try {
  switch ($Cmd) {
    "stills" {
      $a = @("$wd\make_whatif.py", $Arg1, "--stills")
      if ($Times) { $a += @("--times", $Times) }
      Py @a
      $img = Join-Path (TopicDir $Arg1) "stills\overzicht.jpg"
      Write-Host "Testbeelden: $img" -ForegroundColor Green
      Start-Process $img
    }
    "render" {
      $d = TopicDir $Arg1
      if (-not (Test-Path "$d\voice.mp3")) { throw "No voice.mp3 yet: run  .\whatif.ps1 stills $Arg1  first" }
      $t0 = Get-Date
      Py "$wd\make_whatif.py" $Arg1 --from render --workers $Workers
      Write-Host ("Klaar in {0:N0} min" -f ((Get-Date) - $t0).TotalMinutes) -ForegroundColor Green
    }
    "check" {
      $d = TopicDir $Arg1; $slug = Split-Path -Leaf $d; $mp4 = Join-Path $d "$slug.mp4"
      if (-not (Test-Path $mp4)) { throw "Not found: $mp4" }
      ffprobe -v error -show_entries "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size" -of default=nw=1 $mp4
      $bron = if (Test-Path "$d\check-bron.txt") { (Get-Content "$d\check-bron.txt").Trim() } else { "mix.wav" }
      Py "$repo\tools\check_video.py" $d "$slug.mp4" --stem voice.mp3 --bron $bron
      Write-Host "Video: $mp4" -ForegroundColor Green
      Start-Process $mp4
    }
    "archive" {
      $rest = @(); if ($Arg2) { $rest = $Arg2 -split ' ' }
      Py "$wd\archive_whatif.py" $Arg1 @rest
    }
    "preview" {
      Push-Location $wd
      node engine/render.mjs "preview:$($Arg1):$($Arg2)" stills 5 20 40
      Pop-Location
      Start-Process (Join-Path $wd "engine\previews\$Arg1-$Arg2\stills\still-20.jpg")
    }
  }
} catch {
  Write-Host "FOUT: $_" -ForegroundColor Red
  exit 1
} finally {
  Pop-Location
}
