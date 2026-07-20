"""Human Design mechanics: the gate wheel, centers, channels, and the rules that
derive Type / Authority / Profile / Definition / Incarnation Cross from a set of
planetary activations.

All structural data is cross-referenced from multiple independent open-source HD
engines (rave-engine, hdkit, human-design-py, SharpAstrology.HumanDesign) plus
published degree tables; the gate wheel is anchored at Gate 41 = 302.000° ecliptic
longitude (2°00' Aquarius), the Human Design year-start. See README for provenance.

This module is pure data + logic: no ephemeris, no I/O. compute.py feeds it
longitudes and consumes the derived chart.
"""
from __future__ import annotations

# --- the gate wheel -------------------------------------------------------

# Gates in zodiacal order, starting at Gate 41 (302.000° = 2°00' Aquarius).
WHEEL = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
         27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
         31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
         28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]
WHEEL_START = 302.0            # ecliptic longitude of Gate 41, line 1, start
GATE_ARC = 360.0 / 64          # 5.625°  -> 64 gates
LINE_ARC = GATE_ARC / 6        # 0.9375° -> 6 lines per gate
COLOR_ARC = LINE_ARC / 6       # 0.15625° -> 6 colors per line
TONE_ARC = COLOR_ARC / 6       # 0.0260417° -> 6 tones per color
BASE_ARC = TONE_ARC / 5        # 0.0052083° -> 5 bases per tone


