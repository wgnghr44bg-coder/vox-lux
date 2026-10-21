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
  `subtitles: [[start, end, 'text'], ...]`. Subtitles are short, dramatic and scientifically sensible, in English,
  and each one describes what is on screen at that moment.
- A title card at the start, a chapter label per scene, bold white subtitles with a dark outline in the lower middle.
- Preview controls: play/pause, replay, timeline scrubber, a **Sound** button and a **Voice** button (load an audio file).
  `H` or `?clean=1` hides the controls.
- Sound effects generated with Web Audio in a `buildSfx(ctx)` function, used both live and by
  `renderSoundtrack()` (OfflineAudioContext, returns a base64 16-bit WAV), exactly like the reference.
- Render mode `?render=1`: no animation loop; expose `window.renderAt(t)`, `window.renderSoundtrack` and set
  `window.renderReady = true`. Subtitle/title/chapter fades must come from `T` in render mode (no CSS transitions).
- Multiple locations and time steps, a clear focal point in every shot, eased camera moves, a big environmental change
  that builds over the whole video, and a strong final wide shot.
- Keep it smooth on desktop and mobile: instanced meshes for repeated objects, few shadow casters, merged static geometry.

Lessons from earlier videos (the owner noticed every one of these, so they are requirements):
- Vehicles and animals face the way they move: check the model's long axis against the direction of travel.
- Nothing appears, shrinks or vanishes while it is on screen. People, cars and props only leave or appear on a camera cut.
- A cutaway opens on the shot change (the plane is already in place on the first frame), never as a sweep through the camera.
- The camera never passes through or grazes buildings, wires, trees or creatures; check every shot's path, not only its end.
- Flashes (lightning, explosions) rise and fall over a few frames; a one-frame jump to white looks like a glitch.
- Ending: after the last subtitle, hold the final shot about 3 s while the picture fades to dark, the title returns
  and the sound fades to silence (`ENDING = { fade, title, sound }`, see never-stopped-raining.html). The last
  subtitle ends before the fade starts.
- Subtitles must leave room for a calm voice: about 2.5 words per second, so a 10-word line needs at least 4 s.
- Sound effects stay under the narration; `place_voice.py` lowers them (default `--sfx-gain 0.45`) and ducks them
  while the voice speaks.

Check that the page loads without errors in a browser before you finish. Do not change other files.
