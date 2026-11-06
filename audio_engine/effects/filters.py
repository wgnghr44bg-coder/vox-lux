"""FFmpeg filter strings for tone shaping."""


def lowpass(hz):
    """Gentle 12 dB/octave low-pass: takes the harshness off without making it dull."""
    return f"lowpass=f={hz}:p=2:width_type=q:w=0.6"


def highpass(hz):
    """Removes rumble below hz (keeps the low end controlled)."""
    return f"highpass=f={hz}:p=2"


def tilt_dark(db=-1.5, hz=3000):
    """Slight high shelf down: a warmer top end."""
    return f"treble=g={db}:f={hz}"
