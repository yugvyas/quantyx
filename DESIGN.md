---
name: quantyx
description: A mission-control console for an unattended machine that would rather publish nothing than publish something wrong.
colors:
  # --- Console register (the default; appearance.default is `dark`) ---
  panel-void: "#0a0f11"
  panel: "#101619"
  panel-raised: "#172024"
  panel-inset: "#0c1214"
  rule: "#24343a"
  rule-strong: "#354a52"
  ink: "#e6edef"
  ink-dim: "#9fb2b9"
  ink-faint: "#6e848c"
  lamp-nominal: "#46c08a"
  lamp-caution: "#e8a33d"
  lamp-fault: "#e8615a"
  lamp-off: "#2c3a40"
  # --- Daylight register (html[data-theme='light']) ---
  panel-void-light: "#d7dde0"
  panel-light: "#e8ecee"
  panel-raised-light: "#ffffff"
  panel-inset-light: "#dde3e6"
  rule-light: "#b6c1c6"
  rule-strong-light: "#83949b"
  ink-light: "#12191c"
  ink-dim-light: "#47585f"
  ink-faint-light: "#6b7a80"
  lamp-nominal-light: "#157f4f"
  lamp-caution-light: "#8a5a00"
  lamp-fault-light: "#b3261e"
  lamp-off-light: "#c3ccd0"
  # --- Instrument traces: categorical series, assigned in fixed slot order ---
  series-1: "#3799B8"
  series-2: "#B8863F"
  series-3: "#C4548E"
  series-4: "#8E6FE0"
  series-5: "#2FA396"
  series-6: "#2F6FC4"
  series-1-light: "#0E7FA3"
  series-2-light: "#A66A00"
  series-3-light: "#C2317F"
  series-4-light: "#6D3FD6"
  series-5-light: "#00897B"
  series-6-light: "#1B62C9"
  # --- Sequential scale: one hue, identical in both registers ---
  scale-from: "#CFE6EF"
  scale-to: "#0B3F52"
  # --- Evidence-internal theme colors (evidence.config.yaml theme.colors) ---
  evidence-primary: "#5C9BE8"
  evidence-primary-light: "#1B62C9"
  evidence-accent: "#D9A441"
  evidence-accent-light: "#A66A00"
  evidence-chart-ground: "#101619"
  evidence-chart-ground-light: "#e8ecee"  # aligned to panel-light; see The Chart Ground Rule
typography:
  display:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(1.6rem, 3vw, 2.5rem)"
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "normal"
  body:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: "normal"
  body-small:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "normal"
  placard:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.6875rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.14em"
  placard-section:
    fontFamily: "Archivo, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.16em"
  readout-lead:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, monospace"
    fontSize: "2.75rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontFeature: "tnum 1"
  readout:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, monospace"
    fontSize: "1.75rem"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontFeature: "tnum 1"
  data:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, monospace"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "-0.02em"
    fontFeature: "tnum 1"
rounded:
  none: "0"
  hairline: "2px"
spacing:
  seam: "1px"
  tight: "0.4rem"
  xs: "0.5rem"
  sm: "0.625rem"
  md: "0.875rem"
  lg: "1rem"
  xl: "1.5rem"
  block: "1.75rem"
  section: "3rem"
