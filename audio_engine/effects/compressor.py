"""Gentle compression (FFmpeg 'acompressor') to even out swells without pumping."""


def gentle(threshold_db=-24, ratio=2.0, attack_ms=80, release_ms=800):
    return f"acompressor=threshold={threshold_db}dB:ratio={ratio}:attack={attack_ms}:release={release_ms}:knee=6"
