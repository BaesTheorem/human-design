"""Render a themed Human Design BodyGraph as an SVG string.

Geometry (center polygons, the 64 gate anchor points, straight-line channels) is
adapted from the MIT-licensed blank bodygraph in jdempcy/hdkit
(https://github.com/jdempcy/hdkit, bodygraph-blank.svg, (c) 2023 Jonah Dempcy),
cross-validated against dturkuler/humandesign_api's layout data. Coordinate system:
viewBox 0 0 851.41 1309.4, y increasing downward.

Defined centers fill solid ink; open centers stay white. The latent 36-channel
lattice is drawn faint; fully-defined channels overlay in brass. Each gate badge is
colored by activation: black = Personality (conscious), red = Design (unconscious),
black with a red ring = both.
"""
import hd

VIEW_W, VIEW_H = 851.41, 1309.4

# palette (matches pipeline/style.css)
INK = "#22283d"
BRASS = "#9c7b33"
RED = "#9a4a3c"
HAIRLINE = "#cbc5b6"
PAPER = "#fffdf8"
OPEN_FILL = "#ffffff"
FAINT = "#e2ddd0"

# center polygons in the hdkit coordinate system
CENTER_POLY = {
    "Head": [(420, 13), (334, 158), (507, 158)],
    "Ajna": [(334, 209), (507, 209), (420, 360)],
    "Throat": [(343, 399), (497, 399), (497, 559), (343, 559)],
    "G": [(420, 592), (521, 694), (420, 796), (320, 694)],
    "Ego": [(606, 744), (521, 842), (670, 842)],
    "Sacral": [(343, 925), (497, 925), (497, 1079), (343, 1079)],
    "SolarPlexus": [(680, 975), (841, 884), (841, 1066)],
    "Spleen": [(167, 975), (6, 884), (6, 1066)],
    "Root": [(343, 1149), (497, 1149), (497, 1296), (343, 1296)],
}

# the 64 gate badge-circle centers
GATE_XY = {
    1: (420.8, 616.0), 2: (420.7, 766.3), 3: (420.7, 1060.1), 4: (458.2, 228.6),
    5: (383.2, 942.7), 6: (712.6, 976.7), 7: (383.2, 650.9), 8: (425.2, 540.0),
    9: (458.2, 1060.1), 10: (345.5, 690.9), 11: (458.2, 263.4), 12: (479.1, 476.2),
    13: (458.2, 650.9), 14: (420.7, 942.7), 15: (383.2, 734.7), 16: (362.4, 446.9),
    17: (383.2, 262.0), 18: (30.4, 1031.5), 19: (478.1, 1202.3), 20: (362.4, 494.6),
    21: (604.1, 770.2), 22: (781.4, 939.0), 23: (420.7, 416.3), 24: (420.7, 228.6),
    25: (492.6, 699.5), 26: (554.1, 820.2), 27: (363.5, 1024.8), 28: (62.6, 1012.6),
    29: (458.2, 942.7), 30: (813.6, 1031.5), 31: (383.2, 540.2), 32: (95.7, 993.8),
    33: (458.2, 540.2), 34: (363.5, 978.7), 35: (479.1, 442.2), 36: (813.6, 918.3),
    37: (748.2, 957.3), 38: (363.4, 1238.4), 39: (478.1, 1238.4), 40: (638.0, 820.2),
    41: (478.1, 1274.6), 42: (383.2, 1060.1), 43: (420.7, 324.7), 44: (95.7, 957.2),
    45: (479.1, 509.8), 46: (458.2, 734.7), 47: (383.2, 228.5), 48: (30.4, 918.4),
    49: (748.2, 993.8), 50: (131.4, 976.7), 51: (580.1, 794.1), 52: (458.2, 1171.2),
    53: (383.2, 1171.2), 54: (363.4, 1202.3), 55: (780.8, 1013.1), 56: (458.2, 416.3),
    57: (62.6, 939.0), 58: (363.4, 1274.6), 59: (476.4, 1024.8), 60: (420.7, 1171.2),
    61: (420.8, 140.0), 62: (383.2, 416.3), 63: (457.4, 140.0), 64: (383.2, 140.3),
}

GATE_R = 11.5


def _poly(pts, fill, stroke, sw):
    d = " ".join(f"{x},{y}" for x, y in pts)
    return f"<polygon points='{d}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'/>"


def render(subj):
    defined = set(subj["defined_centers"])
    pers_gates = {p["gate"] for p in subj["personality"].values()}
    des_gates = {p["gate"] for p in subj["design"].values()}
    active = pers_gates | des_gates
    defined_pairs = {frozenset(ch["gates"]) for ch in subj["channels"]}

    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {VIEW_W} {VIEW_H}' "
             f"font-family=\"Palatino, Georgia, serif\">"]
    parts.append(f"<rect x='0' y='0' width='{VIEW_W}' height='{VIEW_H}' fill='{PAPER}'/>")

    # 1. centers (behind everything)
    for name, pts in CENTER_POLY.items():
        if name in defined:
            parts.append(_poly(pts, INK, INK, 1.5))
        else:
            parts.append(_poly(pts, OPEN_FILL, HAIRLINE, 1.5))

    # 2. latent lattice as short gate stubs (cleaner than full lines across gaps),
    #    then fully-defined channels overlaid solid on top
    STUB = 26.0
    for a, b, *_ in hd.CHANNELS:
        if frozenset((a, b)) in defined_pairs:
            continue
        (x1, y1), (x2, y2) = GATE_XY[a], GATE_XY[b]
        dx, dy = x2 - x1, y2 - y1
        dist = (dx * dx + dy * dy) ** 0.5 or 1.0
        L = min(STUB, dist / 2 - GATE_R)
        ux, uy = dx / dist, dy / dist
        for (sx, sy), (vx, vy) in (((x1, y1), (ux, uy)), ((x2, y2), (-ux, -uy))):
            parts.append(f"<line x1='{sx + vx * GATE_R:.1f}' y1='{sy + vy * GATE_R:.1f}' "
                         f"x2='{sx + vx * (GATE_R + L):.1f}' y2='{sy + vy * (GATE_R + L):.1f}' "
                         f"stroke='{FAINT}' stroke-width='2.5'/>")
    for a, b, *_ in hd.CHANNELS:
        if frozenset((a, b)) not in defined_pairs:
            continue
        (x1, y1), (x2, y2) = GATE_XY[a], GATE_XY[b]
        parts.append(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' "
                     f"stroke='{BRASS}' stroke-width='6' stroke-linecap='round'/>")

    # 3. gate badges on top
    for g in range(1, 65):
        x, y = GATE_XY[g]
        in_p, in_d = g in pers_gates, g in des_gates
        if in_p and in_d:
            fill, txt, ring = INK, "#fff", RED
        elif in_p:
            fill, txt, ring = INK, "#fff", INK
        elif in_d:
            fill, txt, ring = RED, "#fff", RED
        else:
            fill, txt, ring = PAPER, "#9a927f", HAIRLINE
        sw = 3 if (in_p and in_d) else 1.2
        parts.append(f"<circle cx='{x}' cy='{y}' r='{GATE_R}' fill='{fill}' "
                     f"stroke='{ring}' stroke-width='{sw}'/>")
        parts.append(f"<text x='{x}' y='{y + 4.2}' text-anchor='middle' "
                     f"font-size='13' fill='{txt}'>{g}</text>")

    parts.append("</svg>")
    return "".join(parts)