components:
  module:
    backgroundColor: "{colors.panel-raised}"
    rounded: "{rounded.hairline}"
    padding: "0"
  well:
    backgroundColor: "{colors.panel-inset}"
    textColor: "{colors.ink}"
    rounded: "{rounded.hairline}"
    padding: "0.875rem 1rem 1rem"
  readout-well:
    backgroundColor: "{colors.panel-inset}"
    textColor: "{colors.ink}"
    typography: "{typography.readout}"
    rounded: "{rounded.hairline}"
    padding: "0.875rem 1rem 1rem"
  readout-well-lead:
    typography: "{typography.readout-lead}"
  placard-label:
    textColor: "{colors.ink-dim}"
    typography: "{typography.placard}"
  action-primary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.hairline}"
    padding: "0.75rem 1rem"
  action-primary-hover:
    backgroundColor: "{colors.lamp-caution}"
    textColor: "{colors.panel-void}"
  station:
    backgroundColor: "transparent"
    textColor: "{colors.ink-faint}"
    typography: "{typography.placard}"
    rounded: "{rounded.hairline}"
    padding: "0.4rem 0.7rem"
  station-active:
    backgroundColor: "{colors.panel-inset}"
    textColor: "{colors.ink}"
  lamp-switch:
    backgroundColor: "transparent"
    textColor: "{colors.ink-faint}"
    rounded: "{rounded.hairline}"
    height: "2rem"
    width: "2rem"
  lamp-switch-hover:
    textColor: "{colors.lamp-caution}"
  channel-cell:
    backgroundColor: "{colors.panel-raised}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "0.875rem 1rem 1rem"
  caution-plate:
    backgroundColor: "{colors.panel-inset}"
    textColor: "{colors.ink-dim}"
    typography: "{typography.body}"
    rounded: "{rounded.hairline}"
    padding: "0.875rem 1.125rem"
  input-search:
    backgroundColor: "{colors.panel-inset}"
    textColor: "{colors.ink}"
    typography: "{typography.data}"
    rounded: "{rounded.hairline}"
  table-header-cell:
    textColor: "{colors.ink-dim}"
    typography: "{typography.placard}"
    padding: "0.55rem 0.875rem"
---

# Design System: quantyx

## Overview

**Creative North Star: "The Unattended Console"**

This is not a dashboard. It is the face of an instrument that ran at 02:30 UTC without a human present, and the single most important thing it has to say is that it is willing to refuse to publish. Every visual decision serves that reading. The surface is a matte console panel machined with faint vertical rules; modules are bolted into its face; live values are sunk into recessed wells; labels are engraved placard capitals cut into hairline rules. Numbers are set in a tabular monospace because a readout is a different kind of object from a sentence, and the two never wear each other's clothes.

The world refuses two opposites at once. It refuses the SaaS-card arrangement Evidence ships by default — sidebar, rounded cards, Inter, a saturated blue accent — which is why the shell hides Evidence's entire chrome (`hideSidebar`, `hideHeader`, `hideBreadcrumbs`, `hideTOC`, `builtWithEvidence={false}`) and rebuilds the rail, the footer and the type from scratch. It equally refuses the terminal cliché that a "console" invites: there are no scanlines, no glow, no green-on-black, no ASCII art, no blinking cursors. Depth comes from three stepped ground values and hairline rules, never from a drop shadow.

Density is high and deliberately unpadded — this is an operations panel, not a marketing page — but the prose inside it stays at a 68-character measure and reads plainly. The product's voice ("hedges and caveats are content, not clutter to be designed away") is load-bearing on the visual system: caution plates, dormant lamps and "what these numbers do not say" modules are first-class furniture with real estate, not fine print.

**Key Characteristics:**
- Matte console panel with faint vertical machining, three stepped grounds, zero shadows for elevation
- Engraved placard capitals (Archivo 600, tracked 0.14em) against tabular readouts (JetBrains Mono)
- A single 2px radius everywhere; the corner is a machined chamfer, not a rounded card
- Status lamps in exactly three states, reserved for state, never used decoratively or as chart color
- Modules separated by 1px seams of rule color, not by gaps
- One authored motion moment on the whole site

## Colors

Two authored registers: a console panel (the default) and a printed plot board (the daylight variant). The daylight register is not an inversion of the panel; it is its own set of values, and it is selected on `html[data-theme='light']` only.

### Primary

The console has no "brand accent" in the usual sense. Its primary chromatic voice is the **caution amber** lamp hue, which does double duty as the interface's one attention color.

- **Caution Amber** (`{colors.lamp-caution}` / `{colors.lamp-caution-light}`): the lamp for a real caution state, and — sparingly — the interface's accent of last resort: the tick under the station designation rule, the scale tick on the board's lead readout, the wordmark glyph, the keyboard focus ring, the primary action's border and hover fill. It is never used to make something look nice.

### Secondary

