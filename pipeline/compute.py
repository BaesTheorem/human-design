"""Compute a Human Design chart from birth data and write chart-data.json + a
themed bodygraph SVG per subject.

Usage: python pipeline/compute.py work/<dir>

Reads work/<dir>/subjects.yaml (same birth-data shape as the astrology pipeline):

    subjects:
      - slug: alexander
        name: Alexander
        year: 1994
        month: 5
        day: 29
        hour: 1          # 24h local time
        minute: 27
        city: San Antonio
        nation: US
        lat: 29.4241
        lng: -98.4936
        tz: America/Chicago

All astronomy is Swiss Ephemeris (pyswisseph). The Design side is taken at the
moment the Sun was exactly 88° of ecliptic longitude before birth. Nodes are TRUE
node (validated against published charts). See pipeline/hd.py for the mechanics.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import swisseph as swe
import yaml

import hd

REPO = Path(__file__).resolve().parent.parent
CROSSES = json.loads((REPO / "pipeline" / "crosses.json").read_text()) \
    if (REPO / "pipeline" / "crosses.json").exists() else {}

# HD chart order. Earth and South Node are the exact opposites of Sun / North Node.
PLANETS = [("Sun", swe.SUN), ("Earth", None), ("NorthNode", swe.TRUE_NODE),
           ("SouthNode", None), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
           ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
           ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
           ("Pluto", swe.PLUTO)]
PLANET_GLYPH = {"Sun": "☉", "Earth": "⊕", "NorthNode": "☊", "SouthNode": "☋",
                "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
                "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇"}
PLANET_LABEL = {"NorthNode": "North Node", "SouthNode": "South Node"}
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED


def jd_ut(dt_utc):
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600)


def lon(jd, body):
    return swe.calc_ut(jd, body, FLAGS)[0][0] % 360.0


def design_jd(birth_jd):
    """Moment the Sun was exactly 88° of longitude before birth (~88.1 days)."""
    target = (lon(birth_jd, swe.SUN) - 88.0) % 360.0
    guess = birth_jd - 88.0 * 365.2422 / 360.0
    for _ in range(60):
        diff = (lon(guess, swe.SUN) - target + 180) % 360 - 180
        if abs(diff) < 1e-9:
            break
        guess -= diff / 0.985647
    return guess


def activation(jd):
    """The 13 activations at a moment: longitude + gate/line/sign for each point."""
    lons = {}
    for name, body in PLANETS:
        if name == "Earth":
            L = (lons["Sun"] + 180) % 360
        elif name == "SouthNode":
            L = (lons["NorthNode"] + 180) % 360
        else:
            L = lon(jd, body)
        lons[name] = L
    out = {}
    for name, _ in PLANETS:
        L = lons[name]
        g, ln = hd.gate_line(L)
        out[name] = {"lon": round(L, 4), "gate": g, "line": ln,
                     "sign": SIGNS[int(L // 30)], "deg": round(L % 30, 2),
                     "glyph": PLANET_GLYPH[name], "label": PLANET_LABEL.get(name, name)}
    return out


def compute_subject(cfg):
    local = datetime(cfg["year"], cfg["month"], cfg["day"], cfg["hour"],
                     cfg.get("minute", 0), tzinfo=ZoneInfo(cfg["tz"]))
    utc = local.astimezone(ZoneInfo("UTC"))
    b_jd = jd_ut(utc)
    d_jd = design_jd(b_jd)
    d_y, d_mo, d_d, d_h = swe.revjul(d_jd)

    pers = activation(b_jd)
    des = activation(d_jd)

    active = ({v["gate"] for v in pers.values()} | {v["gate"] for v in des.values()})
    pers_gates = {v["gate"] for v in pers.values()}
    des_gates = {v["gate"] for v in des.values()}
    chans = hd.defined_channels(active)
    cents = hd.defined_centers(chans)
    open_cents = [c for c in hd.CENTERS if c not in cents]

    t = hd.hd_type(cents, chans)
    strategy, signature, not_self = hd.TYPE_META[t]
    au = hd.authority(cents, chans)
    p_line, d_line = pers["Sun"]["line"], des["Sun"]["line"]
    profile = f"{p_line} / {d_line}"
    angle = hd.cross_angle(p_line, d_line)
    quad = [pers["Sun"]["gate"], pers["Earth"]["gate"],
            des["Sun"]["gate"], des["Earth"]["gate"]]
    cross_key = f"{quad[0]}/{quad[1]}|{quad[2]}/{quad[3]}"
    cross_entry = CROSSES.get(cross_key) or {}
    cross_name = cross_entry.get("name") if isinstance(cross_entry, dict) else cross_entry

    # hanging gates: activated but their channel partner is not (per center)
    channel_gates = {g for a, b, *_ in chans for g in (a, b)}
    hanging = sorted(g for g in active if g not in channel_gates)

    return {
        "name": cfg["name"], "config": cfg,
        "birth_utc": str(utc), "design_utc": f"{d_y:04d}-{d_mo:02d}-{d_d:02d} "
        f"{int(d_h):02d}:{int((d_h % 1) * 60):02d} UTC",
        "personality": pers, "design": des,
        "type": t, "strategy": strategy, "signature": signature, "not_self": not_self,
        "authority": au, "profile": profile, "profile_lines": [p_line, d_line],
        "profile_names": [hd.PROFILE_LINE[p_line], hd.PROFILE_LINE[d_line]],
        "definition": hd.definition(cents, chans),
        "defined_centers": sorted(cents, key=list(hd.CENTERS).index),
        "open_centers": sorted(open_cents, key=list(hd.CENTERS).index),
        "channels": [{"gates": [a, b], "name": n, "centers": [ca, cb]}
                     for a, b, n, ca, cb in chans],
        "active_gates": {"personality": sorted(pers_gates), "design": sorted(des_gates),
                         "all": sorted(active)},
        "hanging_gates": hanging,
        "cross": {"angle": angle, "gates": quad, "key": cross_key, "name": cross_name},
    }


def main():
    workdir = Path(sys.argv[1]).resolve()
    cfg = yaml.safe_load((workdir / "subjects.yaml").read_text())
    data = {"subjects": {}}
    for c in cfg["subjects"]:
        data["subjects"][c["slug"]] = compute_subject(c)
    if cfg.get("connection"):
        data["connection"] = {"pair": cfg["connection"]}
    (workdir / "chart-data.json").write_text(json.dumps(data, indent=1, default=str))

    # bodygraph SVGs (import here so a missing bodygraph module doesn't block compute)
    try:
        import bodygraph
        for slug, s in data["subjects"].items():
            svg = bodygraph.render(s)
            (workdir / f"bodygraph-{slug}.svg").write_text(svg)
    except Exception as e:
        print(f"  (bodygraph SVG skipped: {e})")

    for slug, s in data["subjects"].items():
        print(f"{slug}: {s['type']} · {s['authority']} · Profile {s['profile']} · "
              f"{s['definition']} · Cross {s['cross']['angle']} {s['cross']['gates']}")


if __name__ == "__main__":
    main()
