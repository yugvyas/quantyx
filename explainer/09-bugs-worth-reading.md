# 09 — Bugs worth reading

The most useful thing in this folder. Each of these passed a check before it was
caught, and each changed how the project is verified.

---

## 1. The regex that classified "Internal Audit Analyst" as an internship

**What broke.** Term lists were compiled like this:

```python
re.compile(rf"(?<![a-z0-9]){joined}(?![a-z0-9])", re.IGNORECASE)
```

`|` binds loosest in a regex, so that is really:

```
((?<![a-z0-9])intern) | (internship) | (trainee) | ... | (summer analyst(?![a-z0-9]))
```

The lookbehind guards only the first alternative, the lookahead only the last.
Everything between is unguarded.

**Why it mattered.** This ran across every posting on every source. "Internal"
matched "intern". It would have mislabelled thousands of rows, and the seniority
charts would have been quietly wrong forever.

**Fix.** One non-capturing group: `(?:{joined})`.

**Lesson.** It was caught by printing classifier output for a dozen real titles
instead of trusting that the function "looked right". Cheap, and it found a bug
that no type checker or linter would.

---

## 2. `SQL` matching inside `MySQL`

**What broke.** DuckDB uses **RE2**, which has no lookahead. The pattern
`java(?!script)` — the obvious way to avoid matching JavaScript — does not
compile at all.

Worse, unanchored `sql` matches inside "MySQL", "PostgreSQL" and "GraphQL", so
the SQL count would have counted every posting mentioning any of them.

**Fix.** `\b`-anchor everything (RE2 does support `\b`), and verify all 109
patterns compile *and* match correctly before writing any model on top of them.

**Lesson.** Know your regex engine. "It works in Python" is not "it works in
DuckDB".

---

## 3. A workflow that reported success while doing nothing

**What broke.** `ci.yml` had:

```yaml
run: dbt build --vars '{data_dir: ../tests/sample_data}'
```

A plain YAML scalar cannot contain `": "`. The file did not parse.

**Why it was nasty.** GitHub reported a run with **zero jobs and no logs** —
which reads far more like "nothing was triggered" than "your file is broken".

**Fix.** Block scalar (`run: |`), plus `tests/test_workflows.py` — 7 tests that
parse every workflow and assert it has triggers, jobs, `runs-on` and steps. A
malformed workflow now fails locally instead of on GitHub.

---

## 4. The deployment that returned 200 and rendered nothing

**What broke.** GitHub Pages serves a project site under `/<repo>`.
`EVIDENCE_BASE_PATH` was set correctly in the workflow — confirmed present in the
run log — and Evidence 40 ignores it.

Every asset resolved to the domain root and 404'd. The page returned **HTTP 200
and rendered completely unstyled**.

**Fix.** `deployment.basePath: /quantyx` in `evidence.config.yaml`.

**Lesson, and the most important one here.** A 200 proved nothing. `curl` said
success. Only opening the rendered page revealed it. Anything user-facing has to
be *looked at*, not status-checked.

---

## 5. A light theme that could never activate

**What broke.** The light register was written against
`:root[data-appearance="light"]` and `:root.light`. Evidence sets **neither** —
it syncs `html[data-theme]`.

So the entire daylight theme was dead code. And because the shell hides
Evidence's header, its built-in appearance switcher was gone too — there was no
control to reach it with even if the CSS had worked.

**Fix.** Target `html[data-theme='light']`, and build a toggle into the console
rail.

**Lesson.** Found by probing the DOM for what attribute was *actually* set,
rather than trusting the documentation. Two independent bugs were hiding behind
one symptom.

---

## 6. Chart colours indistinguishable to colourblind readers

**What broke.** The first palette put cyan and magenta in adjacent slots. Under
deuteranopia they separate by **ΔE 2.5** — effectively identical.

**Why it mattered.** Roughly 8% of men have some red-green colour deficiency. Two
adjacent series would have been unreadable for them.

**Fix.** Reordering, not recolouring — sand between them. The slot order is now
documented as a safety mechanism so it does not get "tidied".

**Lesson.** This was computed, not eyeballed. Every earlier attempt *looked*
fine.

---

## 7. Charts painted in the exact colour the design refused

**What broke.** The design explicitly refuses the stock SaaS-analytics look,
including its blue accent. Series slot 1 — which paints every single-series chart
on the site — was `#2F6FC4`. A blue. The largest coloured area on two pages was
the thing the design said it was rejecting.

**How it was caught.** An independent reviewer with no knowledge of the build's
reasoning. It is a specific kind of blindness: having *written* the rejection, I
stopped checking whether the build honoured it.

**Fix.** Slot 1 is a deep instrument cyan; blue demoted to slot 6. Re-validated.

---

## 8. A status lamp that could only ever show one state

**What broke.** The gate module hardcoded `state="nominal"` five times. The
module carrying the site's central claim — *it can refuse to publish* — was
physically incapable of rendering the refusal.

**Fix.** The module now states its inference in words (*these ran before this
page published; you are reading it, so they passed*) and shows the halted case
beside the published one. No lamp pretends to be live telemetry.

**Lesson.** Decorative UI that *implies* a capability is worse than no UI. If a
component cannot express the negative case, it is not reporting state.

---

## 9. Chart rows that reordered between identical renders

**What broke.** Queries like `order by posting_count desc` with no tiebreaker.
Equal-count rows came back in different orders on different renders — and with
`limit 25`, different *rows* entirely.

**How it was caught.** A reviewer noticed the bar order differed between the dark
and light screenshots of the same data.

**Why it mattered more than it looks.** On a site whose entire thesis is
deterministic, reproducible publishing, output that changes between runs of
identical data is a correctness bug, not a cosmetic one.

**Fix.** A deterministic secondary sort key on every ranked query. Verified by
rendering the same page twice and comparing pixel hashes — now byte-identical.

---

## 10. A CSS rule that broke two layouts in two different ways

**What broke.** `.markdown p { max-width: 68ch }` applies to *every* paragraph —
including paragraphs that are full-width module rows with their own background.

The plate ended mid-module and the container's rule colour showed through as a
**phantom empty cell**. Fixing it by removing the cap then produced
**100-character lines**, against ~70 everywhere else.

**Fix.** They are two different jobs: the plate spans the module
(`max-width: none`), an inner `span.measure` keeps the text at 68ch.

**Lesson.** The first fix traded a layout defect for a typographic one. Worth
asking, after any fix, what it cost.

---

## What actually caught these

| Method | Found |
| --- | --- |
| Printing real output instead of trusting code | 1 |
| Verifying against the real engine | 2 |
| Parsing config locally before pushing | 3 |
| **Looking at the rendered page** | 4, 10 |
| Probing the DOM for actual state | 5 |
| Running a validator instead of eyeballing | 6 |
| **Independent review with no context** | 7, 8, 9 |

Two patterns stand out.

**A green check is not a working feature.** Bugs 3, 4 and 5 all passed their
checks. The check was measuring the wrong thing.

**You cannot review your own intent.** Bugs 7, 8 and 9 were invisible from inside
the build, because I was checking the work against what I meant rather than what
shipped. Three rounds of review in a fresh context found what re-reading my own
code could not.

---

Next: [10 — Running it yourself](10-running-it-yourself.md).