- **Instrument Cyan** (`{colors.series-1}` / `{colors.series-1-light}`): slot 1 of the categorical ramp and therefore the color of every single-series chart on the site. It is the site's de-facto data color.
- **Oxide Sand** (`{colors.series-2}` / `{colors.series-2-light}`), **Instrument Magenta** (`{colors.series-3}`), **Violet** (`{colors.series-4}`), **Teal** (`{colors.series-5}`), **Blue** (`{colors.series-6}`): slots 2 through 6, assigned in fixed order, never cycled or resampled.

### Tertiary

- **Nominal Green** (`{colors.lamp-nominal}` / `{colors.lamp-nominal-light}`): a channel reporting, a check armed, a run published.
- **Fault Red** (`{colors.lamp-fault}` / `{colors.lamp-fault-light}`): a halted deploy. It appears exactly once in the built surface — the "Halted" outcome plate on the status board — because that is the only place the system currently has a fault to show.
- **Lamp Off** (`{colors.lamp-off}` / `{colors.lamp-off-light}`): a channel that contributed nothing this run. Deliberately achromatic: silence is an absence, not an alarm.

### Neutral

Depth is carried entirely by four stepped ground values plus two rule weights.

- **Panel Void** (`{colors.panel-void}` / `{colors.panel-void-light}`): the `body` ground, behind everything, visible only past the console shell.
- **Panel** (`{colors.panel}` / `{colors.panel-light}`): the console face itself, carrying the vertical machining texture. This is `.console-shell`.
- **Panel Raised** (`{colors.panel-raised}` / `{colors.panel-raised-light}`): a module bolted into the face — every `.module`, board, channel cell, step row, limit plate and verify cell.
- **Panel Inset** (`{colors.panel-inset}` / `{colors.panel-inset-light}`): a recessed well — where live values sit, plus the rail, the footer, table row hover, inline code and caution plates.
- **Rule** (`{colors.rule}` / `{colors.rule-light}`): the engraved hairline. Module borders, row dividers, and the 1px seams between grid cells.
- **Rule Strong** (`{colors.rule-strong}` / `{colors.rule-strong-light}`): a structural edge — rail bottom, footer top, station designation underline, table header underline, scale ticks, the primary-action-adjacent borders.
- **Ink** (`{colors.ink}` / `{colors.ink-light}`): primary legend. Headings, readout values, table cells, active station.
- **Ink Dim** (`{colors.ink-dim}` / `{colors.ink-dim-light}`): body prose, placards at rest, intros, table headers.
- **Ink Faint** (`{colors.ink-faint}` / `{colors.ink-faint-light}`): scale ticks, units, annotations, inactive stations, provenance notes.

Measured in-browser on the built pages, both registers: body prose 7.5:1 (console) and 7.4:1 (daylight), placards 14–18:1, readouts 15:1. All pass 4.5:1 comfortably.

> **Ground truth note.** The `--ink-dim` annotations in `dashboard/static/console.css` originally named the wrong ground (`--panel`, where prose does not sit) and understated the ratio. They now read 7.5:1 / 7.4:1 against `--panel-raised`, matching the in-browser measurements in this document.

### Named Rules

**The Reserved Lamp Rule.** The three status hues (`lamp-nominal`, `lamp-caution`, `lamp-fault`) exist only to report machine state. They are never a chart series, never a decorative highlight, never a "brand" gradient. And a lamp never carries meaning in color alone: `StatusLamp` always ships an engraved word *and* a drawn SVG glyph (check / triangle / cross / dash). Color is confirmation, not the message.

**The Slot Order Rule.** The categorical palette's slot order is a CVD-safety mechanism, not taste. Oxide sand sits between instrument cyan and magenta because those two collide at ΔE 2.5 under deuteranopia when adjacent. The full ramp was validated with the dataviz validator against *this world's actual surfaces* (`{colors.panel}` console ground / `{colors.evidence-chart-ground-light}` plot board), not a generic white: every check passes in both registers with no warnings — worst adjacent CVD ΔE 13.0 in both, worst adjacent normal-vision ΔE 15.5 console / 18.7 daylight. **Do not reorder, insert, drop or resample a slot without re-running the validator against both grounds.**

