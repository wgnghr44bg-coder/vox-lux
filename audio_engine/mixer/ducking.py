"""Sidechain ducking computed from the narration itself: while the narrator speaks the music dips by a
few dB, and it comes back up smoothly in the pauses. Done as a gain curve (100 points per second) so the
amount in dB is exact, not dependent on compressor ratios."""
import numpy as np
import soundfile as sf

RATE = 100   # gain points per second


def gain_curve(voice_path, amount_db=4.0, attack=0.15, release=1.2, threshold_db=-45.0):
    """Returns gain in dB per 1/RATE s (0 when silent, -amount_db while speaking)."""
    info = sf.info(voice_path)
    hop = info.samplerate // RATE
    env = []
    with sf.SoundFile(voice_path) as f:
        for block in f.blocks(blocksize=hop * RATE * 30, always_2d=True):
            mono = block.mean(axis=1)
            n = len(mono) // hop
            if n:
                env.append(np.sqrt((mono[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12))
    env_db = 20 * np.log10(np.concatenate(env) + 1e-12)
    peak = np.percentile(env_db, 99)
    speaking = np.clip((env_db - (peak + threshold_db + 25)) / 10.0, 0, 1)    # 0..1, soft knee of 10 dB
    target = -amount_db * speaking
    out = np.empty_like(target)
    a_up, a_dn = np.exp(-1 / (release * RATE)), np.exp(-1 / (attack * RATE))
    g = 0.0
    for i, x in enumerate(target):                      # one-pole smoothing: fast down, slow back up
        coef = a_dn if x < g else a_up
        g = coef * g + (1 - coef) * x
        out[i] = g
    return out


def apply(music_block, start_sample, sr, curve_db):
    """Multiply a (n, 2) music block that starts at start_sample with the interpolated curve."""
    t = (start_sample + np.arange(len(music_block))) / sr * RATE
    g = np.interp(t, np.arange(len(curve_db)), curve_db, right=0.0)
    return music_block * (10 ** (g / 20))[:, None]
