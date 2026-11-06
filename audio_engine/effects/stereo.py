"""Stereo width with mid/side gain (FFmpeg 'extrastereo'): wider without delay tricks, so it stays stable
and does not sound phasey; mono playback keeps the full mid signal."""


def widen(width=1.3):
    width = max(1.0, min(2.0, width))
    return f"extrastereo=m={width:.2f}:c=false"
