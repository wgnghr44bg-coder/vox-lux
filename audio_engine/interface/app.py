"""Local web interface (Gradio): Voice Studio, Music Studio and Final Mix. Opens on http://127.0.0.1:7865."""
import json
import time
from dataclasses import asdict, fields
from pathlib import Path

import gradio as gr

from music.composition_engine import PRESETS, MusicConfig, preset
from music.music_studio import generate
from mixer.final_mix import mix
from mixer.voice_music_mixer import MixConfig
from voice.voice_config import DESIGN_OPTIONS, VoiceConfig, list_voices, load_voice

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"


def stamp(kind, name=""):
    d = OUT / kind / (time.strftime("%Y%m%d-%H%M%S") + (f"-{name}" if name else ""))
    d.mkdir(parents=True, exist_ok=True)
    return d


def recent(kind, filename):
    return [str(p) for p in sorted((OUT / kind).glob(f"*/{filename}"), reverse=True)] if (OUT / kind).exists() else []


def bar(progress):
    return lambda f, m="": progress(f, desc=m)


# ---------------- voice ----------------
def do_voice(text, txt_file, voice, speed, seed, steps, guidance, p_sent, p_par, batch_size, progress=gr.Progress()):
    from voice.batch_generator import narrate
    if txt_file:
        text = Path(txt_file).read_text(encoding="utf-8")
    cfg = VoiceConfig(voice=voice, speed=speed, seed=int(seed), num_step=int(steps), guidance_scale=guidance,
                      pause_sentence=p_sent, pause_paragraph=p_par, batch_size=int(batch_size))
    d = stamp("voice")
    r = narrate(text, cfg, d, bar(progress))
    info = f"{r['sentences']} zinnen, {r['words']} woorden, {r['duration'] / 60:.1f} min, {r['words_per_min']} woorden/min, {r['seconds']} s rekentijd"
    return str(d / "voice.mp3"), [str(d / "voice.wav"), str(d / "voice.mp3"), str(d / "voice-tijden.tsv"), str(d / "voice-config.json")], info


def do_voice_batch(files, voice, speed, seed, progress=gr.Progress()):
    from voice.batch_generator import batch
    if not files:
        raise gr.Error("Kies een of meer .txt-bestanden.")
    scripts = {Path(f).stem: Path(f).read_text(encoding="utf-8") for f in files}
    d = stamp("voice", "batch")
    res = batch(scripts, VoiceConfig(voice=voice, speed=speed, seed=int(seed)), d, bar(progress))
    out = [str(d / n / f"{n}.wav") for n in res] + [str(d / n / f"{n}.mp3") for n in res]
    return out, "\n".join(f"{n}: {r['duration'] / 60:.1f} min, {r['words_per_min']} woorden/min" for n, r in res.items())


def do_design(name, gender, age, pitch, accent, seed, progress=gr.Progress()):
    from voice.omnivoice_engine import design_voice
    if not name.strip():
        raise gr.Error("Geef de stem een naam.")
    progress(0.2, desc="stem ontwerpen")
    p = design_voice(name.strip(), gender, age, pitch, accent, int(seed))
    return str(p), gr.update(choices=list_voices(), value=name.strip())


def voice_preview(voice):
    ref, meta = load_voice(voice)
    return str(ref), meta.get("description", "")


