"""Skeleton for a Human Design content module. Copy to work/<dir>/content_<slug>.py
and write. Replace SLUG/NAME and every [TODO] with prose grounded in chart-data.json.
See content_guide.md for the section contract and writing rules, reference.md for keynotes.
"""


def build(ctx):
    d = ctx["data"]["subjects"]["SLUG"]
    bodygraph = ctx["svg_inline"](ctx["workdir"] / "bodygraph-SLUG.svg")
    variables = ctx["variables_table"](d)
    gates_list = ctx["gates_list"](d)
    channels_list = ctx["channels_full_list"](d)
    activ = ctx["activations_table"](d)
    centers = ctx["centers_table"](d)
    channels = ctx["channels_table"](d)
    cross = d["cross"]
    cross_line = (f"{cross['angle']} Cross of {cross['name']} "
                  if cross.get("name") else f"{cross['angle']} Cross ")
    cross_line += f"({cross['gates'][0]}/{cross['gates'][1]} | {cross['gates'][2]}/{cross['gates'][3]})"

    return f"""
<div class="cover">
  <div class="kicker">Human Design · BodyGraph · Swiss Ephemeris</div>
  <h1>NAME</h1>
  <div class="birthdata">[TODO: date · time · city · coordinates]</div>
  <hr class="rule">
  {ctx["vitals_strip"](d)}
  <div class="bodygraphwrap">{bodygraph}</div>
  <div class="foot">Signature: {d['signature']} · Not-Self: {d['not_self']} · Design: {d['design_utc']}</div>
</div>

<section class="pb">
<h2><span class="no">Part One</span>How to Read This Chart</h2>
<p class="lead">[TODO: one-sentence orientation to this specific chart.]</p>
<p>Human Design maps the moment of your birth onto sixty-four gates and nine energy
centers. Two calculations feed the graph: your <b>Personality</b> (the black numbers, taken
at your birth minute, the conscious "you" your mind identifies with) and your <b>Design</b>
(the red numbers, taken at the moment the Sun sat 88 degrees earlier in the sky, about
three months before birth, the unconscious body you live out without noticing). [TODO:
adapt.]</p>
<div class="callout"><div class="ttl">Three things to hold onto</div>
<p><b>1. [TODO: Type + Strategy].</b> [TODO]</p>
<p><b>2. [TODO: Authority].</b> [TODO]</p>
<p><b>3. [TODO: the standout Definition / Cross detail].</b> [TODO]</p></div>
</section>

<section class="pb">
<h2><span class="no">Part Two</span>Type &amp; Strategy</h2>
<h3>{d['type']} <span class="tag">Strategy · {d['strategy']}</span></h3>
<p>[TODO: aura + energy mechanics; name the wiring that makes this the Type, e.g. defined/
undefined Sacral and whether a motor reaches the Throat.]</p>
<p>[TODO: the Strategy in plain, practical terms.]</p>
<div class="callout"><div class="ttl">The compass</div>
<p><b>Signature (on track): {d['signature']}.</b> [TODO] <b>Not-Self (off track):
{d['not_self']}.</b> [TODO: use this as the daily diagnostic.]</p></div>
</section>

<section class="pb">
<h2><span class="no">Part Three</span>Inner Authority</h2>
<h3>{d['authority']}</h3>
<p>[TODO: how this person is designed to decide; concrete and practical.]</p>
</section>

<section class="pb">
<h2><span class="no">Part Four</span>Profile: {d['profile']}</h2>
<p class="lead">{d['profile_names'][0]} (conscious) / {d['profile_names'][1]} (unconscious).</p>
<p>[TODO: the two line themes and how they combine.]</p>
</section>

<section class="pb">
<h2><span class="no">Part Five</span>Definition &amp; the Centers</h2>
<p>[TODO: one line on the {d['definition']} and what bridges it.]</p>
{centers}
<h3>Your open centers</h3>
<!-- One short read per OPEN center: where you sample/amplify others, the not-self
     question, the wisdom on offer. Open centers are gifts, not deficits. -->
<div class="entry"><h3>[TODO: open center]</h3><p>[TODO]</p></div>
</section>

<section class="pb">
<h2><span class="no">Part Six</span>Channels &amp; Gates</h2>
<p class="lead">Channels are your fixed wiring: the traits that are consistently "on"
because both of their gates are activated.</p>
{channels}
<!-- One .entry per defined channel; note standout hanging gates too. -->
<div class="entry"><h3>[TODO: channel]</h3><p>[TODO]</p></div>
</section>

<section class="pb">
<h2><span class="no">Part Seven</span>Incarnation Cross</h2>
<h3>{cross_line}</h3>
<p>[TODO: the life theme from the four Sun/Earth gates and the {cross['angle']} angle.]</p>
</section>

<section class="pb">
<h2><span class="no">Part Eight</span>The Variables</h2>
<p class="lead">The advanced layer: how the body takes in food, information, and place.
Handle this one lightly.</p>
<p>[TODO: one paragraph flagging Color/Tone, the four arrows, and that this is the most
birth-time-sensitive layer (a Tone shifts ~40 min, a Color ~4 hr), meant to be lived last.]</p>
{variables}
<!-- Short reads grounded in d["variables"]: Digestion+Sense (Design Sun), Environment
     (Design Node), Motivation + Perspective (Personality). Keynotes in reference.md; do
     not overclaim beyond the color keynote. -->
<div class="entry"><h3>[TODO]</h3><p>[TODO]</p></div>
</section>

<section class="pb">
<h2><span class="no">Part Nine</span>Living the Design</h2>
<p class="lead">If the chart were a single sentence: [TODO].</p>
<p>[TODO: the experiment, deconditioning the open centers, 2-3 paragraphs.]</p>
<p class="footer-note">Calculated with the Swiss Ephemeris. Design taken at 88° of solar
arc before birth; gates mapped on the Rave Mandala anchored at Gate 41 = 302° (2° Aquarius);
true node. Human Design is a self-reflective system that synthesizes the I Ching, astrology,
the chakras, and the Kabbalah; it is not scientifically validated and is not a diagnosis or
a prediction. In the words of its founder, the invitation is not to believe any of it but to
experiment and keep only what proves true in your own experience.</p>
</section>

<section class="pb">
<h2><span class="no">Part Ten</span>Gates &amp; Channels</h2>
<p class="lead">The full inventory: every gate switched on, and the channels where two
join into fixed wiring.</p>
<h3>Defined channels</h3>
{channels_list}
<h3>All activated gates</h3>
{gates_list}
</section>

<section class="pb">
<h2><span class="no">Appendix</span>The Activation Table</h2>
<p class="lead">Every gate and line in this packet, both sides of the chart.</p>
{activ}
<p>Read each row from the center out: the <span style="color:#9a4a3c">red</span> Design
value on the left (unconscious), the planet in the middle, the black Personality value on
the right (conscious). "16.3" means Gate 16, Line 3.</p>
</section>
"""
