# IfScape3D - short commands on Windows (run from anywhere).
#
#   .\whatif.ps1 "What if the Sun disappeared?"
#       EVERYTHING in one go: Grok (xAI) writes and checks the scenario -> voice + 6 test frames -> you answer j
#       (or type what to change) -> full video with sound -> check -> source files archived.
#       After setup.ps1 also just:  whatif "..."      Costs (xAI): about 5-10 cents per Short.
#
# Single steps (topic number from onderwerpen.md):
#   .\whatif.ps1 stills 45      6 test frames + overview (makes the voice first: xAI, about 1 cent)
#   .\whatif.ps1 render 45      full video after approval (voice already made) -> topics\<slug>\<slug>.mp4
#   .\whatif.ps1 check 45       is the mp4 there, playable, right size, picture + sound (CONTROLE GOED)
#   .\whatif.ps1 archive 45     source files -> C:\AI\ifscape3d-videos\<date>-<slug>\ (commit, no push)
#   .\whatif.ps1 preview street wind    one frame of a place + force, no topic, no costs
#   .\whatif.ps1 aanpassen 12 "the water must reach the houses"   Grok changes topic 12, new test frames, then the same steps
#   .\whatif.ps1 camera 12 "more close-ups of the cars"   only the director chooses the camera again (with a wish), then the same steps
#   .\whatif.ps1 camera 12 "langzaam inzoomen bij de golf, eindig met een kraan omhoog"   camera moves (push, zoom, drone, orbit, crane ...)
#
# Nothing is ever uploaded or published.

param(
  [Parameter(Position = 0)][string]$Cmd = "",
  [Parameter(Position = 1)][string]$Arg1,
  [Parameter(Position = 2)][string]$Arg2,
  [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest,
  [int]$Workers = 0,
  [string]$Times = ""
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false } catch {}   # Python prints UTF-8
$steps = @("stills", "render", "check", "archive", "preview")
$fixNr = $null
$camOnly = $false
if ($Cmd -eq "aanpassen" -or $Cmd -eq "fix" -or $Cmd -eq "camera") {   # whatif aanpassen 12 "wat er anders moet" / whatif camera 12 "wens"
  $camOnly = ($Cmd -eq "camera")
  $fixNr = $Arg1; $fixText = (@($Arg2) + @($Rest) | Where-Object { $_ }) -join " "
  if (-not $fixText -and -not $camOnly) { $fixText = Read-Host "Wat moet er anders aan onderwerp $fixNr" }
  $Cmd = "make"
} elseif ($steps -notcontains $Cmd) {                             # not a step: it is a topic (or nothing yet)
  $Arg1 = (@($Cmd, $Arg1, $Arg2) + @($Rest) | Where-Object { $_ }) -join " "
  $Cmd = "make"
}
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

function Topic {   # make_topic.py: Grok writes / adjusts the scenario; returns the topic number
  $ErrorActionPreference = "Continue"          # Python warnings on stderr must not stop PowerShell 5
  $lines = @(& $py "$wd\make_topic.py" @args 2>&1 | ForEach-Object { $t = "$_"; Write-Host $t; $t })
  $code = $LASTEXITCODE
  $num = ($lines | Select-String '^NUMBER=(\d+)' | Select-Object -Last 1)
  if ($code -eq 3) { throw "Dit onderwerp is al gemaakt (zie onderwerpen.md)" }
  if ($code -ne 0) { throw "Het scenario lukte niet (zie de meldingen hierboven)" }
  if ($num) { return $num.Matches[0].Groups[1].Value }
}

Push-Location $repo
try {
  switch ($Cmd) {
    "make" {
      if ($fixNr -and $camOnly) {
        $nr = $fixNr
        Write-Host "1/5 De regisseur kiest de camera opnieuw voor onderwerp $nr $(if ($fixText) { ": $fixText" })" -ForegroundColor Cyan
        $da = @("$wd\director.py", $nr); if ($fixText) { $da += @("--wish", $fixText) }   # PowerShell 5 drops empty arguments
        Py @da
      } elseif ($fixNr) {
        $nr = $fixNr
        Write-Host "1/5 Grok past onderwerp $nr aan: $fixText" -ForegroundColor Cyan
        Topic --fix $nr $fixText | Out-Null
      } else {
        $topic = $Arg1
        if (-not $topic) { $topic = Read-Host "Onderwerp (bijv. What if the Sun disappeared?)" }
        if (-not $topic) { throw "Geen onderwerp" }
        Write-Host "1/5 Grok schrijft en controleert het scenario voor: $topic" -ForegroundColor Cyan
        $nr = Topic $topic
      }
      $d = TopicDir $nr; $slug = Split-Path -Leaf $d
      Write-Host "Onderwerp $nr -> topics\$slug" -ForegroundColor Green

      while ($true) {
        Write-Host "2/5 Stem + 6 testbeelden" -ForegroundColor Cyan
        Py "$wd\make_whatif.py" $nr --stills
        Start-Process (Join-Path $d "stills\overzicht.jpg")
        $ans = (Read-Host "Goed? [Enter/j = video maken, n = stoppen, of typ wat er anders moet]").Trim()
        if ($ans -eq "" -or $ans -match '^(j|ja|y|yes|goed|ok)$') { break }
        if ($ans -match '^(n|nee|no|stop)$') { Write-Host "Gestopt. Later verder:  whatif render $nr"; return }
        Write-Host "Grok past het scenario aan ..." -ForegroundColor Cyan
        try { Topic --fix $nr $ans | Out-Null } catch { Write-Host "$_ (vorige versie blijft staan)" -ForegroundColor Yellow }
      }

      Write-Host "3/5 Video + geluid (duurt 10-30 min)" -ForegroundColor Cyan
      $t0 = Get-Date
      Py "$wd\make_whatif.py" $nr --from render --workers $Workers
      Write-Host ("   klaar in {0:N0} min" -f ((Get-Date) - $t0).TotalMinutes)
      Write-Host "4/5 Controle" -ForegroundColor Cyan
      $mp4 = Join-Path $d "$slug.mp4"
      ffprobe -v error -show_entries "stream=codec_type,width,height:format=duration" -of default=nw=1 $mp4
      $bron = if (Test-Path "$d\check-bron.txt") { (Get-Content "$d\check-bron.txt").Trim() } else { "mix.wav" }
      & $py "$repo\tools\check_video.py" $d "$slug.mp4" --stem voice.mp3 --bron $bron
      $ok = ($LASTEXITCODE -eq 0)
      Write-Host "5/5 Bronbestanden bewaren" -ForegroundColor Cyan
      Py "$wd\archive_whatif.py" $nr --force
      Push-Location $repo
      git add "whatif-demo/topics/$slug" whatif-demo/onderwerpen.md
      git commit -q -m "whatif: $slug"
      Pop-Location
      Write-Host ""
      if ($ok) { Write-Host "KLAAR: $mp4" -ForegroundColor Green } else { Write-Host "Video gemaakt, maar de controle vond iets (zie hierboven): $mp4" -ForegroundColor Yellow }
      $up = Get-Content (Join-Path $d "upload.json") -Raw | ConvertFrom-Json
      Write-Host "Titel  : $($up.title)"
      if ($up.tiktok) { Write-Host "TikTok : $($up.tiktok)" }
      Write-Host "Niets geupload. Dat doe je zelf."
      Write-Host "Iets anders willen?  whatif aanpassen $nr `"wat er anders moet`""
      Start-Process $mp4
    }
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
