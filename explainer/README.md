# Explainer

How this project was built, why each decision went the way it did, and what
broke along the way.

The top-level [`README.md`](../README.md) tells you what quantyx *is* and how to
run it. This folder is the long version: the reasoning, the dead ends, and the
bugs. It is written for someone who wants to judge the engineering rather than
use the dashboard.

## Read in order

| File | What it covers |
| --- | --- |
| [01 — What this is and why](01-what-and-why.md) | The problem, the goal, and the one property everything else serves |
| [02 — Choosing the sources](02-choosing-the-sources.md) | Why the original scraping plan was scrapped, and how the four APIs were picked |
| [03 — The pipeline](03-the-pipeline.md) | Fetch → normalize → classify → store, and the schema that holds it together |
| [04 — The storage model](04-the-storage-model.md) | Why full records are written once and a tiny log is written daily |
| [05 — The transform layer](05-the-transform-layer.md) | dbt on DuckDB: staging, intermediate, marts, and the skills dictionary |
| [06 — The deploy gate](06-the-deploy-gate.md) | Four drift tests, and the script that proves they actually fail |
| [07 — Automation](07-automation.md) | GitHub Actions, and the trap that kills most self-updating repos |
| [08 — The dashboard](08-the-dashboard.md) | Evidence, the console design system, and a colour palette that had to be computed |
| [09 — Bugs worth reading](09-bugs-worth-reading.md) | The real failures, what caused them, and what each one changed |
| [10 — Running it yourself](10-running-it-yourself.md) | Commands, gotchas, and how to verify every claim here |

## The short version

A scheduled job pulls data/AI job postings from four official APIs every
morning, commits the raw results to this repository, transforms them with dbt on
DuckDB, and republishes a dashboard — but only if the data passes its own tests.

Three properties are doing most of the work:

1. **The repository is the dataset.** Every posting ever seen is committed here
   as gzipped JSONL. Any published number can be recomputed by cloning and
   running `dbt build`.
2. **It refuses to publish when it is wrong.** Four tests gate the deploy. A
   failing run leaves the previous dashboard live rather than replacing it with
   a market collapse the pipeline invented.
3. **Nobody touches it.** The commits that add data are the pipeline's own.

## A note on the numbers

Every figure in this folder was true when written and is dated where it matters.
The live figures live in the top-level README's stats block, which is
regenerated from the built data on every run by
[`pipeline/stats.py`](../pipeline/stats.py). If a number here disagrees with
that block, the block is right and this folder is stale.

Nothing here is rounded up.