# ---------------- music ----------------
def do_music(preset_name, minutes, seconds, key, seed, chord_len, drone, strings, choir, piano, atmosphere,
             reverb_mix, reverb_size, lowpass, width, level, stems, progress=gr.Progress()):
    dur = float(minutes) * 60 + float(seconds)
    if dur < 10:
        raise gr.Error("Kies minstens 10 seconden.")
    cfg = preset(preset_name, duration=dur, key=key, seed=int(seed), chord_len=chord_len, drone=drone,
                 strings=strings, choir=choir, piano=piano, atmosphere=atmosphere, reverb_mix=reverb_mix,
                 reverb_size=reverb_size, lowpass_hz=lowpass, width=width, target_lufs=level)
    d = stamp("music", preset_name)
    r = generate(cfg, d, stems=stems, progress=bar(progress))
    prev = d / "preview.mp3"
    from export.mp3_export import to_mp3
    to_mp3(d / "music.wav", prev, kbps=192, seconds=180)
    files = [str(p) for p in [d / "music.wav", d / "music.mp3", d / "config.json"] + sorted((d / "stems").glob("*.wav"))
             if p.exists()]
    info = f"{r['chords']} akkoorden (elke {cfg.chord_len} s), {r['loudness']['lufs']} LUFS, piek {r['loudness']['true_peak']} dBTP, {r['seconds']} s rekentijd"
    return str(prev), files, info


def apply_preset(name):
    p = {**asdict(MusicConfig()), **PRESETS[name]}
    return [p[k] for k in ("drone", "strings", "choir", "piano", "atmosphere", "reverb_mix", "reverb_size", "lowpass_hz", "width")]


