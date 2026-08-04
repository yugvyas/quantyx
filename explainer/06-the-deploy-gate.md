# 06 — The deploy gate

## The failure this project is built around

It is not a crash. A crash is easy: the run fails, nothing publishes, you get an
email.

The failure that matters is **a source that breaks quietly**. An API starts
returning an empty list. A field gets renamed upstream and silently becomes
`NULL`. A company's board token goes stale. Nothing errors. The pipeline runs
happily, the dashboard rebuilds, and it publishes a collapse in the Indian job
market that never happened.

A dashboard that confidently reports a market crash caused by its own bug is
worse than one that stops.

## The four tripwires

In `dbt/tests/`. Any of them returning a row fails `dbt build`, which halts the
workflow **before** the deploy step.

### `assert_volume_not_collapsed`

Today's observation count against its trailing seven-day average. Catches a
source that starts returning nothing.

It **no-ops until seven days of history exist**, because before that there is no
trailing average to compare against. This is not a fudge — it is stated on the
dashboard's front page, where that check currently shows a caution lamp reading
`DORMANT` with a note explaining it passes without testing anything. A green lamp
that means nothing is worse than an amber one that is honest.

### `assert_no_source_disappeared`

Any source seen in the trailing window but absent from the latest run.

This exists because the volume test cannot see it. When the drift-detection
script kills one channel, it drops **2 rows out of 92** — a 2% change that
disappears entirely into the volume test's noise, while the source test catches it
immediately. Two tests, two genuinely different failure modes.

### `assert_required_fields_present`

Per-source, on the latest partition only: are `url`, `title` and `company` still
populated for every row?

Scoped to the latest partition deliberately. A column-level `not_null` test would
fire on the whole table and then stay red forever because of older good data — so
it would be permanently broken and therefore permanently ignored.

### `assert_compensation_is_coherent`

Pay figures that cannot be true: `min > max`, missing currency or period,
non-positive amounts. Guards the salary charts against silently skewed
distributions.

## Proving the gate actually works

A test that has never been observed failing is not evidence of anything.

`scripts/verify_drift_detection.sh` runs in CI on every pull request. It:

1. Copies the sample dataset, **guts the latest day** down to one row per source,
   and asserts `assert_volume_not_collapsed` **fails**.
2. Copies it again, **deletes the least common source** so total volume barely
   moves, and asserts `assert_no_source_disappeared` **fails**.
3. Runs both against the clean dataset and asserts they **pass** — because a test
   that fires on healthy data is just noise.

If any of those three expectations is violated, the script exits non-zero and CI
goes red.

```
=== Verifying drift detection ===

  simulated collapse: 92 -> 3 observations
  ok  assert_volume_not_collapsed correctly failed
  simulated dead source: dropped 'lever' (2 rows)
  ok  assert_no_source_disappeared correctly failed
  ok  both tests pass on healthy data

=== Drift detection verified ===
```

That second line is the one worth pausing on: 2 rows of 92. That is the case the
volume test structurally cannot catch, caught.

## What failure looks like to a visitor

Nothing dramatic. The workflow stops before the deploy step, opens or comments on
a single rolling GitHub issue, and **leaves the previous dashboard live**.

So the visible symptom of a failure is a *stale* page, not a wrong one. That
trade is deliberate and is stated on the front page:

> Any one of them returning a row stops the deploy, files an issue, and leaves
> the previous dashboard live — so a stale page, not a wrong one, is what failure
> looks like here.

## One honest limitation

The gate module on the dashboard does **not** poll a live system. It cannot: a
static site has no running backend to ask.

What it does instead is state its inference explicitly — *these four ran before
this page was published; you are reading it, therefore they passed* — and show
the halted case beside the published one as a worked example.

An earlier version rendered four green "GO" lamps. That was removed, because a
lamp physically incapable of showing anything but GO is decoration pretending to
be telemetry, on the one module carrying the site's central claim.

---

Next: [07 — Automation](07-automation.md).
