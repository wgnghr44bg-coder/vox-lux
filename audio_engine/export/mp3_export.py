"""MP3 export (LAME, 320 kbit/s CBR by default)."""
from effects.volume_control import ffmpeg


def to_mp3(src, dst, kbps=320, seconds=None):
    """seconds: only the first N seconds (quick preview of a long file)."""
    args = ["-i", str(src)] + (["-t", str(seconds)] if seconds else [])
    ffmpeg(args + ["-c:a", "libmp3lame", "-b:a", f"{kbps}k", str(dst)])
    return dst