**The No Stock Blue Rule.** Slot 1 is a deep instrument cyan and deliberately *not* a blue. Slot 1 paints every single-series chart on the site, and a saturated blue there is exactly the stock accent this world's thesis refuses — it made the Skills and Companies plots read as default Evidence charts wearing a console frame. Blue is demoted to slot 6, where six concurrent series would have to be on screen before it appears.

**The One-Hue Scale Rule.** The sequential scale is one hue, light to dark (`{colors.scale-from}` → `{colors.scale-to}`), cyan to match the categorical ramp's lead. It is identical in both registers. Never a rainbow, never a diverging ramp for non-diverging data.

**The `data-theme` Rule.** Light mode is selected on `html[data-theme='light']` and nothing else. Evidence sets that attribute and sets no class and no `data-appearance`; targeting anything else makes the entire daylight register dead code that no switcher can ever reach. The rail's own `.lamp-switch` sets the attribute directly, because Evidence's built-in switcher lives in the header that this shell hides. Setting the attribute is the supported path — Evidence observes `html[data-theme]` and syncs its store from it.

## Typography

**Display / Body Font:** Archivo (with `ui-sans-serif, system-ui, sans-serif`)
**Readout / Mono Font:** JetBrains Mono (with `ui-monospace, "SF Mono", monospace`)

Both are self-hosted from `dashboard/static/fonts/`, latin + latin-ext subsets, `font-display: swap`, declared in `fonts.css`. Archivo ships weights 400/500/600/700; JetBrains Mono ships 400/500/700. The two subsets actually used above the fold (`Archivo-5.woff2`, weight 600 latin; `JetBrainsMono-1.woff2`, weight 400 latin) are preloaded in the shell. No webfont CDN is contacted.

**Character:** Archivo is a grotesque with a tight, mechanical vertical stress — it engraves cleanly at small tracked capitals and holds its shape at display size without ever looking editorial. JetBrains Mono is the machine's own hand: every figure the same width, so a column of counts is a column, not ragged text. The pairing is the world's whole argument in two typefaces: one says what a thing *is*, the other says how *much*.

`body` sets `font-feature-settings: "tnum" 1` globally, so even Archivo-set numbers stay tabular.

### Hierarchy

- **Display** (Archivo 700, `clamp(1.6rem, 3vw, 2.5rem)`, line-height 1.08, tracking -0.035em, `max-width: 22ch`, `text-wrap: balance`): the status board's headline on the index page. Exactly one per site.
- **Headline** (Archivo 700, 1.5rem, tracking -0.025em): `h1.title` — the station designation on the five deep pages. Evidence auto-renders the frontmatter `title` into this element; it is underlined with a `rule-strong` hairline and ticked with a 2.5rem `lamp-caution` segment at its left edge.
- **Title** (Archivo 600, 0.8125rem–0.9375rem): a module's own name — channel names, the footer byline, the wordmark (0.9375rem/700, tracking 0.02em).
- **Body** (Archivo 400, 0.9375rem, line-height 1.7, `max-width: 68ch`): all prose. `Panel`'s `intro` runs slightly narrower at 62ch.
- **Body Small** (Archivo 400, 0.8125rem, line-height 1.6): in-module explanatory copy — outcome plates, verify cells, coverage notes, dormant notes.
- **Placard** (Archivo 600, 0.6875rem, tracking 0.14em, uppercase, `ink-dim`): the one repeated typographic gesture of the world. Every label on every well, module, step, table header and rail item.
- **Placard, section** (Archivo 600, 0.75rem, tracking 0.16em, uppercase, `ink`): `Panel`'s own heading, cut into an engraved rule. Slightly larger and slightly more tracked than the everyday placard, which is the entire hierarchy signal.
- **Readout, lead** (JetBrains Mono 700, 2.75rem → 2.25rem below 640px, line-height 1): the board's headline figure. One per page at most.
- **Readout** (JetBrains Mono 500, 1.75rem, line-height 1): the standard value in a well. Channel counts run at 1.25rem, the last-run stamp at 1.125rem.
- **Data** (JetBrains Mono 400, 0.8125rem, tabular-nums, tracking -0.02em): every table, inline `code`, search input and test name.

### Named Rules

