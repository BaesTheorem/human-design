"""Assemble packet HTML from chart-data.json plus the work dir's content modules.

Usage: python pipeline/build.py work/<dir>

Expects in the work dir: chart-data.json, bodygraph-<slug>.svg (from compute.py),
and content_<slug>.py per subject (written by hand; see content_guide.md). Each
content module defines build(ctx) -> body HTML string.

Writes work/<dir>/out/<slug>.html.
"""
import html as htmllib
import importlib.util
import json
import sys
from pathlib import Path

import hd

REPO = Path(__file__).resolve().parent.parent
CSS = (REPO / "pipeline" / "style.css").read_text()

# Chart order matches the published bodygraph column: Sun, Earth, Nodes, Moon, planets.
CHART_ORDER = ["Sun", "Earth", "NorthNode", "SouthNode", "Moon", "Mercury", "Venus",
               "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
SIGN_GLYPH = {"Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋", "Leo": "♌",
              "Virgo": "♍", "Libra": "♎", "Scorpio": "♏", "Sagittarius": "♐",
              "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓"}
GLYPH_CHARS = "♈♉♊♋♌♍♎♏♐♑♒♓☉⊕☽☿♀♂♃♄♅♆♇☊☋◀▶"


def activations_table(subj):
    """The two-column Design (unconscious) | Personality (conscious) activation table,
    the heart of the published chart: each planet's gate.line on both sides."""
    des, pers = subj["design"], subj["personality"]
    rows = []
    for name in CHART_ORDER:
        d, p = des[name], pers[name]
        rows.append(
            f"<tr><td class='num red'>{d['gate']}.{d['line']}</td>"
            f"<td class='gl'>{d['glyph']}</td>"
            f"<td>{p['label']}</td>"
            f"<td class='gl'>{p['glyph']}</td>"
            f"<td class='num'>{p['gate']}.{p['line']}</td></tr>")
    return ("<table class='data activ'><thead><tr>"
            "<th class='num red'>Design</th><th></th><th>Planet</th><th></th>"
            "<th class='num'>Personality</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def detail_table(subj, which):
    """One side's full detail: planet, gate.line, and zodiac position (for the appendix)."""
    side = subj[which]
    rows = []
    for name in CHART_ORDER:
        p = side[name]
        rows.append(f"<tr><td class='gl'>{p['glyph']}</td><td>{p['label']}</td>"
                    f"<td class='num'>{p['gate']}.{p['line']}</td>"
                    f"<td class='gl'>{SIGN_GLYPH[p['sign']]}</td>"
                    f"<td>{p['deg']:.2f}° {p['sign']}</td></tr>")
    head = "Personality (conscious · birth)" if which == "personality" \
        else "Design (unconscious · 88° before birth)"
    return (f"<table class='data'><thead><tr><th></th><th>{head}</th>"
            "<th>Gate.Line</th><th></th><th>Zodiac</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def channels_table(subj):
    if not subj["channels"]:
        return "<p class='muted'>No fully-defined channels (all centers open).</p>"
    rows = []
    for ch in subj["channels"]:
        a, b = ch["gates"]
        ca, cb = (CENTER_SHORT.get(c, c) for c in ch["centers"])
        rows.append(f"<tr><td class='num'>{a}-{b}</td><td>{ch['name']}</td>"
                    f"<td class='muted'>{ca} ↔ {cb}</td></tr>")
    return ("<table class='data'><thead><tr><th>Gates</th><th>Channel</th>"
            "<th>Connects</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


CENTER_SHORT = {"Head": "Head", "Ajna": "Ajna", "Throat": "Throat", "G": "G",
                "Ego": "Ego", "Sacral": "Sacral", "SolarPlexus": "Solar Plexus",
                "Spleen": "Spleen", "Root": "Root"}


def gates_list(subj):
    """Every activated gate: number, keynote name, and which planets (Design in red,
    Personality in ink) switch it on. Hanging gates are flagged."""
    rev = {}
    for side, key in (("d", "design"), ("p", "personality")):
        for pname, p in subj[key].items():
            rev.setdefault(p["gate"], {"d": [], "p": []})[side].append(p["glyph"])
    hanging = set(subj["hanging_gates"])
    rows = []
    for g in subj["active_gates"]["all"]:
        acts = rev.get(g, {"d": [], "p": []})
        d = f"<span class='red'>{' '.join(acts['d'])}</span>" if acts["d"] else ""
        p = " ".join(acts["p"])
        tag = " <span class='muted'>· hanging</span>" if g in hanging else ""
        rows.append(f"<tr><td class='num'>{g}</td><td>{hd.GATE_NAMES.get(g, '')}{tag}</td>"
                    f"<td class='gl'>{d}</td><td class='gl'>{p}</td></tr>")
    return ("<table class='data'><thead><tr><th>Gate</th><th>Keynote</th>"
            "<th class='gl red'>Design</th><th class='gl'>Pers.</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def channels_full_list(subj):
    """Defined channels as a labeled list, with the two centers each bridges."""
    if not subj["channels"]:
        return "<p class='muted'>No fully-defined channels.</p>"
    items = []
    for ch in subj["channels"]:
        a, b = ch["gates"]
        ca, cb = (CENTER_SHORT.get(c, c) for c in ch["centers"])
        items.append(f"<li><b>{a}-{b} {ch['name']}</b> · {hd.GATE_NAMES.get(a)} + "
                     f"{hd.GATE_NAMES.get(b)} · <span class='muted'>{ca} ↔ {cb}</span></li>")
    return f"<ul class='channels'>{''.join(items)}</ul>"


ARROW_CHAR = {"left": "◀", "right": "▶"}


def variables_table(subj):
    """The five transformations as labeled rows: Design side (red) then Personality."""
    v = subj.get("variables")
    if not v:
        return ""
    def row(side, label, name, mode, arrow, detail):
        arr = f"<span class='sub'>{ARROW_CHAR[arrow]} {mode}</span>" if arrow else ""
        return (f"<div class='varrow {side}'><div class='vk'>{label}</div>"
                f"<div class='vv'>{name} {arr} <span class='sub'>{detail}</span></div></div>")
    rows = [
        row("design", "Digestion", v["determination"]["name"], v["determination"]["mode"],
            v["determination"]["arrow"], "how you take things in · Design Sun colour"),
        row("design", "Design Sense", v["cognition"]["name"], "", None,
            "the sense you trust · Design Sun tone"),
        row("design", "Environment", v["environment"]["name"], v["environment"]["mode"],
            v["environment"]["arrow"], "where you thrive · Design Node colour"),
        row("pers", "Motivation", v["motivation"]["name"], v["motivation"]["mode"],
            v["motivation"]["arrow"], "what moves you · Personality Sun colour"),
        row("pers", "Perspective", v["perspective"]["name"], v["perspective"]["mode"],
            v["perspective"]["arrow"], "how you see · Personality Node colour"),
    ]
    return (f"<div class='vars'>{''.join(rows)}</div>"
            f"<p class='muted' style='font-size:8.5pt'>Four-arrow code: "
            f"<b>{v['short_code']}</b> (Personality Mind/View, Design Brain/Body; "
            f"◀ left = active/focused, ▶ right = receptive/peripheral).</p>")


def vitals_strip(subj):
    """Compact Type / Authority / Profile / Definition badge strip for the cover."""
    cells = [("Type", subj["type"]), ("Authority", subj["authority"].split(" (")[0]),
             ("Profile", subj["profile"]), ("Definition", subj["definition"].replace(" Definition", ""))]
    inner = "".join(f"<div><div class='lbl'>{k}</div><div class='val'>{v}</div></div>"
                    for k, v in cells)
    return f"<div class='vitals'>{inner}</div>"


def centers_table(subj):
    """Defined vs open centers, two columns."""
    def col(title, items):
        lis = "".join(f"<li>{CENTER_SHORT.get(c, c)}</li>" for c in items) or "<li class='muted'>none</li>"
        return f"<div><div class='ttl'>{title}</div><ul class='centerlist'>{lis}</ul></div>"
    return (f"<div class='cols2'>{col('Defined (consistent)', subj['defined_centers'])}"
            f"{col('Open (conditioned · wisdom)', subj['open_centers'])}</div>")


def force_text_glyphs(html):
    VS = "︎"
    for ch in GLYPH_CHARS:
        html = html.replace(ch, ch + VS)
    return html.replace(VS + VS, VS)


def page(title, body):
    parts, rest = [], body
    while "<svg" in rest:
        pre, rest = rest.split("<svg", 1)
        svg, rest = rest.split("</svg>", 1)
        parts.append(force_text_glyphs(pre))
        parts.append("<svg" + svg + "</svg>")
    parts.append(force_text_glyphs(rest))
    return (f"<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<title>{htmllib.escape(title)}</title>\n<style>{CSS}</style></head>"
            f"<body>{''.join(parts)}</body></html>")


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    workdir = Path(sys.argv[1]).resolve()
    data = json.loads((workdir / "chart-data.json").read_text())
    outdir = workdir / "out"
    outdir.mkdir(exist_ok=True)

    ctx = {
        "data": data, "workdir": workdir,
        "activations_table": activations_table, "detail_table": detail_table,
        "channels_table": channels_table, "vitals_strip": vitals_strip,
        "gates_list": gates_list, "channels_full_list": channels_full_list,
        "variables_table": variables_table,
        "centers_table": centers_table, "CENTER_SHORT": CENTER_SHORT,
        "SIGN_GLYPH": SIGN_GLYPH,
        "svg_inline": lambda p: (s := Path(p).read_text())[s.index("<svg"):],
    }

    for slug, subj in data["subjects"].items():
        mod_path = workdir / f"content_{slug}.py"
        if not mod_path.exists():
            print(f"skip {slug}: no {mod_path.name}")
            continue
        body = load_module(mod_path).build(ctx)
        (outdir / f"{slug}.html").write_text(page(f"Human Design — {subj['name']}", body))
        print(f"built {slug}.html")


if __name__ == "__main__":
    main()
