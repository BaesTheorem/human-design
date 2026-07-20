"""Validate the compute engine against a known-correct published chart
(aHumanDesign.com screenshot for Alexander, 29 May 1994 01:27 San Antonio TX).
Golden vector: every one of the 26 activations plus all derived properties.
Run: .venv/bin/python pipeline/validate.py
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

import hd

# --- ephemeris ------------------------------------------------------------

PLANETS = [  # HD chart order; Earth and South Node are derived opposites
    ("Sun", swe.SUN), ("Earth", None), ("NorthNode", swe.TRUE_NODE),
    ("SouthNode", None), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
    ("Pluto", swe.PLUTO),
]
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED


def jd_ut(dt_utc):
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def lon(jd, body):
    return swe.calc_ut(jd, body, FLAGS)[0][0] % 360.0


def activations(jd, node=swe.TRUE_NODE):
    out = {}
    for name, body in PLANETS:
        if name == "Earth":
            L = (out["Sun"] + 180) % 360
        elif name == "SouthNode":
            L = (out["NorthNode"] + 180) % 360
        else:
            b = node if name == "NorthNode" else body
            L = lon(jd, b)
        out[name] = L
    return out


def design_jd(birth_jd):
    """Moment the Sun was exactly 88° of longitude earlier than at birth."""
    target = (lon(birth_jd, swe.SUN) - 88.0) % 360.0
    guess = birth_jd - 88.0 * 365.2422 / 360.0  # ~88 days
    for _ in range(60):
        cur = lon(guess, swe.SUN)
        diff = (cur - target + 180) % 360 - 180
        if abs(diff) < 1e-9:
            break
        guess -= diff / 0.985647  # Sun ~0.9856°/day
    return guess


# --- golden vector --------------------------------------------------------

EXPECT_PERS = {"Sun": (16, 3), "Earth": (9, 3), "NorthNode": (43, 6), "SouthNode": (23, 6),
               "Moon": (41, 1), "Mercury": (15, 3), "Venus": (39, 1), "Mars": (27, 3),
               "Jupiter": (28, 5), "Saturn": (63, 1), "Uranus": (61, 6), "Neptune": (61, 3),
               "Pluto": (14, 3)}
EXPECT_DES = {"Sun": (37, 5), "Earth": (40, 5), "NorthNode": (14, 3), "SouthNode": (8, 3),
              "Moon": (48, 5), "Mercury": (49, 6), "Venus": (22, 4), "Mars": (30, 1),
              "Jupiter": (1, 2), "Saturn": (55, 4), "Uranus": (61, 5), "Neptune": (61, 2),
              "Pluto": (14, 4)}
EXPECT = {"type": "Projector", "authority": "Emotional (Solar Plexus)",
          "definition": "Split Definition", "profile": "3 / 5",
          "cross": "Right Angle", "cross_gates": (16, 9, 37, 40)}


def run(node_name, node_const):
    local = datetime(1994, 5, 29, 1, 27, tzinfo=ZoneInfo("America/Chicago"))
    utc = local.astimezone(ZoneInfo("UTC"))
    b_jd = jd_ut(utc)
    d_jd = design_jd(b_jd)

    pers = activations(b_jd, node_const)
    des = activations(d_jd, node_const)
    pg = {k: hd.gate_line(v) for k, v in pers.items()}
    dg = {k: hd.gate_line(v) for k, v in des.items()}

    ok = True
    print(f"\n=== node = {node_name} ===")
    print(f"design date: {swe.revjul(d_jd)}  (birth utc {utc})")
    for label, got, exp in (("PERS", pg, EXPECT_PERS), ("DES", dg, EXPECT_DES)):
        for name, _ in PLANETS:
            g = got[name]
            e = exp[name]
            mark = "" if g == e else "  <-- MISMATCH"
            if g != e:
                ok = False
            print(f"  {label:4} {name:10} {g[0]}.{g[1]}   expect {e[0]}.{e[1]}{mark}")

    # derived
    active = {g for g, l in pg.values()} | {g for g, l in dg.values()}
    chans = hd.defined_channels(active)
    cents = hd.defined_centers(chans)
    t = hd.hd_type(cents, chans)
    au = hd.authority(cents, chans)
    de = hd.definition(cents, chans)
    prof = f"{pg['Sun'][1]} / {dg['Sun'][1]}"
    ang = hd.cross_angle(pg["Sun"][1], dg["Sun"][1])
    quad = (pg["Sun"][0], pg["Earth"][0], dg["Sun"][0], dg["Earth"][0])

    def chk(label, got, exp):
        nonlocal ok
        m = "" if got == exp else f"  <-- expect {exp}"
        if got != exp:
            ok = False
        print(f"  {label:12} {got}{m}")

    print("  --- derived ---")
    chk("type", t, EXPECT["type"])
    chk("authority", au, EXPECT["authority"])
    chk("definition", de, EXPECT["definition"])
    chk("profile", prof, EXPECT["profile"])
    chk("cross angle", ang, EXPECT["cross"])
    chk("cross gates", quad, EXPECT["cross_gates"])
    print(f"  defined centers: {sorted(cents)}")
    print(f"  channels: {[(a, b, n) for a, b, n, ca, cb in chans]}")
    print(f"\n  {'PASS' if ok else 'FAIL'} for node={node_name}")
    return ok


if __name__ == "__main__":
    r_true = run("TRUE_NODE", swe.TRUE_NODE)
    r_mean = run("MEAN_NODE", swe.MEAN_NODE)
    print(f"\n\nSUMMARY: true_node={'PASS' if r_true else 'FAIL'} "
          f"mean_node={'PASS' if r_mean else 'FAIL'}")
