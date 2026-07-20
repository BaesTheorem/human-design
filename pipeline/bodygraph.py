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
VB_Y0 = -104          # headroom above the Head for the four Variable arrows

# palette (matches pipeline/style.css)
INK = "#22283d"
BRASS = "#9c7b33"
RED = "#9a4a3c"
HAIRLINE = "#cbc5b6"
PAPER = "#fffdf8"
OPEN_FILL = "#ffffff"
OPEN_STROKE = "#8c8574"   # open-center outline; must read on white paper
FAINT = "#b3ab97"         # latent (undefined) channel stubs; darker than paper
INACTIVE_RING = "#9a9280"
INACTIVE_TXT = "#7c745f"

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


def _arrow(x, y, direction, color, s=11):
    if direction == "left":
        pts = [(x + s, y - s), (x + s, y + s), (x - s, y)]
    else:
        pts = [(x - s, y - s), (x - s, y + s), (x + s, y)]
    d = " ".join(f"{px:.0f},{py:.0f}" for px, py in pts)
    return f"<polygon points='{d}' fill='{color}'/>"


def _variable_arrows(v):
    """The four crown arrows: Design pair (red) left, Personality pair (black) right.
    Top of each pair is Sun-driven, bottom is Node-driven."""
    xL, xR, yT, yB = 372, 480, VB_Y0 + 36, VB_Y0 + 76
    out = [
        f"<text x='{xL}' y='{VB_Y0 + 16}' text-anchor='middle' font-size='12' "
        f"letter-spacing='1.5' fill='{RED}'>DESIGN</text>",
        f"<text x='{xR}' y='{VB_Y0 + 16}' text-anchor='middle' font-size='12' "
        f"letter-spacing='1.5' fill='{INK}'>PERS.</text>",
        _arrow(xL, yT, v["determination"]["arrow"], RED),
        _arrow(xL, yB, v["environment"]["arrow"], RED),
        _arrow(xR, yT, v["motivation"]["arrow"], INK),
        _arrow(xR, yB, v["perspective"]["arrow"], INK),
    ]
    return "".join(out)


def render(subj):
    defined = set(subj["defined_centers"])
    pers_gates = {p["gate"] for p in subj["personality"].values()}
    des_gates = {p["gate"] for p in subj["design"].values()}
    active = pers_gates | des_gates
    defined_pairs = {frozenset(ch["gates"]) for ch in subj["channels"]}

    vb_h = VIEW_H - VB_Y0
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 {VB_Y0} {VIEW_W} {vb_h}' "
             f"font-family=\"Palatino, Georgia, serif\">"]
    parts.append(f"<rect x='0' y='{VB_Y0}' width='{VIEW_W}' height='{vb_h}' fill='{PAPER}'/>")
    if subj.get("variables"):
        parts.append(_variable_arrows(subj["variables"]))

    # 1. centers (behind everything)
    for name, pts in CENTER_POLY.items():
        if name in defined:
            parts.append(_poly(pts, INK, INK, 1.5))
        else:
            parts.append(_poly(pts, OPEN_FILL, OPEN_STROKE, 2.2))

    # 2. every channel is a full connecting line. Three passes so colored lines
    #    always sit above the faint lattice:
    #      dormant (neither gate active) -> faint full line
    #      hanging gate (one gate active) -> that half colored (ink=Personality,
    #        red=Design), the other half faint
    #      defined (both gates active)   -> solid brass end to end
    def seg(x1, y1, x2, y2, color, w):
        return (f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' "
                f"stroke='{color}' stroke-width='{w}' stroke-linecap='round'/>")

    for a, b, *_ in hd.CHANNELS:
        if frozenset((a, b)) not in defined_pairs:
            (x1, y1), (x2, y2) = GATE_XY[a], GATE_XY[b]
            parts.append(seg(x1, y1, x2, y2, FAINT, 2))
    for a, b, *_ in hd.CHANNELS:
        if frozenset((a, b)) in defined_pairs:
            continue
        (x1, y1), (x2, y2) = GATE_XY[a], GATE_XY[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        for (gx, gy), g in (((x1, y1), a), ((x2, y2), b)):
            if g in active:
                c = RED if (g in des_gates and g not in pers_gates) else INK
                parts.append(seg(gx, gy, mx, my, c, 4))
    for a, b, *_ in hd.CHANNELS:
        if frozenset((a, b)) in defined_pairs:
            (x1, y1), (x2, y2) = GATE_XY[a], GATE_XY[b]
            parts.append(seg(x1, y1, x2, y2, BRASS, 6))

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
            fill, txt, ring = OPEN_FILL, INACTIVE_TXT, INACTIVE_RING
        sw = 3 if (in_p and in_d) else 1.4
        parts.append(f"<circle cx='{x}' cy='{y}' r='{GATE_R}' fill='{fill}' "
                     f"stroke='{ring}' stroke-width='{sw}'/>")
        parts.append(f"<text x='{x}' y='{y + 4.2}' text-anchor='middle' "
                     f"font-size='13' fill='{txt}'>{g}</text>")

    parts.append("</svg>")
    return "".join(parts)