def load_music_config(file):
    js = json.loads(Path(file).read_text(encoding="utf-8"))["config"]
    c = MusicConfig(**{f.name: js[f.name] for f in fields(MusicConfig) if f.name in js})
    return [c.preset, int(c.duration // 60), c.duration % 60, c.key, c.seed, c.chord_len, c.drone, c.strings, c.choir,
            c.piano, c.atmosphere, c.reverb_mix, c.reverb_size, c.lowpass_hz, c.width, c.target_lufs]


# ---------------- mix ----------------
def do_mix(voice_sel, voice_up, music_sel, music_up, auto_music, preset_name, below, voice_gain, music_gain, duck,
           duck_amount, progress=gr.Progress()):
    vpath = voice_up or voice_sel
    if not vpath:
        raise gr.Error("Kies of upload een stem.")
    d = stamp("mix")
    mpath = music_up or music_sel
    if auto_music or not mpath:
        import soundfile as sf
        dur = sf.info(vpath).duration + 6
        progress(0.02, desc="muziek op lengte maken")
        generate(preset(preset_name, duration=dur), d / "music", stems=False,
                 progress=lambda f, m="": progress(0.5 * f, desc=f"muziek: {m}"))
        mpath = d / "music" / "music.wav"
    cfg = MixConfig(music_below_voice_db=below, voice_gain_db=voice_gain, music_gain_db=music_gain, ducking=duck,
                    duck_amount_db=duck_amount)
    r = mix(vpath, mpath, cfg, d, progress=lambda f, m="": progress(0.5 + 0.5 * f, desc=m))
    from export.mp3_export import to_mp3
    to_mp3(d / "mix.wav", d / "preview.mp3", kbps=192, seconds=300)
    info = f"eind: {r['result']['lufs']} LUFS, piek {r['result']['true_peak']} dBTP; muziek {r['music_gain_db']} dB" + \
           ("; LET OP: muziek was te kort en is herhaald" if r["music_looped"] else "")
    return str(d / "preview.mp3"), [str(d / "mix.wav"), str(d / "mix.mp3"), str(d / "mix-config.json")], info


def refresh():
    return gr.update(choices=recent("voice", "voice.wav")), gr.update(choices=recent("music", "music.wav"))


def build():
    with gr.Blocks(title="Audio Engine – documentaire") as app:
        gr.Markdown("## Audio Engine – stem (OmniVoice) en 432 Hz-muziek, alles lokaal")
        with gr.Tab("Voice Studio"):
            with gr.Row():
                with gr.Column(scale=3):
                    text = gr.Textbox(label="Script (lege regel = nieuwe alinea, [pause] / [long-pause] = extra pauze)", lines=12)
                    txt = gr.File(label="of .txt importeren", file_types=[".txt"], type="filepath")
                with gr.Column(scale=2):
                    voice = gr.Dropdown(list_voices(), value="narrator-b", label="Stem")
                    ref_audio = gr.Audio(label="Voorbeeld van de stem", interactive=False)
                    ref_info = gr.Markdown()
                    speed = gr.Slider(0.6, 1.1, 0.64, step=0.01, label="Snelheid (0.64 ≈ 130 woorden/min)")
                    with gr.Accordion("Meer instellingen", open=False):
                        seed = gr.Number(7, label="Seed (zelfde seed = zelfde uitvoering)")
                        steps = gr.Slider(16, 64, 32, step=4, label="OmniVoice-stappen")
                        guidance = gr.Slider(1.0, 4.0, 2.0, step=0.1, label="Guidance")
                        p_sent = gr.Slider(0.3, 2.0, 0.7, step=0.1, label="Pauze na een zin (s)")
                        p_par = gr.Slider(0.5, 3.0, 1.1, step=0.1, label="Pauze na een alinea (s)")
                        bsize = gr.Slider(1, 8, 4, step=1, label="Zinnen tegelijk op de GPU")
            go = gr.Button("Stem maken", variant="primary")
            v_info = gr.Markdown()
            v_play = gr.Audio(label="Luisteren", interactive=False)
            v_files = gr.Files(label="Downloads (WAV 48 kHz 24-bit, MP3, tijden, JSON)")
            go.click(do_voice, [text, txt, voice, speed, seed, steps, guidance, p_sent, p_par, bsize], [v_play, v_files, v_info])
            voice.change(voice_preview, voice, [ref_audio, ref_info])
            app.load(voice_preview, voice, [ref_audio, ref_info])
            with gr.Accordion("Batch: meerdere scripts tegelijk", open=False):
                bfiles = gr.File(file_count="multiple", file_types=[".txt"], type="filepath", label=".txt-bestanden")
                bgo = gr.Button("Alles inspreken")
                b_info = gr.Markdown()
                b_out = gr.Files(label="Resultaten")
                bgo.click(do_voice_batch, [bfiles, voice, speed, seed], [b_out, b_info])
            with gr.Accordion("Nieuwe stem ontwerpen (OmniVoice kent alleen deze kenmerken)", open=False):
                with gr.Row():
                    d_name = gr.Textbox(label="Naam", placeholder="bijv. narrator-c")
                    d_g = gr.Dropdown(DESIGN_OPTIONS["gender"], value="male", label="Geslacht")
                    d_a = gr.Dropdown(DESIGN_OPTIONS["age"], value="elderly", label="Leeftijd")
                    d_p = gr.Dropdown(DESIGN_OPTIONS["pitch"], value="low pitch", label="Toonhoogte")
                    d_ac = gr.Dropdown(DESIGN_OPTIONS["accent"], value="british accent", label="Accent")
                    d_s = gr.Number(19, label="Seed")
                d_go = gr.Button("Ontwerpen en opslaan")
                d_out = gr.Audio(label="Nieuwe stem", interactive=False)
                d_go.click(do_design, [d_name, d_g, d_a, d_p, d_ac, d_s], [d_out, voice])

        with gr.Tab("Music Studio"):
            with gr.Row():
                with gr.Column():
                    pr = gr.Radio(list(PRESETS), value="referentie", label="Stijl")
                    with gr.Row():
                        mins = gr.Number(2, label="Minuten")
                        secs = gr.Number(0, label="Seconden")
                    key = gr.Dropdown(["A", "D", "E", "B", "C", "G", "F"], value="A", label="Toonsoort (mineur)")
                    mseed = gr.Number(7, label="Seed")
                    clen = gr.Slider(4, 12, 7, step=0.5, label="Akkoordwissel (s)")
                    gr.Markdown("Stemming: **A4 = 432 Hz** (vast)")
                with gr.Column():
                    dr = gr.Slider(0, 2, 0, step=0.05, label="Drone")
                    st = gr.Slider(0, 2, 1, step=0.05, label="Strijkers")
                    ch = gr.Slider(0, 2, 0.5, step=0.05, label="Koor")
                    pi = gr.Slider(0, 2, 0, step=0.05, label="Piano")
                    at = gr.Slider(0, 2, 0.25, step=0.05, label="Sfeer")
                with gr.Column():
                    rv = gr.Slider(0, 1, 0.35, step=0.05, label="Galm (hoeveelheid)")
                    rs = gr.Slider(1, 8, 3.0, step=0.5, label="Galm (lengte, s)")
                    lp = gr.Slider(600, 12000, 1000, step=100, label="Low-pass (Hz)")
                    wd = gr.Slider(1, 2, 1.2, step=0.05, label="Stereobreedte")
                    lvl = gr.Slider(-36, -14, -24, step=1, label="Muziekvolume (LUFS)")
                    stems = gr.Checkbox(True, label="Losse lagen (stems) exporteren")
            pr.change(apply_preset, pr, [dr, st, ch, pi, at, rv, rs, lp, wd])
            mgo = gr.Button("Muziek maken", variant="primary")
            m_info = gr.Markdown()
            m_play = gr.Audio(label="Luisteren (eerste 3 min)", interactive=False)
            m_files = gr.Files(label="Downloads (WAV 48 kHz 24-bit, MP3, stems, JSON)")
            mgo.click(do_music, [pr, mins, secs, key, mseed, clen, dr, st, ch, pi, at, rv, rs, lp, wd, lvl, stems],
                      [m_play, m_files, m_info])
            with gr.Accordion("Instellingen laden uit een config.json (zelfde muziek opnieuw)", open=False):
                cfile = gr.File(file_types=[".json"], type="filepath")
                cfile.upload(load_music_config, cfile, [pr, mins, secs, key, mseed, clen, dr, st, ch, pi, at, rv, rs, lp, wd, lvl])

        with gr.Tab("Final Mix"):
            with gr.Row():
                with gr.Column():
                    v_sel = gr.Dropdown(recent("voice", "voice.wav"), label="Gemaakte stem")
                    v_up = gr.File(label="of stem uploaden", type="filepath")
                    m_sel = gr.Dropdown(recent("music", "music.wav"), label="Gemaakte muziek")
                    m_up = gr.File(label="of muziek uploaden", type="filepath")
                    auto = gr.Checkbox(True, label="Nieuwe muziek precies op lengte maken")
                    mpr = gr.Radio(list(PRESETS), value="referentie", label="Stijl (bij nieuwe muziek)")
                    ref_btn = gr.Button("Lijsten verversen")
                with gr.Column():
                    below = gr.Slider(4, 30, 11, step=0.5, label="Muziek onder de stem (dB, 11 = zoals het voorbeeld)")
                    vg = gr.Slider(-6, 6, 0, step=0.5, label="Stem volume (dB)")
                    mg = gr.Slider(-12, 12, 0, step=0.5, label="Muziek volume extra (dB)")
                    duck = gr.Checkbox(True, label="Ducking: muziek iets zachter als er gesproken wordt")
                    dam = gr.Slider(0, 10, 3, step=0.5, label="Ducking (dB)")
            xgo = gr.Button("Eindmix maken", variant="primary")
            x_info = gr.Markdown()
            x_play = gr.Audio(label="Luisteren (eerste 5 min)", interactive=False)
            x_files = gr.Files(label="Downloads (WAV 48 kHz 24-bit, MP3, JSON)")
            ref_btn.click(refresh, None, [v_sel, m_sel])
            xgo.click(do_mix, [v_sel, v_up, m_sel, m_up, auto, mpr, below, vg, mg, duck, dam], [x_play, x_files, x_info])
    return app


def launch(port=7865, open_browser=True):
    build().queue().launch(server_name="127.0.0.1", server_port=port, inbrowser=open_browser,
                           allowed_paths=[str(OUT), str(ROOT / "voices")])