**The Two Voices Rule.** Archivo says what a thing is; JetBrains Mono says how much there is. A number never appears in Archivo (units and notes beside a value are Archivo on purpose — they are words, not quantities). Prose never appears in mono. There is no third face.

**The Placard-Is-The-Label Rule.** A placard is the section's own label, never an eyebrow stacked above a separate heading. `Panel` renders its `label` *as* the `h2`; if you find yourself writing a placard and a heading that say the same thing, delete the heading.

**The Engraved Identity Rule.** Nothing identifies itself by color alone. The active station in the rail gets an inset ground and a `rule-strong` border, not a tint. `h1.title` gets a rule and a tick. This is the type system's half of the Reserved Lamp Rule.

## Layout

**Frame.** One container, `max-width: 78rem`, centred, `padding-inline: 1.5rem` (1rem below 640px in the main frame, below 800px in the rail, below 560px implicitly in the footer). The rail, the main content and the footer all share the same 78rem measure so their edges agree down the page. The shell is `EvidenceDefaultLayout` with `fullWidth={true}` and every piece of its chrome disabled; all real layout happens inside the `content` slot.

**Vertical rhythm.** `main` runs `padding-top: 2.5rem` / `padding-bottom: 6rem`. Sections are separated by the engraved rule's own margin: `3rem` above, `1rem` below. Inside a module, block padding is `0.875rem–1rem`; between grouped modules it is `1.75rem`.

**The seam grid.** Module groups — the tallies row, the channel strip, the limits list, the verify grid, the scale row, the GO/NO-GO verdict pair — are CSS grids with `gap: 1px` over a `rule`-colored background and a 1px `rule` border. The seam *is* the rule. Cells inside these groups have their own borders, radii and shadows stripped (`border: 0; border-radius: 0; box-shadow: none`) so the group reads as one machined plate subdivided, not as a row of separate cards.

**Responsive.** Breakpoints are per-component and chosen where the content actually breaks, not from a global scale. Observed: 1000px (tallies 5→3, verify 3→1), 900px (scale 5→3), 860px (channel strip 4→2, coverage 3→2, postings tallies 4→2), 800px (rail collapses to a `Stations` disclosure panel), 780px (board head 2-col→1-col), 640px (steps and limits drop their label column, verdict 2→1, lead readout shrinks), 560px (footer repo path hides), 460/420px (remaining grids →1 column). Verified: zero horizontal overflow on all six pages at 1440px and at a true 390px viewport.

### Named Rules

**The Measure Rule.** `.markdown p` caps every paragraph at 68ch. When a paragraph is itself a full-width module row with its own background, the *plate* must span the module (`max-width: none`) while an inner `<span class="measure">` (`display: inline-block; max-width: 68ch`) keeps the text readable. Two different jobs: uncapping the paragraph alone produces 100-character lines; leaving the cap on ends the row's background mid-module and leaks the container's rule color through as a phantom cell. Both failure modes have already been hit here — see `TheGate.svelte` and `compensation.md`.

**The Seam Rule.** Related modules are separated by a 1px seam of rule color, never by whitespace and never by a shadow. If two things need to look like part of the same instrument, put them in a seam grid.

**The Shared Measure Rule.** Rail, content and footer all sit at 78rem with the same 1.5rem gutter. A new full-width band must adopt both or it will visibly disagree with everything above it.

## Elevation & Depth

**There are no elevation shadows.** Not one `box-shadow` in this system lifts anything off the page. Depth is entirely tonal: four stepped ground values (`panel-void` → `panel` → `panel-raised` → `panel-inset`) plus two rule weights, read as *machining* rather than as floating. A module is raised because it is lighter than the face it is bolted to; a well is recessed because it is darker.

The only shadow in the system is an inset one, and it is a bevel, not a lift: `.well` carries `inset 0 1px 0` of 40% black in the console register, softened to `inset 0 1px 2px` of 8% black in daylight. It reads as the top lip of a cut-out.

The console face additionally carries a `repeating-linear-gradient(90deg, ...)` at a 4px pitch — a 1px stripe of 18%-mixed rule color every 4px — which is the faint vertical machining. It is texture, not a pattern anyone should notice.

### Named Rules

