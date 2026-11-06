"""Dark cinematic harmony: chord qualities, progressions in a minor key and smooth voice leading.

A progression is a list of (degree in semitones above the key tonic, quality). Progressions are
chained at random (never the same one twice in a row), and every chord is voiced as close as possible
to the previous one, so the inner voices move by small steps instead of jumping.
"""
import itertools

QUALITIES = {
    "m": [0, 3, 7],             # minor
    "five": [0, 7, 12],         # open fifth
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "madd9": [0, 3, 7, 14],     # minor add9
    "m7": [0, 3, 7, 10],
    "maj7": [0, 4, 7, 11],      # only on VI/III: the dark-but-warm film colour, not a pop chord
    "dim": [0, 3, 6],
    "m9": [0, 3, 7, 10, 14],    # extended
}

# degrees: 0 = i, 2 = ii, 3 = III, 5 = iv, 7 = v, 8 = VI, 10 = VII
PROGRESSIONS = {
    "calm": [
        [(0, "madd9"), (8, "maj7"), (3, "sus2"), (10, "five")],
        [(0, "m"), (5, "m7"), (8, "sus2"), (7, "sus4")],
        [(0, "five"), (8, "five"), (5, "madd9"), (7, "sus4")],
        [(0, "madd9"), (10, "sus2"), (8, "maj7"), (5, "m")],
        [(0, "m9"), (3, "sus2"), (8, "maj7"), (7, "sus4")],
    ],
    "deep": [                   # middle section: heavier, more tension
        [(0, "m7"), (2, "dim"), (7, "sus4"), (0, "madd9")],
        [(0, "m"), (8, "maj7"), (5, "m7"), (11, "dim")],
        [(5, "madd9"), (0, "five"), (1, "maj7"), (7, "sus4")],
        [(0, "madd9"), (5, "m9"), (2, "dim"), (7, "five")],
    ],
}

LOW, HIGH = 50, 76          # range of the voiced pad notes (D3..E5)


def chord_pcs(tonic_pc, degree, quality):
    root = (tonic_pc + degree) % 12
    return root, [(root + i) % 12 for i in QUALITIES[quality]]


def voice(pcs, root_pc, prev, n_voices=4):
    """Pick n distinct notes in LOW..HIGH that contain the root and the colour tone, closest to prev."""
    pcs = list(dict.fromkeys(pcs))
    must = {root_pc, pcs[1] if len(pcs) > 1 else root_pc}
    notes = [m for m in range(LOW, HIGH + 1) if m % 12 in pcs]
    best, best_cost = None, 1e9
    for cand in itertools.combinations(notes, min(n_voices, len(notes))):
        got = {m % 12 for m in cand}
        if not must <= got or len(got) < min(3, len(pcs)):
            continue
        span = cand[-1] - cand[0]
        if span > 19 or span < 7:
            continue
        if any(b - a < 2 for a, b in zip(cand, cand[1:])):    # no seconds packed together (muddy)
            continue
        if prev:
            cost = sum(abs(a - b) for a, b in zip(sorted(cand), sorted(prev)))
        else:
            cost = abs(sum(cand) / len(cand) - 62)               # first chord: around D4
        if cost < best_cost:
            best, best_cost = list(cand), cost
    return best or sorted(notes[:n_voices])


def progression_stream(tonic_pc, n_chords, rng, deep_from=None, chord_len=7.0):
    """List of dicts {degree, quality, root_pc, pcs, notes} for n_chords chords."""
    out, prev, last = [], None, None
    while len(out) < n_chords:
        t = len(out) * chord_len
        fam = "deep" if deep_from is not None and t >= deep_from and rng.random() < 0.45 else "calm"
        choices = [i for i in range(len(PROGRESSIONS[fam])) if (fam, i) != last]
        i = choices[rng.integers(len(choices))]
        last = (fam, i)
        for degree, q in PROGRESSIONS[fam][i]:
            root, pcs = chord_pcs(tonic_pc, degree, q)
            notes = voice(pcs, root, prev)
            out.append({"degree": degree, "quality": q, "root_pc": root, "pcs": pcs, "notes": notes})
            prev = notes
            if len(out) == n_chords:
                break
    return out
