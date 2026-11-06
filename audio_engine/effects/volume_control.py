"""Loudness measurement and normalisation (EBU R128), fades, and a small FFmpeg runner."""
import json
import re
import subprocess


def ffmpeg(args, quiet=True):
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-y"] + (["-loglevel", "error"] if quiet else []) + args
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError(f"ffmpeg failed: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r


def measure(path, extra_filter=None):
    """Integrated loudness (LUFS), true peak (dBTP) and loudness range of a file."""
    af = (extra_filter + "," if extra_filter else "") + "loudnorm=print_format=json"
    r = ffmpeg(["-i", str(path), "-af", af, "-f", "null", "-"], quiet=False)
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    return {"lufs": float(js["input_i"]), "true_peak": float(js["input_tp"]), "lra": float(js["input_lra"]),
            "thresh": float(js["input_thresh"]), "offset": float(js["target_offset"])}


def loudnorm_two_pass(target_lufs, tp=-1.0, lra=11.0, m=None):
    """Second-pass loudnorm filter (linear: one fixed gain, no pumping), using the first-pass numbers m."""
    return (f"loudnorm=I={target_lufs}:TP={tp}:LRA={max(lra, m['lra'] + 1)}:measured_I={m['lufs']}:"
            f"measured_TP={m['true_peak']}:measured_LRA={m['lra']}:measured_thresh={m['thresh']}:"
            f"offset={m['offset']}:linear=true")


def fades(duration, fade_in=4.0, fade_out=8.0):
    parts = []
    if fade_in > 0:
        parts.append(f"afade=t=in:d={fade_in}:curve=qsin")
    if fade_out > 0:
        parts.append(f"afade=t=out:st={max(duration - fade_out, 0):.3f}:d={fade_out}:curve=qsin")
    return ",".join(parts)


def peak_db(path):
    r = ffmpeg(["-i", str(path), "-af", "astats=measure_overall=Peak_level:measure_perchannel=none", "-f", "null", "-"],
               quiet=False)
    m = re.findall(r"Peak level dB:\s*(-?[\d.]+|-inf)", r.stderr)
    return float(m[-1]) if m and m[-1] != "-inf" else -200.0
