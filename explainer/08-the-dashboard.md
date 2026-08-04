# 08 — The dashboard

Built with [Evidence](https://evidence.dev) — a static site generator where pages
are Markdown with embedded SQL, and queries run against parquet in the browser via
DuckDB-WASM. No server, no API, deployable to GitHub Pages.

The full design system is documented in [`DESIGN.md`](../DESIGN.md). This file
covers the reasoning.

## Why the stock theme had to go

Evidence ships a perfectly competent default: grey sidebar, Inter, soft-cornered
cards, blue accent. The problem is that it is *the* default — every Evidence
project looks like that, and a recruiter who has seen one has seen this one.

Underneath sat a machine that re-derives a market every morning and refuses to
publish when its own tests fail. The theme said "someone tried a BI tool".

## The world: a mission-control console

Not a dashboard — a **console watching an unattended machine**, whose headline is
that it can refuse to publish.

Two things were explicitly refused:

- The SaaS-analytics arrangement (sidebar, rounded cards, Inter, blue accent) —
  the category default, and literally what was already there.
- Its predictable opposite, the green-on-black hacker terminal — the obvious
  anti-move, and just as much a cliché for anything data-adjacent.

What shipped instead is institutional: a matte panel machined with faint vertical
rules, modules bolted into the face, live values sunk into recessed wells,
engraved placard capitals against tabular readouts, and status lamps that mean
exactly one thing each.

The direction was chosen from seven candidate worlds derived from the audience's
own culture — split-flap departure boards, strip-chart recorders, broadsheet
market tables, ISO technical drawing standards, cricket scoreboards,
mission-control telemetry, status-page uptime timelines — and the assignment was
rolled rather than picked, specifically so the result would not converge on the
safest option.

### Type

Two self-hosted faces, latin subsets only (412 KB total):

- **Archivo** — placard capitals, tracked `0.14em`, uppercase. The one repeated
  typographic gesture of the world.
- **JetBrains Mono** — every number on the site, with `tabular-nums` so figures
  align in columns.

Monospace here is legitimate: it is for data and measurement, not as a costume
for "technical".

## The palette had to be computed, not chosen

This is the part I would defend hardest.

Chart colours are not a taste decision when they carry meaning. The palette was
run through a validator checking six properties against **this world's actual
surfaces** — not a generic light/dark ground:

- lightness band, chroma floor (does it read as grey?)
- **colour-vision-deficiency separation** between adjacent slots
- normal-vision separation
- contrast against the surface

The first several attempts failed. The instructive one: **cyan and magenta
collide at ΔE 2.5 under deuteranopia** when adjacent — effectively identical to a
red-green colourblind reader. The fix was not new colours but a new *order*: sand
sits between them.

**The slot order is a colourblindness-safety mechanism, not cosmetics.** That is
recorded in `evidence.config.yaml` and in `DESIGN.md` precisely because it looks
arbitrary and would otherwise get "tidied up" by a future contributor.

### Slot 1 is deliberately not blue

Slot 1 paints every single-series chart on the site. A saturated blue there is
exactly the stock accent the design refuses — and for a while, it *was* that blue,
making the Skills and Companies plots read as default Evidence charts sitting
inside a console frame.

Slot 1 is now a deep instrument cyan; blue is demoted to slot 6, where six
concurrent series would have to be on screen before it appears.

Final palette: **all checks pass in both registers with no warnings.**

### Status colours are reserved

Nominal green, caution amber and fault red are **never** used as a chart series.
And lamps always carry a word *and* a drawn glyph — never colour alone, so the
state survives colourblindness and greyscale printing.

## Making caution mean something

For several iterations the lamp system had three states and used one. Everything
was green; amber appeared only as an editorial callout.

There was a truthful machine condition available: `assert_volume_not_collapsed`
compares against a trailing seven-day average, so it genuinely does nothing until
seven days of history exist — and there are two.

That check now shows `DORMANT` in amber, with a note saying it "passes without
testing anything". It is true, it is specific, it disarms itself automatically at
seven days, and it makes the third lamp state real rather than decorative.

## Two registers

Dark is the default — it is a console. Light is authored separately as a
**printed plot board**, not an inverted panel: white modules on a machined grey
ground, ochre caution, darker traces, its own validated palette steps.

Both registers were measured in-browser for contrast: body text **7.5:1 dark /
7.4:1 light**, placards 14–18:1, readouts 15:1 — all comfortably above the 4.5:1
requirement.

## Structure

The front page is one scrolling argument rather than six equal pages behind a
sidebar. Above the fold: the last-run readout, four individually lamped ingest
channels, and the four pre-publish checks. Generic counts sit *below* the board —
they are context, not proof.

Skills, Compensation, Companies, Postings and Method remain as deep pages for
anyone who wants to dig.

## Charts obey their data

- **Compensation is never blended.** One chart per currency-and-period, each on
  its own axis. Dividing a USD/year salary by twelve to compare it against an
  INR/month stipend produces a chart that is confidently wrong.
- **Skill trends are a share, not a count.** As the registry grows the absolute
  number rises for reasons that have nothing to do with the market.
- **Every chart that can legitimately be empty is guarded** with an explanatory
  message. The sample dataset has no early-career postings, and day one of any
  real deployment has no trend — both would otherwise 500 the strict build.
- **Every ranked query has a deterministic secondary sort key.** Without one,
  equal-count rows reordered between renders. On a site whose thesis is
  deterministic publishing, that is a correctness bug. Two independent renders are
  now byte-identical.

## Review

The design went through three rounds of independent finish review, each in a
fresh context with no knowledge of the reasoning behind the build. It caught the
stock-blue series, the fake verdict lamps, and the unstable sort ordering.

Details in [09 — Bugs worth reading](09-bugs-worth-reading.md).

---

Next: [09 — Bugs worth reading](09-bugs-worth-reading.md).
