Build a new cinematic low-poly Three.js "What If" animation for vertical video and save it as `{{FILE}}`.

Story: **{{STORY}}**

Use `tools/threejs/never-stopped-raining.html` as the reference. Read it first and keep the same structure and
features, so the existing tools (`make_cues.py`, `export_mp4.mjs`, `place_voice.py`) keep working:

- One self-contained HTML file. Three.js 0.170.0 from `https://cdn.jsdelivr.net/npm/three@0.170.0/` via an import map.
  WebGLRenderer with antialiasing, soft shadows, ACESFilmic tone mapping and sRGB output. MeshStandardMaterial,
  RoundedBoxGeometry and procedural low-poly geometry only (no downloaded models or images).
- Vertical 9:16 stage (1080x1920 composition), 60–90 seconds, deterministic: everything is a function of the time `T`.
- `const SCENES = [...]` at the top. Every scene has `id`, `when`, `what`, `start`, `end`, `env` (story values that blend
  toward the next scene), `shots` (camera keys `[time, [pos], [target], fov, up?]` or a `follow` shot) and
  `subtitles: [[start, end, 'text'], ...]`. Subtitles are short and dramatic, in English,
  and each one describes what is on screen at that moment.
- A title card at the start, a chapter label per scene, bold white subtitles with a dark outline in the lower middle.
- Preview controls: play/pause, replay, timeline scrubber, a **Sound** button and a **Voice** button (load an audio file).
  `H` or `?clean=1` hides the controls.
- Sound effects generated with Web Audio in a `buildSfx(ctx)` function, used both live and by
  `renderSoundtrack()` (OfflineAudioContext, returns a base64 16-bit WAV), exactly like the reference.
- Render mode `?render=1`: no animation loop; expose `window.renderAt(t)`, `window.renderSoundtrack` and set
  `window.renderReady = true`. Subtitle/title/chapter fades must come from `T` in render mode (no CSS transitions).
- End the story with a twist: a surprising but true fact that turns the story around (the owner likes this; e.g. the
  insects video: giant insects really lived 300 million years ago, when the air held more oxygen). The narration
  always announces it with its own line "Here's the twist:" (give it enough time) and then tells it.
- Multiple locations and time steps, a clear focal point in every shot, eased camera moves, a big environmental change
  that builds over the whole video, and a strong final wide shot.
- Keep it smooth on desktop and mobile: instanced meshes for repeated objects, few shadow casters, merged static geometry.

Make it gripping, not a lecture (owner on the insects video, 21 Oct 2026: "niet spannend, er gebeurt niks, het laat
niet zien wat voor impact het heeft"):
- Entertainment first, not a science lesson: fantasy and exaggeration are fine. Use a real fact only where it adds
  punch (the twist is the main place for one).
- Keep viewers watching: hook in the first 2 seconds, then a varied chain of different events (never the same kind of
  shot twice in a row), each one a small surprise, with a reason to wait for the next ("But that was only the start…").
- Every scene SHOWS a consequence happening on screen: things break, crash, collapse, flood, get eaten, people run.
  Facts are told while the viewer watches the damage, never instead of it.
- Escalate: each chapter is bigger and more dangerous than the last; the viewer's own house, street and city are at stake.
- Action beats every few seconds: impacts with a short camera shake, debris, dust, sudden movement, close calls.
- Short, punchy subtitles that raise the stakes ("Your car is next.") and a sound bed that builds tension
  (impact hits, rumbles, rising drone), still kept under the voice.

Lessons from earlier videos (the owner noticed every one of these, so they are requirements):
- Vehicles and animals face the way they move: check the model's long axis against the direction of travel.
- Nothing appears, shrinks or vanishes while it is on screen. People, cars and props only leave or appear on a camera cut.
- A cutaway opens on the shot change (the plane is already in place on the first frame), never as a sweep through the camera.
- The camera never passes through or grazes buildings, wires, trees or creatures; check every shot's path, not only its end.
- Flashes (lightning, explosions) rise and fall over a few frames; a one-frame jump to white looks like a glitch.
- Ending: after the last subtitle, hold the final shot about 3 s while the picture fades to dark and the sound fades
  to silence (`ENDING = { fade, sound }`, see never-stopped-raining.html). No title card at the end (the owner finds
  it ugly). The last subtitle ends before the fade starts.
- Subtitles must leave room for a calm voice: about 2.5 words per second, so a 10-word line needs at least 4 s.
- Sound effects stay under the narration; `place_voice.py` lowers them (default `--sfx-gain 0.45`) and ducks them
  while the voice speaks.

Clean, smooth picture (owner, 24 Oct 2026: "zorg dat alles vloeiend is zonder rare dingen in beeld"; this goes for every
video, Shorts and long videos alike):
- No sparkling dots, flicker or stripes on water or other big surfaces. Shade water with smooth normals computed from the
  waves (not per-pixel `dFdx`/`dFdy` normals), draw a surface from one side only, never let grid cells get smaller than a
  few centimetres, keep sun glints soft and fade them out with distance.
- Nothing should show through a surface by accident (half-transparent water that shows a body as stripes underneath).
- Particles (bubbles, specks, spray) stay small near the camera; never let a few huge blobs cover the picture.
- Bright light and flashes stay soft: no white blow-outs that hide the action.
- Not too dark without a reason (owner, 24 Oct 2026). Daylight is allowed and often better: a story does not have to play
  at night. Darkness is fine where it is logical (inside a whale, the deep sea, a power cut), but the viewer must still
  see what the line of narration is about (a lamp, a glow, a rim light on the subject). `check_frames.mjs` lists frames
  darker than 38 (out of 255): look at each one and only brighten it if the darkness is not logical for that moment or
  the subject cannot be seen.

Quality check (required, before you render and again on the finished MP4):
1. `node tools/threejs/check_frames.mjs <page.html> <folder> [--fade-from <s>]`: a frame every second, all console
   errors/warnings per time, contact sheets, and the list of frames that are too dark or too bright. Look at every sheet for glitches, popping, the camera inside or through objects, wrong facing, too dark /
   overexposed shots, sparkles or stripes, subjects that are not in frame. Fix and check again until it is clean.
2. For water, particle and fast shots also check a few frames 1/30 s apart (`--times 50,50.033,50.067`) for flicker.
3. After rendering: `node tools/threejs/check_frames.mjs --video <video.mp4> <folder>` and look at the sheets again.

Check that the page loads without errors in a browser before you finish. Do not change other files.
