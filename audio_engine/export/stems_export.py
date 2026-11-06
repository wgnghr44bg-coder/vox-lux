"""Stem export: every music layer as its own 24-bit WAV, with the same gain as the dry mix got,
so the stems add up to the (pre-effects) music."""
from pathlib import Path

from .wav_export import to_wav24


def export_stems(folder, gain_db, out_folder=None):
    folder = Path(folder)
    out = Path(out_folder or folder / "stems")
    out.mkdir(exist_ok=True)
    done = []
    for f in sorted(folder.glob("stem-*.wav")):
        done.append(to_wav24(f, out / f.name, af=f"volume={gain_db:.2f}dB"))
        f.unlink()
    return done
