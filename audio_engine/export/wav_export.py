"""WAV export: 48 kHz, stereo, 24-bit PCM."""
from effects.volume_control import ffmpeg


def to_wav24(src, dst, af=None, sr=48000):
    args = ["-i", str(src)]
    if af:
        args += ["-af", af]
    ffmpeg(args + ["-ar", str(sr), "-ac", "2", "-c:a", "pcm_s24le", str(dst)])
    return dst
