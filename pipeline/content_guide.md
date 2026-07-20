# Writing content modules

The pipeline computes everything mechanical (activations, gates, lines, channels, centers,
Type/Authority/Profile/Definition/Cross, the BodyGraph SVG). The prose is yours. Each work
dir needs one `content_<slug>.py` per subject, exposing `build(ctx) -> str` that returns the
packet's body HTML. Start from `content_template.py`. Draw keynotes from `reference.md`, but
never paste them: every sentence is grounded in THIS person's computed chart.

## The ctx dict

| key | what it gives you |
|---|---|
| `data` | full chart-data.json: `data["subjects"][slug]` |
| `activations_table(subj)` | the two-column Design \| Personality activation table (the chart's core) |
| `detail_table(subj, "personality"|"design")` | one side's full detail incl. zodiac position |
| `channels_table(subj)` | the defined channels table |
| `centers_table(subj)` | defined vs open centers, two columns |
| `vitals_strip(subj)` | Type / Authority / Profile / Definition badge strip (cover) |
| `svg_inline(path)` | inline an SVG; the BodyGraph lives at `workdir / "bodygraph-<slug>.svg"` |
| `CENTER_SHORT` | dict of internal center keys → display names |
| `workdir` | Path to the work dir |

### What's in `data["subjects"][slug]`

`name`, `config` (birth data), `birth_utc`, `design_utc`; `type`, `strategy`, `signature`,
`not_self`, `authority`, `profile` (e.g. `"3 / 5"`), `profile_lines`, `profile_names`,
`definition`, `defined_centers`, `open_centers`; `channels` (list of `{gates, name,
centers}`); `active_gates` (`personality`/`design`/`all`); `hanging_gates`; `cross`
(`angle`, `gates` `[pSun,pEarth,dSun,dEarth]`, `key`, `name`); and `personality` / `design`
dicts, each mapping the 13 point names to `{lon, gate, line, sign, deg, glyph, label}`.

## Natal packet structure (keep this order)

1. **Cover** — kicker (`Human Design · BodyGraph · Swiss Ephemeris`), name, birth line,
   `vitals_strip`, the BodyGraph SVG, footer (design date + Signature/Not-Self).
2. **Part One: How to read this chart** — the honest framing (what HD is and isn't), the
   Personality (conscious/black) vs Design (unconscious/red) distinction, and a "three
   things to hold onto" callout naming THIS chart's most load-bearing features (usually
   Type+Strategy, Authority, and the standout Definition/Cross detail).
3. **Part Two: Type & Strategy** — the aura and energy mechanics of this Type, the Strategy
   in plain terms, and the Signature/Not-Self pair as the "is this working?" diagnostic.
   Ground it: name which centers (and motor-to-Throat wiring, or its absence) produce this
   Type for this person.
4. **Part Three: Inner Authority** — how this person is designed to make decisions, named
   from their authority center. Be concrete and practical.
5. **Part Four: Profile** — the two lines (conscious Personality-Sun line / unconscious
   Design-Sun line), what each theme means, and how they combine.
6. **Part Five: Definition & the Centers** — `centers_table`, then a short read of each
   OPEN center (where the person samples/amplifies others and holds potential wisdom, with
   its not-self question) and a note on the Definition type and what bridges it. Open
   centers are as load-bearing as defined ones; give them real space.
7. **Part Six: Channels & Gates** — `channels_table`, then a plain-language read of each
   defined channel (the person's fixed, reliable wiring) and any standout hanging gates.
8. **Part Seven: Incarnation Cross** — the life theme from the four Sun/Earth gates and the
   angle; name the cross if `cross.name` is present, otherwise describe the angle + gates.
9. **Part Eight: Living the design** — the experiment (Strategy + Authority over time,
   deconditioning the open centers), a one-sentence synthesis lead, then 2-3 paragraphs, and
   the methods footer + disclaimer.
10. **Appendix: The activation table** — `activations_table`, a short "reading the table"
    explainer, and optionally the two `detail_table`s with zodiac positions.

## Connection packet (optional add-on)

Only when `connection` is declared in `subjects.yaml` and the user asked for it. Human
Design reads relationships by overlaying two charts: **electromagnetic** channels (each
person has one gate of a channel, together they complete it: attraction), **compromise**
(both have the same whole channel), **dominance** (one person's definition overrides the
other's open center), and **companionship** (both share the same open centers). Lead with
the combined-chart Type/Authority realities, then the channel-level connections. Keep each
person's natal packet self-contained and free of the other person; cross-chart material
lives only in the connection packet.

## Writing rules (non-negotiable)

- **Ground every claim in the computed data.** Name the Type's actual wiring, the specific
  gates/channels/lines, the open vs defined center. Never write a sentence that could sit
  in anyone's chart.
- **Plain language.** Translate every term in the same breath the first time ("your Sacral,
  the life-force center in the middle of the graph, is undefined"). Assume the reader has
  never seen a BodyGraph.
- **Honest, not fatalistic.** No doom, no flattery, no destiny-worship. Open centers are
  gifts-and-vulnerabilities, not flaws. Type is a strategy, not a caste.
- **The de-AI pass is part of the build, not optional.** After drafting, run the `/de-ai`
  checklist over the prose. Specifically hunt:
  - em dashes (banned outright; use commas/periods/parentheses/colons)
  - metaphorical "quietly" + hype adverbs (effortlessly, seamlessly, simply)
  - the correctio pattern ("It is not X; it is Y") — at most one per packet
  - "genuinely / precisely / truly / remarkable / profound" — grep and thin them
  - repeated openers ("This is a person who…", "This is the signature of…")
  - three-item lists stacked in consecutive sentences
  - gate/center keynotes from reference.md pasted verbatim, or identical interpretive
    sentences copied between two packets (shared boilerplate like the method note is fine;
    interpretive sentences are not)
- **Keep the disclaimer.** HD is reflective language, not deterministic science; attribute
  the method honestly (Swiss Ephemeris; 88° solar-arc Design; Rave Mandala anchored at
  Gate 41 = 302°; true node).

## Human Design conventions used

- **The core is Type + Strategy + Authority.** Lead with it; everything else is texture.
  If a reader takes one thing from the packet, it should be their Strategy and Authority.
- **Not-Self theme** (Frustration / Anger / Bitterness / Disappointment, plus the open-center
  conditioning) is the single best "is this landing?" diagnostic; weave it in.
- **Design = unconscious/body, Personality = conscious/mind.** The red side is what the
  person lives out without noticing; the black side is what they identify with.
- **Open centers are where we take in and amplify others** (and, over time, grow wise about
  that theme). Do not frame them as deficits.
- **Attribution:** "Ra Uru Hu / Jovian Archive" and *The Definitive Book of Human Design*
  (Bunnell & Ra Uru Hu) are the defensible sources. Spot-check the specific person's active
  gate keynotes and their exact Incarnation Cross name before delivery.
