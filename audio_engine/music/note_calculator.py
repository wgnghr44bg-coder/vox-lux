"""Note frequencies in 432 Hz tuning: f = 432 * 2^((n - 69) / 12), with n the MIDI note number (A4 = 69)."""

A4_HZ = 432.0
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_hz(n, a4=A4_HZ):
    return a4 * 2.0 ** ((n - 69) / 12.0)


def name_to_pc(name):
    """'A' -> 9, 'D#' -> 3 (pitch class)."""
    return NAMES.index(name.strip().upper().replace("BB", "A#").replace("EB", "D#"))


def midi_name(n):
    return f"{NAMES[n % 12]}{n // 12 - 1}"