**The Three Grounds Rule.** The daylight register's ground values are stepped *further* apart than a naive light theme would space them, because the whole "a module bolted into the console face" reading is carried by that separation. In an earlier tighter light palette the module boundary collapsed to a single 1px rule and the depth story disappeared. If you add a ground value, keep the steps visibly distinct in light before you check dark.

**The No-Lift Rule.** Nothing hovers. If something needs to feel prominent, change its ground, its rule weight or its tick color. Never add a drop shadow, and never add `transform: translateY()` on hover.

## Shapes

One radius, everywhere: **2px** (`{rounded.hairline}`). Modules, wells, buttons, inputs, code spans, blockquotes, focus rings and the rail's controls all use it. It is not a rounded corner in the SaaS sense — at 2px it reads as a machined chamfer on a metal plate. Cells inside a seam grid drop to `0` so the plate's outer corner is the only one visible; the tallies row under the board uses `0 0 2px 2px` so it fuses with the board's flat bottom edge.

Borders are the primary shape tool: a 1px `rule` hairline for ordinary module edges, a 1px `rule-strong` for structural edges. Two shapes carry meaning through an asymmetric border: the **caution plate** (a full `rule` border with its `border-left` swapped to `lamp-caution`) and the **station designation** (`h1.title`, a `rule-strong` bottom border with a 2.5rem `lamp-caution` segment overlaid at its left edge). The **scale tick** — a 1.75rem × 2px bar flush to the top edge of every `Readout` well, `rule-strong` normally and `lamp-caution` on the lead value — is the world's smallest recurring form.

Iconography is line-drawn SVG on a 12–16px viewBox at `stroke-width: 1.25`–`1.5`, square line caps, `fill: none`, `stroke: currentColor`. Everything is drawn inline; there is no icon font and no icon package.

