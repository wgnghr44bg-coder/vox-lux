#!/usr/bin/env python3
"""Estimate speaking pace (syllables per second) of one or more audio files.

Counts syllable nuclei as energy peaks in the vowel band (300-2500 Hz). It is a
rough estimate, but the method is the same for every file, so comparing a
reference narration with your own output is fair:

    python3 tools/measure_pace.py reference.mp3 test.mp3

If test.mp3 is slower than the reference, raise --speed in xai_voiceover.py
by roughly the ratio (e.g. 3.35 / 3.10 = 1.08), or shorten the pauses.

Requires: numpy, scipy, and ffmpeg (on PATH, via $FFMPEG, or imageio-ffmpeg).
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import butter, find_peaks, sosfiltfilt

from xai_voiceover import find_ffmpeg

SR = 16000
HOP = 160  # 10 ms


def load_mono(ffmpeg: str, path: Path) -> np.ndarray:
    raw = subprocess.run(
        [ffmpeg, "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
         "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def syllable_peaks(x: np.ndarray) -> np.ndarray:
    sos = butter(4, [300, 2500], btype="band", fs=SR, output="sos")
    y = sosfiltfilt(sos, x)
    env = np.sqrt(np.convolve(y**2, np.ones(400) / 400, "same")[::HOP])
    db = np.convolve(20 * np.log10(env + 1e-9), np.ones(5) / 5, "same")
    # Peaks at least 2 dB prominent and 100 ms apart (max 10 syllables/s).
    peaks, _ = find_peaks(db, prominence=2.0, distance=10)
    # Keep peaks clearly above the local floor (drops noise/music bumps).
    floor = np.array([np.percentile(db[max(0, i - 200):i + 200], 30) for i in peaks])
    return peaks[db[peaks] > floor + 3]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    ffmpeg = find_ffmpeg()
    for path in args.files:
        x = load_mono(ffmpeg, path)
        seconds = len(x) / SR
        n = len(syllable_peaks(x))
        print(f"{path}: {n / seconds:.2f} syllables/s "
              f"({n} in {seconds:.0f} s, including pauses)")


if __name__ == "__main__":
    main()
