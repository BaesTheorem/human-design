"""The Human Design Variable / Primary Health System (PHS) layer: the four arrows and
the five transformations (Determination/Digestion, Cognition/Sense, Environment,
Motivation, Perspective).

Derivation (cross-referenced against Jovian Archive + dturkuler/humandesign_api; see
reference.md and the SKILL notes):
  Determination (Digestion) = COLOR of the Design Sun
  Cognition   (Design Sense) = TONE  of the Design Sun
  Environment                = COLOR of the Design Nodes
  Motivation                 = COLOR of the Personality Sun
  Perspective (View)         = COLOR of the Personality Nodes
  Each of the four arrows = TONE of its point: tone 1-3 -> Left, 4-6 -> Right.
  (Sun and Earth, and North and South Node, share identical colour/tone, so node
  polarity does not matter.)

This is the most birth-time-sensitive layer in HD: a tone changes about every 38
minutes, a colour about every 3.8 hours. Present with that caveat.
"""

DETERMINATION = {1: "Appetite", 2: "Taste", 3: "Thirst", 4: "Touch", 5: "Sound", 6: "Light"}
COGNITION = {1: "Smell", 2: "Taste", 3: "Outer Vision", 4: "Inner Vision",
             5: "Feeling", 6: "Touch"}
ENVIRONMENT = {1: "Caves", 2: "Markets", 3: "Kitchens", 4: "Mountains",
               5: "Valleys", 6: "Shores"}
MOTIVATION = {1: "Fear", 2: "Hope", 3: "Desire", 4: "Need", 5: "Guilt", 6: "Innocence"}
PERSPECTIVE = {1: "Survival", 2: "Possibility", 3: "Power", 4: "Wanting",
               5: "Probability", 6: "Personal"}

# tone <=3 -> Left, else Right; each arrow's two orientations are named per PHS
ARROW_LABELS = {  # arrow key: (left-label, right-label)
    "motivation": ("Strategic", "Receptive"),     # Personality Sun tone  (the "Mind")
    "perspective": ("Focused", "Peripheral"),      # Personality Node tone (the "View")
    "determination": ("Active", "Passive"),        # Design Sun tone       (the "Brain")
    "environment": ("Observed", "Observer"),       # Design Node tone      (the "Body")
}


def _arrow(tone):
    return "left" if tone <= 3 else "right"


def _mode(key, tone):
    left, right = ARROW_LABELS[key]
    return left if tone <= 3 else right


def compute(subj):
    ds = subj["design"]["Sun"]
    dn = subj["design"]["NorthNode"]
    ps = subj["personality"]["Sun"]
    pn = subj["personality"]["NorthNode"]

    out = {
        "determination": {"color": ds["color"], "tone": ds["tone"],
                          "name": DETERMINATION[ds["color"]],
                          "mode": _mode("determination", ds["tone"]),
                          "arrow": _arrow(ds["tone"])},
        "cognition": {"tone": ds["tone"], "name": COGNITION[ds["tone"]]},
        "environment": {"color": dn["color"], "tone": dn["tone"],
                        "name": ENVIRONMENT[dn["color"]],
                        "mode": _mode("environment", dn["tone"]),
                        "arrow": _arrow(dn["tone"])},
        "motivation": {"color": ps["color"], "tone": ps["tone"],
                       "name": MOTIVATION[ps["color"]],
                       "mode": _mode("motivation", ps["tone"]),
                       "arrow": _arrow(ps["tone"])},
        "perspective": {"color": pn["color"], "tone": pn["tone"],
                        "name": PERSPECTIVE[pn["color"]],
                        "mode": _mode("perspective", pn["tone"]),
                        "arrow": _arrow(pn["tone"])},
    }
    ar = {k: ("L" if out[k]["arrow"] == "left" else "R")
          for k in ("motivation", "perspective", "determination", "environment")}
    out["short_code"] = f"P{ar['motivation']}{ar['perspective']} D{ar['determination']}{ar['environment']}"
    return out
