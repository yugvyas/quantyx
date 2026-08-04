# 03 — The pipeline

Everything in `pipeline/`. One command runs it:

```bash
python -m pipeline.run
```

## The shape

```
   Adzuna    Greenhouse    Lever    Ashby
      │           │          │        │
      └───────────┴────┬─────┴────────┘
                       │   four response shapes
                       ▼
                  Posting            ← the shared contract
                       │
                       ▼
              filter to data/AI roles
                       │
                       ▼
            dedupe against known IDs
                       │
                       ▼
     data/postings/<date>/<source>.jsonl.gz   (first sighting only)
     data/observations/<date>.jsonl.gz        (still-open log)
```

## The contract: `pipeline/schema.py`

One pydantic model, `Posting`, is the only thing the rest of the system sees.
Source adapters differ wildly; nothing downstream knows that.

```python
source        posting_id   title      company    url
location      is_remote    comp_min   comp_max
comp_currency comp_period  posted_date
description   seniority    is_india   fetched_at
```

Two details that are load-bearing:

**Blank identity fields are rejected at parse time.** A posting with no ID cannot
be deduped, so it would inflate counts on every single run. Better to drop it
loudly than to corrupt the lifespan model silently.

**`comp_period` is an enum, never normalised away.** An INR/month stipend and a
USD/year salary are not the same kind of number. The currency and period travel
with the amount all the way to the dashboard, which reports them as separate
distributions and never blends them.

### `key`

```python
@property
def key(self) -> str:
    return f"{self.source.value}:{self.posting_id}"
```

`source:posting_id` is the stable identity across runs. Dedupe and the entire
lifespan model rest on it.

## Source adapters: `pipeline/sources/`

Each implements `SourceAdapter.fetch()` and returns a `FetchResult` carrying
postings *and* errors. Errors are collected, never raised — a single dead company
slug, or one entirely dead source, must not take down the daily run.

Each adapter is split into a **pure `parse_job()` function** and a fetch loop.
That split is what makes the test suite possible: `parse_job` is tested against
real saved API responses with no network at all.

### Worth calling out

**Adzuna discards predicted salaries.** Adzuna fills missing salaries with an ML
prediction and flags it via `salary_is_predicted`. Those are model output, not
advertised pay. Including them would quietly poison every salary distribution on
the site, so they are dropped at ingest.

**Ashby's `employmentType` beats the text heuristic.** When Ashby says
`"Intern"`, that is authoritative and the title-based classifier does not
overwrite it.

**Hybrid is not remote.** `looks_remote()` explicitly excludes hybrid: it
requires presence, and conflating the two would overstate the remote share.

## Classification: `pipeline/classify.py`

This module decides what the dataset *is*, so every rule is a plain regex over
text — no model, no external API in the daily path.

**Matching runs on the title, by design.** Nearly every engineering job mentions
machine learning somewhere in its description. A role titled "Backend Engineer"
that name-drops ML is not a data role, and including it would inflate every count
on the site.

The rule is: title matches a data/AI term **and** does not match an adjacent-role
term. That second clause is why "AI Account Executive" and "Machine Learning
Recruiter" are correctly rejected.

### The regex bug that shaped this file

The first version built patterns like this:

```python
re.compile(rf"(?<![a-z0-9]){joined}(?![a-z0-9])", re.IGNORECASE)
```

`|` binds loosest in a regex. That compiles to:

```
((?<![a-z0-9])intern) | (internship) | ... | (summer analyst(?![a-z0-9]))
```

The lookbehind guards only the *first* alternative and the lookahead only the
*last*. Everything in between is unguarded — so **"Internal Audit Analyst" was
being classified as an internship.**

The fix is one non-capturing group:

```python
rf"(?<![a-z0-9])(?:{joined})(?![a-z0-9])"
```

It is covered by a named regression test now
(`test_short_tokens_do_not_match_inside_words`). See
[09 — Bugs worth reading](09-bugs-worth-reading.md).

## Storage: `pipeline/store.py`

Covered properly in [04 — The storage model](04-the-storage-model.md). Two
details belong here:

**Writes are atomic.** A run killed mid-write would otherwise leave a truncated
`.gz` that breaks every subsequent dbt build until someone deletes it by hand.

**gzip is written with `mtime=0`.** Identical content produces a byte-identical
file, so an unchanged partition creates no spurious git diff. On a repo whose
commit history is part of the argument, noise commits are a real cost.

## Re-runs are idempotent

`known_keys(exclude_date=run_date)` deliberately ignores the current day's
partition when computing what is already known.

Without it, a second run on the same day would find everything "already known",
write an empty partition, and silently destroy the first run's data. With it, a
re-run rebuilds that day from the full fetch.

Covered by `test_exclude_date_makes_reruns_idempotent`.

## The safety valve

```python
if not postings:
    log.error("no relevant postings fetched — refusing to write an empty day")
    return 1
```

If every source returns nothing, the run fails rather than committing a day of
zeroes. An empty day would look like a market that vanished.

---

Next: [04 — The storage model](04-the-storage-model.md).