**The Square Cap Rule.** Icon strokes end square, not round. A rounded cap softens the instrument and none of the glyphs in the system use one (except the mode-switch moon's `stroke-linejoin: round`, where the crescent needs it).

## Components

### Buttons

- **Shape:** machined chamfer (2px), 1px border, transparent or inset ground.
- **Primary action** (`.action`): a bordered plate in `lamp-caution`, transparent ground, `ink` label in Archivo 600 at 0.8125rem, uppercase, tracked 0.06em, `padding: 0.75rem 1rem`, with a `→` glyph pushed to the far edge by `justify-content: space-between`. This is the repository link — the board's single primary action, sitting at the status board's right.
- **Hover:** the plate fills with `lamp-caution` and the label inverts to `panel-void`, over 140ms `ease-out`. No lift, no scale.
- **Wide variant** (`.action-wide`): same plate, but the label is set in JetBrains Mono at its natural case — because the label is a URL, and a URL is a readout.
- **Rail toggle** (`.rail-toggle`, ≤800px only): raised ground, `rule-strong` border, placard type, the word `Stations` / `Close`.
- **Focus:** every focusable element gets `outline: 2px solid var(--lamp-caution); outline-offset: 2px` via `:focus-visible`. The focus ring is a lamp, and it is never removed.

### Cards / Containers

There are no cards. There are **modules** and **wells**.

- **Module** (`.module`, and every hand-rolled equivalent): `panel-raised` ground, 1px `rule` border, 2px radius. Internal padding `0.875rem–1.125rem` block, `1rem–1.25rem` inline.
- **Well** (`.well`): `panel-inset` ground, 1px `rule` border, 2px radius, plus the inset top-lip bevel. Wells hold live values and nothing else.
- **Board** (`.board` on the index): the one oversized module — `rule-strong` border, `panel-raised` ground, containing the headline, the state well, the primary action, and two bolted-in sub-modules each behind its own engraved placard.
- **Shadow strategy:** none. See Elevation & Depth.

### Inputs / Fields

Evidence's `DataTable search` input, rebuilt as a console control: `panel-inset` ground, 1px `rule-strong` border, 2px radius, JetBrains Mono at 0.8125rem, `ink-faint` placeholder. Focus swaps to a 2px `lamp-caution` outline at `outline-offset: 1px` and keeps the border. All of this is applied with `!important` because it is overriding Evidence's own component styles.

### Navigation

- **Rail** (`ConsoleRail`): sticky to the top at `z-index: 40`, `panel-inset` ground, `rule-strong` bottom border, 3.25rem tall, on the shared 78rem frame. Left: the wordmark with a 16px drawn crosshair-in-square mark in `lamp-caution`. Right: the register switch, then six stations.
- **Stations:** placard type, `ink-faint` at rest, `padding: 0.4rem 0.7rem`, transparent border.
- **Hover:** `ink` label, `rule` border appears. 140ms `ease-out`.
- **Active:** `ink` label, `panel-inset` ground, `rule-strong` border, `aria-current="page"`. Engraved, not tinted.
- **Path matching** normalizes trailing slashes and strips the SvelteKit `base`, because trailing slashes differ between `evidence dev` and the static build and the active station would otherwise silently fall through on the deployed site.
- **Mobile (≤800px):** stations collapse into a full-width disclosure panel below the rail, driven by `aria-expanded`/`aria-controls`, with rows at `0.85rem 1rem` separated by `rule` top borders.

### Status Lamp (signature)

The world's defining component. Three live states plus an off state, each rendered as **an engraved word and a drawn glyph** in the state's hue: `nominal` (circle + check), `caution` (triangle + bang), `fault` (circle + cross), `off` (circle + dash, in achromatic `lamp-off`). The word is overridable — the built surface uses `Live`/`Silent` on channels, `Armed`/`Dormant` on checks, `Published`/`Halted` on outcomes — but it is never *absent*. A `compact` variant drops the word to 0.625rem for in-row use.

### Readout (signature)

A single live quantity sunk into a well: engraved placard label, tabular value, an optional Archivo-set unit held apart from the number so the figure stays scannable, and an optional note line for provenance. A 1.75rem × 2px scale tick sits flush to the well's top edge — `rule-strong` normally, `lamp-caution` when `lead` is set. Values are formatted through `toLocaleString('en-IN')` and null/empty renders as an em dash, never as `0` or `NaN`.

This is deliberately *not* the big-number stat card. The well, the engraved label and the scale tick are what make it belong here; a borderless number with a small grey caption underneath would be the generic thing this world refuses.

### Channel Strip (signature)

Four ingest channels in a seam grid, each individually lamped. The four channels are declared in the component, not derived from the data, so a channel that reported nothing still renders — as a `Silent` off-lamp with a count of 0. That is the point: a source that disappears must be visible as an absence, which is exactly what `assert_no_source_disappeared` watches for. 4 → 2 columns at 860px, → 1 at 460px.

### The Gate (signature)

The status board's verdict module (`TheGate.svelte`): a placard head, four check rows each naming its dbt test in mono with a plain-language "what it watches" line and an `Armed`/`Dormant` lamp, then a two-up outcome plate showing `Published` (nominal) and `Halted` (fault) side by side, then a proof line.

> **Ground truth note.** Despite the component's name and the direction contract's "GO/NO-GO poll", this module does **not** render a live GO/NO-GO verdict, and that is intentional and documented in the file: a build that fails the gate never reaches a browser, so lamps that could only ever read GO would be decoration. What it shows instead is which checks are armed, plus both outcomes as a worked example. The one genuinely conditional lamp is the volume check, which goes `caution` / `Dormant` until seven days of history exist, with the reason printed beside it. This is the only place in the built surface where a caution lamp reflects live state.

### Footer

`panel-inset` ground, `rule-strong` top border, the 78rem frame at 1.5rem padding, wrapping flex. Left: a `Built by` placard and the byline. Right: a repository plate — raised ground, `rule-strong` border, inline GitHub mark, a `Source` placard and the URL in mono. Hover swaps the border to `lamp-caution` and the ground to `panel`. The mono URL hides below 560px; the plate and its label do not.

### Markdown surface

Because pages are Evidence Markdown, the stylesheet re-dresses the default elements rather than wrapping them: `blockquote` becomes a caution plate (inset ground, `lamp-caution` left border, no italic — blockquotes are how these pages state their limits, so they get the caution treatment rather than a decorative bar); `code` becomes an inset mono chip; `table` becomes a printed data listing with left-aligned cells, placard-set headers and a `panel-inset` row hover. Evidence's own `DataTable` lives in `.table-container`, whose margins are zeroed so the markdown-table rules do not leak in and stack with the engraved rule into the largest interval on the page. Chart wrappers are forced transparent so plots sit in the panel rather than on a white sheet.

## Do's and Don'ts

### Do:

- **Do** keep `deployment.basePath: /quantyx` in `evidence.config.yaml`. Evidence 40 does **not** honour the `EVIDENCE_BASE_PATH` environment variable; without the config value the GitHub Pages project site returns 200 and renders **completely unstyled**, because every `/_app/...` request 404s. Any asset URL you add must go through `base` from `$app/paths` for the same reason.
- **Do** select the daylight register on `html[data-theme='light']` and nowhere else, and keep the rail's `.lamp-switch` as the way a visitor reaches it — Evidence's own switcher is in the header this shell hides.
- **Do** give every ranked query a deterministic secondary sort key (`order by posting_count desc, canonical_skill`). Without one, equal-count rows reorder between renders; on a site whose entire thesis is deterministic publishing, that is a correctness defect, not a cosmetic one. Two independent renders of the same page are byte-identical by pixel hash *after* this fix — keep it that way.
- **Do** hide `h1.title` with route-scoped CSS on the index only. Evidence auto-renders the frontmatter title into `h1.title`; on the index the board carries its own headline, so the heading is redundant there and is suppressed inside `index.md`'s own `<style>` block. SvelteKit only loads a route's CSS for that route, which is what keeps it off the five deep pages where `h1.title` is the real station designation. Never move that rule into `console.css`.
- **Do** give a full-width paragraph row `max-width: none` on the plate and an inner `span.measure` at 68ch for the text.
- **Do** ship a word and a glyph with every lamp, and re-run the dataviz validator against both grounds before touching the categorical palette.
- **Do** put new module groups in a 1px seam grid over `rule`, and strip the child's own border/radius/shadow.
- **Do** state a limit as furniture — a caution plate, a lamp, a dormant note — rather than as small grey text at the bottom.

### Don't:

- **Don't** add a second animation. Motion is exactly one authored moment: a 620ms `cubic-bezier(0.16, 1, 0.3, 1)` power-on (6px rise + fade) applied to `.board` on the index and nowhere else, disabled under `prefers-reduced-motion` — which additionally clamps every animation and transition on the site to 0.01ms. State changes get a 140ms `ease-out` color/border transition; that is the whole vocabulary.
- **Don't** reorder, resample or extend the categorical palette without re-running the validator. Oxide sand is between cyan and magenta for a reason (ΔE 2.5 under deuteranopia when those two are adjacent).
- **Don't** put a status hue on a chart series, and don't put an instrument-trace hue on a lamp.
- **Don't** make slot 1 a blue. Blue is slot 6 and the demotion is the point.
- **Don't** add a drop shadow, a hover lift, a gradient fill or a radius above 2px.
- **Don't** un-hide Evidence's sidebar, header, breadcrumbs, TOC or "Built with Evidence" badge, and don't reintroduce Inter — the shell's job is to prevent the default SaaS-card arrangement from reasserting itself.
- **Don't** reach for the terminal cliché the word "console" invites: no scanlines, no CRT glow, no green-on-black, no monospace prose, no blinking cursor, no ASCII borders.
- **Don't** remove the direction contract from `pages/+layout.svelte`. It is injected as raw markup via `{@html}` specifically because Svelte strips ordinary HTML comments at compile time; it is the first HTML comment in every built page and is meant to stay auditable in the shipped output.
- **Don't** use a placard as an eyebrow above a separate heading, and don't set a number in Archivo or a sentence in JetBrains Mono.

---

*Scanned from the built surface at `dashboard/`: `static/console.css`, `evidence.config.yaml`, `pages/+layout.svelte`, the six pages, and the seven components. `dashboard/app.css` is imported by the layout but does not exist in source — it resolves against Evidence's generated template at `.evidence/template/src/app.css` at build time. Machine-readable extensions (tonal ramps, shadow and motion tokens, breakpoints, renderable component snippets, narrative) live in `.impeccable/design.json`.*
