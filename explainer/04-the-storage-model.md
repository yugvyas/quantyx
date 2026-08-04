# 04 — The storage model

This is the part of the project I would point at first.

## The obvious approach, and what it costs

The obvious way to track a job market daily is to snapshot every open posting
every day:

```
data/2026-08-04/postings.jsonl    ← all 950 postings, descriptions and all
data/2026-08-05/postings.jsonl    ← all 950 again, mostly identical
data/2026-08-06/postings.jsonl    ← all 950 again
```

It works, and it has two problems. It re-commits every job description every day,
so the repository grows by roughly the full dataset daily — on the order of half
a gigabyte a year. And because git stores each day as a new blob, the history
becomes mostly duplicate text.

## What this project does instead

Split the data by how often it actually changes.

| Path | Written | Contains | Size |
| --- | --- | --- | --- |
| `data/postings/<date>/<source>.jsonl.gz` | **once**, the day a posting is first seen | the full record, description included | most of the bytes |
| `data/observations/<date>.jsonl.gz` | **every run** | `(source, posting_id, observed_date)` only | a few KB/day |

A posting's description is immutable in practice, so it is stored once. What
changes daily is only *which* postings are still open — and that is three short
fields per posting.

## What you get back

From those two datasets, `int_postings_lifespan.sql` reconstructs something a
daily snapshot cannot cheaply give you:

```sql
min(observed_date)                        as first_seen_date
max(observed_date)                        as last_seen_date
date_diff('day', first_seen, last_seen)+1 as days_open
last_observed_date >= last_run_date       as is_active
```

That unlocks **posting-lifespan analysis**: how long roles stay open, which
companies fill fastest, which postings are still live right now. The Companies
page's "time to close" chart exists because of this model.

So the compact format is not only cheaper — it is strictly more capable than the
naive one.

## Two details that matter more than they look

### `is_active` compares against the last *run*, not today

```sql
coalesce(s.last_observed_date, p.first_seen_date) >= r.last_run_date as is_active
```

If it compared against the current date, then any day the cron failed to run
would mark every posting in the dataset as closed. Comparing against the most
recent run date means a missed day is simply a missed day.

### `days_open` is a lower bound, and says so

It counts from the first day *this pipeline* saw a posting, not from when the
employer published it. A role that was already live for a month before tracking
began shows as one day old on day one.

That is stated on the dashboard and on the Method page rather than quietly
smoothed over. The Companies page goes further: median days-open is computed
**only over roles that have actually closed**, because including still-open ones
would drag every median toward "however long this pipeline has been running" —
a number about the instrument, not the market.

## Growth in practice

Day one wrote 584 KB (550 postings with full descriptions). Every subsequent day
writes only newly-discovered postings plus an observation log measured in
kilobytes.

The growth curve is therefore driven by *new* postings, not total postings —
which is the right shape, because new postings are the thing genuinely being
discovered each day.

## Robustness

`known_keys()` reads every prior partition to build the set of already-seen
postings. Two deliberate properties:

- **A corrupt partition does not wedge the pipeline.** A truncated `.gz` is
  logged and skipped rather than raising, so one bad file cannot block every
  future run. Covered by `test_corrupt_partition_does_not_crash_known_keys`.
- **Writes are atomic** — temp file, then rename — so a crash mid-write cannot
  leave that truncated file in the first place.

---

Next: [05 — The transform layer](05-the-transform-layer.md).
