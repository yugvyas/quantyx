# quantyx

**A self-updating data pipeline for the India DS/AI job market.**

Every morning a scheduled job pulls data/AI job postings from four APIs,
commits the raw results to this repository, transforms them with dbt on
DuckDB, and republishes a dashboard — but only if the data passes its tests.

The repository is the dataset. There is no hidden database: every posting this
pipeline has ever seen is committed here as gzipped JSONL, so every number on
the dashboard can be recomputed by anyone who clones it.

<!-- STATS:START -->

**3,947** unique postings · **34,441** total observations · **34** days of history · **1,112** companies · **4** sources

| Metric | Value |
| --- | --- |
| Unique postings | 3,947 |
| Total observations | 34,441 |
| Days of history | 34 |
| Date range | 2026-08-03 → 2026-09-05 |
| Currently open | 1,052 |
| Companies tracked | 1,112 |
| Skill tags applied | 12,060 |
| Distinct skills seen | 109 |
| India-located postings | 3,166 |
| Remote postings | 389 |
| With advertised pay | 289 |
| Intern / new-grad / junior | 95 |

_Regenerated automatically on every pipeline run (last: 2026-09-05)._

<!-- STATS:END -->

---

## How it works

> **New here?** [`explainer/`](explainer/) is the long-form write-up: why each
> decision went the way it did, and the bugs that shaped it. Start with
> [what this is and why](explainer/01-what-and-why.md), or jump straight to
> [bugs worth reading](explainer/09-bugs-worth-reading.md).


```
                  ┌──────────┐  ┌────────────┐  ┌───────┐  ┌───────┐
   daily cron ──► │  Adzuna  │  │ Greenhouse │  │ Lever │  │ Ashby │
                  └────┬─────┘  └─────┬──────┘  └───┬───┘  └───┬───┘
                       └──────────────┴─────────────┴──────────┘
                                      │  four response shapes → one schema
                                      ▼
                         filter to data/AI roles, classify
                                      │
                                      ▼
                    data/postings/<date>/<source>.jsonl.gz   (first sighting)
                    data/observations/<date>.jsonl.gz        (still-open log)
                                      │  committed to git
                                      ▼
                        dbt + DuckDB: staging → marts
                                      │
                              ┌───────┴────────┐
                        tests pass?       tests fail?
                              │                │
                              ▼                ▼
                    publish dashboard    keep last good site
                                          + open an issue
```

### The storage model

A naive pipeline snapshots every open posting daily. That re-commits every job
description every day and pushes the repository past a gigabyte within a year.

Instead there are two datasets:

| Path | Written | Size |
| --- | --- | --- |
| `data/postings/<date>/<source>.jsonl.gz` | once, the day a posting is first seen | most of the bytes |
| `data/observations/<date>.jsonl.gz` | every run, `(source, posting_id)` only | a few KB/day |

From those two, dbt reconstructs `first_seen_date`, `last_seen_date`,
`days_open` and `is_active` — so the dataset supports **posting-lifespan
analysis** that a daily snapshot cannot, at a fraction of the storage.

### The deploy gate

`dbt build` runs 53 tests. Four are tripwires for the failure mode that
actually matters — a source breaking *quietly*:

| Test | Catches |
| --- | --- |
| `assert_volume_not_collapsed` | Today's volume far below its trailing average |
| `assert_no_source_disappeared` | A source that vanishes while others carry the total |
| `assert_required_fields_present` | A field that silently stops being populated (renamed upstream key) |
| `assert_compensation_is_coherent` | Pay figures that cannot be true |

If any fail, the workflow stops **before** the deploy step: the previous
dashboard stays live and an issue is opened. A pipeline that publishes a
market crash caused by its own bug is worse than one that stops.

`scripts/verify_drift_detection.sh` runs in CI and deliberately corrupts the
sample dataset to prove these tests actually fail — a test that has never been
seen failing is not evidence of anything.

## Sources

All four are official APIs used as intended. Nothing here scrapes a site whose
`robots.txt` disallows it.

