# human-design

Printable Human Design chart PDF packets, computed with the Swiss Ephemeris and
typeset for paper. One YAML file of birth data in, one Letter-size packet out per
person: a themed BodyGraph, the full Design/Personality activation table, Type /
Strategy / Authority / Profile / Definition / Incarnation Cross, and room for
plain-language interpretation.

Sibling to [`birth-charts`](../birth-charts): same shape (compute → hand-written prose
modules → HTML → Playwright PDF), same de-AI discipline, its own charcoal-indigo/brass
print theme.

## What Human Design is (and isn't)

Human Design is a self-reflective system that maps birth data onto 64 I Ching gates and
9 centers, synthesizing the I Ching, astrology, the chakra system, and the Kabbalah. It
is **not** a science and not a diagnosis or prediction; its founder's own framing was
"don't believe it, experiment with it." The packets say so, plainly. The *astronomy*
here is real and exact; the *interpretation* is offered as reflective language.

## How the chart is computed

- **Personality** (conscious, black) = planetary positions at the birth moment.
- **Design** (unconscious, red) = positions at the moment the Sun was exactly **88° of
  ecliptic longitude** before birth (~88 days), solved by iteration on the real ephemeris.
- Each of 13 points (Sun, Earth, North/South Node, Moon, Mercury…Pluto) on both sides is
  mapped to a **gate (1–64) and line (1–6)** via the Rave Mandala, anchored at
  **Gate 41 = 302.000° (2°00′ Aquarius)**, the Human Design year-start. Nodes are the
  **true** node.
- A **channel** is defined when both its gates are activated; a **center** is defined when
  a defined channel touches it. Type, Authority, Profile, Definition, and the Incarnation
  Cross all derive from that (see `pipeline/hd.py`).

### Provenance & validation

The gate wheel, the 36 channels, the 64 gate→center assignments, and the Type/Authority/
Definition rules are cross-referenced across four independent open-source HD engines
(rave-engine, hdkit, human-design-py, SharpAstrology.HumanDesign) plus published degree
tables. The engine is validated end-to-end against a known-correct published chart:
`pipeline/validate.py` reproduces all 26 activations and every derived property. Run it:

```bash
.venv/bin/python pipeline/validate.py   # expects PASS for true_node
```

## Stack

- [pyswisseph](https://github.com/astrorigin/pyswisseph) (Swiss Ephemeris) for positions
- Pure-Python HD mechanics (`pipeline/hd.py`) and a hand-drawn themed BodyGraph SVG
  (`pipeline/bodygraph.py`)
- HTML + print CSS (`pipeline/style.css`), rendered to PDF by headless Chromium (Playwright)

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium   # if not already present
```

## Use

```bash
mkdir -p work/my-charts
cp subjects.example.yaml work/my-charts/subjects.yaml   # edit with real birth data
.venv/bin/python make.py work/my-charts
```

The first run stops after compute and lists the content modules the work dir still needs.
Write them (start from `pipeline/content_template.py`, follow `pipeline/content_guide.md`
and the keynotes in `pipeline/reference.md`), then run `make.py` again. PDFs land in
`work/my-charts/out/`, or pass `--dest ~/somewhere`.

`work/` is gitignored on purpose: real people's birth data and readings stay local.
