"""Mix settings and the level logic: the music is placed a fixed number of dB below the narration
(measured as EBU R128 loudness), then shaped so it never fights the voice."""
from dataclasses import dataclass

from effects import volume_control as vc


@dataclass
class MixConfig:
    music_below_voice_db: float = 11.0   # in LUFS; measured on the owner's example (6 nov 2026) this gives the same
                                         # ±19 dB between spoken words and the music in the gaps
    voice_gain_db: float = 0.0           # manual trim of the narration
    music_gain_db: float = 0.0           # manual trim of the music on top of the automatic level
    ducking: bool = True
    duck_amount_db: float = 3.0          # extra dip while the narrator speaks
    duck_attack: float = 0.15
    duck_release: float = 1.2
    low_cut_hz: float = 120.0            # music low end under the voice (0 = off): no low-frequency buildup
    clarity_db: float = -3.0             # dip in the music around 2.5 kHz where speech is most intelligible
    target_lufs: float = -14.0           # final loudness (YouTube level, owner's standard)
    true_peak: float = -1.0
    tail: float = 4.0                    # seconds of music after the last word


def music_gain_db(voice_lufs, music_lufs, cfg):
    return (voice_lufs + cfg.voice_gain_db - cfg.music_below_voice_db) - music_lufs + cfg.music_gain_db


def music_shaping(cfg):
    parts = []
    if cfg.low_cut_hz > 0:
        parts.append(f"highpass=f={cfg.low_cut_hz}:p=1")
    if cfg.clarity_db:
        parts.append(f"equalizer=f=2500:t=q:w=1.0:g={cfg.clarity_db}")
    return ",".join(parts) or "anull"


def levels(voice, music):
    return vc.measure(voice), vc.measure(music)
