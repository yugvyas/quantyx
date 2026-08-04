# 01 — What this is and why

## The problem

If you want to know what the Indian data/AI job market actually asks for — which
skills, at what level, for what pay — there is no good public answer. There are
opinion pieces, there are job boards you can scroll, and there are "top 10
skills" listicles with no method behind them.

The underlying data exists. It is spread across job APIs, it changes daily, and
nobody is measuring it in a way you can check.

## The goal

Measure it, in public, every day, in a way that anyone can verify.

That last clause is the whole project. It is easy to publish a chart. It is
harder to publish a chart that a skeptical reader can reproduce from scratch,
and harder still to keep publishing it every morning without a human involved.

## The one property everything else serves

**A reader must be able to check any number without trusting the author.**

Every significant design decision falls out of that:

| Decision | Why it follows |
| --- | --- |
| Raw data is committed to git, not a hidden database | You can clone the repo and recompute every figure |
| The transform layer is SQL in the repo, not a notebook | You can read exactly how a number was derived |
| Skills are matched by hand-written regex, not a model | Every skill count traces to a pattern you can read |
| Tests gate the deploy | A published number has passed a check, not just a build |
| The stats block is generated, never typed | The scale claims cannot drift from reality |
| Limits are stated on the dashboard itself | A measurement without its error bars is decoration |

## What it deliberately is not

**Not a job board.** It does not try to be a place you find a job. It links back
to the source posting and otherwise stays out of the way.

**Not a prediction.** It reports what employers advertised. Where a source
supplies a machine-*predicted* salary — Adzuna does this to fill gaps — that
figure is discarded at ingest rather than presented as employer-stated pay.

**Not complete.** Coverage is bounded by the company registry and by what Adzuna
surfaces. A company absent from both is invisible here, which is a limit of the
instrument and is stated as one.

## Why "quantyx"

A coined name with no meaning, chosen so it carries no claim. The dashboard's
own words do the work.

## What success looks like

Someone technical opens this repository, spends ninety seconds, and concludes
the person who built it can build production data systems — not because the
README says so, but because the commit history shows a machine that has been
running unattended and the dashboard shows what it caught.

---

Next: [02 — Choosing the sources](02-choosing-the-sources.md), which starts with
the plan that had to be thrown away.