def gate_line(longitude: float) -> tuple[int, int]:
    """Map an ecliptic longitude (0-360, tropical) to (gate, line 1-6)."""
    adj = (longitude - WHEEL_START) % 360.0
    idx = int(adj // GATE_ARC)
    gate = WHEEL[idx]
    line = int((adj % GATE_ARC) // LINE_ARC) + 1
    return gate, line


def full_address(longitude: float) -> dict:
    """Full HD address: gate, line, color, tone, base. Color and tone drive the
    Variable / Primary Health System layer (Digestion, Environment, Motivation,
    Perspective, Cognition). Each level is 1/6 of the one above it (base is 1/5)."""
    adj = (longitude - WHEEL_START) % 360.0
    idx = int(adj // GATE_ARC)
    off = adj % GATE_ARC
    line = int(off // LINE_ARC); offl = off % LINE_ARC
    color = int(offl // COLOR_ARC); offc = offl % COLOR_ARC
    tone = int(offc // TONE_ARC); offt = offc % TONE_ARC
    base = int(offt // BASE_ARC)
    return {"gate": WHEEL[idx], "line": line + 1, "color": color + 1,
            "tone": tone + 1, "base": base + 1}


# --- centers --------------------------------------------------------------

CENTERS = {  # display name -> its gates
    "Head":        [61, 63, 64],
    "Ajna":        [4, 11, 17, 24, 43, 47],
    "Throat":      [8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62],
    "G":           [1, 2, 7, 10, 13, 15, 25, 46],
    "Ego":         [21, 26, 40, 51],
    "Sacral":      [3, 5, 9, 14, 27, 29, 34, 42, 59],
    "SolarPlexus": [6, 22, 30, 36, 37, 49, 55],
    "Spleen":      [18, 28, 32, 44, 48, 50, 57],
    "Root":        [19, 38, 39, 41, 52, 53, 54, 58, 60],
}
CENTER_OF_GATE = {g: c for c, gates in CENTERS.items() for g in gates}

# Standard HD / Rave I Ching gate keynotes. Wording drifts between schools; these are
# the common Ra-lineage names (see reference.md). Spot-check before delivery.
GATE_NAMES = {
    1: "Self-Expression", 2: "Direction of the Self", 3: "Ordering", 4: "Formulization",
    5: "Fixed Rhythms", 6: "Friction", 7: "Role of the Self", 8: "Contribution",
    9: "Focus", 10: "Behavior of the Self", 11: "Ideas", 12: "Caution",
    13: "The Listener", 14: "Power Skills", 15: "Extremes", 16: "Skills",
    17: "Opinions", 18: "Correction", 19: "Wanting", 20: "The Now",
    21: "The Hunter", 22: "Openness", 23: "Assimilation", 24: "Rationalization",
    25: "Spirit of the Self", 26: "The Egoist", 27: "Caring", 28: "The Game Player",
    29: "Perseverance", 30: "Feelings", 31: "Influence", 32: "Continuity",
    33: "Privacy", 34: "Power", 35: "Change", 36: "Crisis",
    37: "Friendship", 38: "The Fighter", 39: "Provocation", 40: "Aloneness",
    41: "Contraction", 42: "Growth", 43: "Insight", 44: "Alertness",
    45: "The Gatherer", 46: "Determination of the Self", 47: "Realization", 48: "Depth",
    49: "Principles", 50: "Values", 51: "Shock", 52: "Stillness",
    53: "Beginnings", 54: "Ambition", 55: "Spirit", 56: "Stimulation",
    57: "Intuitive Clarity", 58: "Vitality", 59: "Sexuality", 60: "Acceptance",
    61: "Inner Truth", 62: "Detail", 63: "Doubt", 64: "Confusion",
}
MOTORS = {"Sacral", "SolarPlexus", "Ego", "Root"}
CENTER_LABEL = {
    "Head": "Head", "Ajna": "Ajna", "Throat": "Throat", "G": "G (Identity)",
    "Ego": "Ego (Heart / Will)", "Sacral": "Sacral", "SolarPlexus": "Solar Plexus",
    "Spleen": "Spleen", "Root": "Root",
}

# --- channels -------------------------------------------------------------

# (gateA, gateB, name, centerA, centerB). A channel is defined iff BOTH gates
# are activated; a center is defined iff a defined channel touches it.
CHANNELS = [
    (1, 8, "Inspiration", "G", "Throat"),
    (2, 14, "The Beat", "G", "Sacral"),
    (3, 60, "Mutation", "Sacral", "Root"),
    (4, 63, "Logic", "Ajna", "Head"),
    (5, 15, "Rhythm", "Sacral", "G"),
    (6, 59, "Mating", "SolarPlexus", "Sacral"),
    (7, 31, "The Alpha", "G", "Throat"),
    (9, 52, "Concentration", "Sacral", "Root"),
    (10, 20, "Awakening", "G", "Throat"),
    (10, 34, "Exploration", "G", "Sacral"),
    (10, 57, "Perfected Form", "G", "Spleen"),
    (11, 56, "Curiosity", "Ajna", "Throat"),
    (12, 22, "Openness", "Throat", "SolarPlexus"),
    (13, 33, "The Prodigal", "G", "Throat"),
    (16, 48, "The Wavelength", "Throat", "Spleen"),
    (17, 62, "Acceptance", "Ajna", "Throat"),
    (18, 58, "Judgment", "Spleen", "Root"),
    (19, 49, "Synthesis", "Root", "SolarPlexus"),
    (20, 34, "Charisma", "Throat", "Sacral"),
    (20, 57, "The Brainwave", "Throat", "Spleen"),
    (21, 45, "Money", "Ego", "Throat"),
    (23, 43, "Structuring", "Throat", "Ajna"),
    (24, 61, "Awareness", "Ajna", "Head"),
    (25, 51, "Initiation", "G", "Ego"),
    (26, 44, "Surrender", "Ego", "Spleen"),
    (27, 50, "Preservation", "Sacral", "Spleen"),
    (28, 38, "Struggle", "Spleen", "Root"),
    (29, 46, "Discovery", "Sacral", "G"),
    (30, 41, "Recognition", "SolarPlexus", "Root"),
    (32, 54, "Transformation", "Spleen", "Root"),
    (34, 57, "Power", "Sacral", "Spleen"),
    (35, 36, "Transitoriness", "Throat", "SolarPlexus"),
    (37, 40, "Community", "SolarPlexus", "Ego"),
    (39, 55, "Emoting", "Root", "SolarPlexus"),
    (42, 53, "Maturation", "Sacral", "Root"),
    (47, 64, "Abstraction", "Ajna", "Head"),
]


def _self_check():
    """Internal consistency: 36 channels, 64 gates each in exactly one center,
    every channel's stated centers match its gates' home centers."""
    assert len(CHANNELS) == 36, f"expected 36 channels, got {len(CHANNELS)}"
    all_gates = sorted(g for gs in CENTERS.values() for g in gs)
    assert all_gates == list(range(1, 65)), "gates must be exactly 1..64, once each"
    for a, b, name, ca, cb in CHANNELS:
        assert CENTER_OF_GATE[a] == ca, f"{name}: gate {a} is in {CENTER_OF_GATE[a]}, not {ca}"
        assert CENTER_OF_GATE[b] == cb, f"{name}: gate {b} is in {CENTER_OF_GATE[b]}, not {cb}"


_self_check()


# --- derivation -----------------------------------------------------------

def defined_channels(active_gates: set[int]) -> list[tuple]:
    """Channels with BOTH gates active, sorted by gate pair."""
    out = [ch for ch in CHANNELS if ch[0] in active_gates and ch[1] in active_gates]
    return sorted(out, key=lambda ch: (ch[0], ch[1]))


def defined_centers(channels: list[tuple]) -> set[str]:
    d = set()
    for a, b, name, ca, cb in channels:
        d.add(ca)
        d.add(cb)
    return d


def _components(centers: set[str], channels: list[tuple]) -> list[set[str]]:
    """Connected components of defined centers, edges = defined channels."""
    adj = {c: set() for c in centers}
    for a, b, name, ca, cb in channels:
        adj[ca].add(cb)
        adj[cb].add(ca)
    seen, comps = set(), []
    for c in centers:
        if c in seen:
            continue
        stack, comp = [c], set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.add(x)
            stack.extend(adj[x] - seen)
        comps.append(comp)
    return comps


DEFINITION_NAME = {0: "No Definition", 1: "Single Definition", 2: "Split Definition",
                   3: "Triple-Split Definition", 4: "Quadruple-Split Definition"}


def definition(centers: set[str], channels: list[tuple]) -> str:
    return DEFINITION_NAME.get(len(_components(centers, channels)), "Complex")


def _motor_reaches_throat(centers: set[str], channels: list[tuple]) -> bool:
    """BFS from each defined motor; True if any reaches the Throat through a
    chain of defined channels (indirect paths count, e.g. motor->G->Throat)."""
    if "Throat" not in centers:
        return False
    adj = {c: set() for c in centers}
    for a, b, name, ca, cb in channels:
        adj[ca].add(cb)
        adj[cb].add(ca)
    for motor in MOTORS & centers:
        seen, stack = set(), [motor]
        while stack:
            x = stack.pop()
            if x == "Throat":
                return True
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adj[x] - seen)
    return False


def hd_type(centers: set[str], channels: list[tuple]) -> str:
    if not centers:
        return "Reflector"
    reaches = _motor_reaches_throat(centers, channels)
    if "Sacral" in centers:
        return "Manifesting Generator" if reaches else "Generator"
    return "Manifestor" if reaches else "Projector"


TYPE_META = {
    "Manifestor": ("To Inform", "Peace", "Anger"),
    "Generator": ("To Respond", "Satisfaction", "Frustration"),
    "Manifesting Generator": ("To Respond, then Inform", "Satisfaction & Peace", "Frustration & Anger"),
    "Projector": ("Wait for the Invitation", "Success", "Bitterness"),
    "Reflector": ("Wait a Lunar Cycle", "Surprise / Delight", "Disappointment"),
}


def _g_connects_throat(centers, channels):
    if "G" not in centers or "Throat" not in centers:
        return False
    for a, b, name, ca, cb in channels:
        if {ca, cb} == {"G", "Throat"}:
            return True
    return False


def authority(centers: set[str], channels: list[tuple]) -> str:
    """Inner-authority hierarchy: first match wins, top-down."""
    if "SolarPlexus" in centers:
        return "Emotional (Solar Plexus)"
    if "Sacral" in centers:
        return "Sacral"
    if "Spleen" in centers:
        return "Splenic"
    if "Ego" in centers:
        return "Ego (Heart)"
    if _g_connects_throat(centers, channels):
        return "Self-Projected (G)"
    if not centers:
        return "Lunar (Reflector)"
    return "Mental Projector (Environmental / No Inner Authority)"


PROFILE_LINE = {1: "Investigator", 2: "Hermit", 3: "Martyr", 4: "Opportunist",
                5: "Heretic", 6: "Role Model"}
RIGHT_ANGLE = {(1, 3), (1, 4), (2, 4), (2, 5), (3, 5), (3, 6), (4, 6)}
JUXTAPOSITION = {(4, 1)}
LEFT_ANGLE = {(5, 1), (5, 2), (6, 2), (6, 3)}


def cross_angle(p_line: int, d_line: int) -> str:
    key = (p_line, d_line)
    if key in RIGHT_ANGLE:
        return "Right Angle"
    if key in JUXTAPOSITION:
        return "Juxtaposition"
    if key in LEFT_ANGLE:
        return "Left Angle"
    return "Right Angle"  # fallback; every valid profile is covered above