| Source | Auth | Coverage |
| --- | --- | --- |
| [Adzuna](https://developer.adzuna.com) | free key | Broad Indian job market |
| [Greenhouse](https://developers.greenhouse.io/job-board.html) | none | Per-company boards |
| [Lever](https://api.lever.co) | none | Per-company boards |
| [Ashby](https://developers.ashbyhq.com/docs/public-job-posting-api) | none | Per-company boards, structured pay |

The three ATS sources are driven by `registry/companies.csv`, a curated list of
company job boards. Every entry in it has been verified to resolve;
`registry/candidates.csv` keeps the full discovery list including dead ones, so
the search can be re-run and widened.

## Quick start

```bash
python3.12 -m venv .venv && source .venv/bin/activate   # 3.10–3.13; dbt does not support 3.14
pip install -r requirements-dev.txt

cp .env.example .env            # optional: add Adzuna keys for India coverage

python -m pipeline.run --dry-run --limit 5   # smoke test, writes nothing
python -m pipeline.run                       # real run, writes partitions

cd dbt && dbt build --profiles-dir .         # transform + test
python -m pipeline.stats                     # refresh the README block above

cd dashboard && npm install
npm run sources && npm run dev               # dashboard at localhost:3000/quantyx
```

Two things that bite if skipped: `evidence build` does **not** materialize
sources, so `npm run sources` must run first on a clean checkout; and the dev
server lives under `/quantyx` because `deployment.basePath` is set for GitHub
Pages (plain `localhost:3000` redirects there).

### Useful commands

```bash
pytest tests/                                   # 126 tests, no network
ruff check pipeline tests scripts               # lint
scripts/verify_drift_detection.sh               # prove the deploy gate works
python -m pipeline.validate_registry            # find dead company boards
python scripts/make_sample_data.py              # regenerate CI fixtures

# Widen coverage: add rows to registry/candidates.csv, then
python -m pipeline.validate_registry --input registry/candidates.csv \
    --prune-to registry/companies.csv --min-jobs 1
```

## Deploying your own

1. Push to GitHub and enable **Settings → Pages → Source: GitHub Actions**.
2. Add repository secrets:
   - `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` — free from
     [developer.adzuna.com](https://developer.adzuna.com). **Without these the
     dataset skews heavily non-India**, because the three ATS sources are
     per-company boards dominated by US employers.
   - `PIPELINE_PAT` — a fine-grained PAT with `contents: write`. **Strongly
     recommended.** GitHub disables scheduled workflows on public repos after
     60 days with no *user* activity, and commits made with the default
     `GITHUB_TOKEN` do not reset that clock. Without a PAT the cron dies
     quietly after two months and the "always fresh" promise breaks silently.
3. Run the `Daily pipeline` workflow manually once to seed the data.

## What the numbers do not say

- **Seniority is inferred from job titles.** Most postings do not state a
  level, so a large share is `unknown`. That bucket is excluded from charts
  rather than folded into another level.
- **`days_open` is a lower bound** — it counts from the first day this pipeline
  saw a posting, not from when it was published.
- **Compensation is sparse and self-selected.** Employers who publish pay are
  not a random sample. Adzuna's machine-predicted salaries are discarded at
  ingest rather than presented as employer-stated pay.
- **Coverage is bounded by the registry.** Companies not listed, and not
  surfaced by Adzuna, are invisible here.
- **One row per requisition** — a role advertised in three cities appears three
  times, because each is a separate opening.

## Layout

```
pipeline/     fetch, normalize, classify, store        (Python)
registry/     which company job boards to track        (CSV)
data/         the dataset itself, append-only          (gzipped JSONL)
dbt/          staging → intermediate → marts + tests   (SQL)
dashboard/    Evidence.dev site                        (Markdown + SQL)
scripts/      sample-data generation, gate verification
tests/        126 tests + real API fixtures            (pytest)
```

## Licence

MIT for the code. Job posting data belongs to its respective sources and is
retained here only in the aggregate form the dashboard needs.
