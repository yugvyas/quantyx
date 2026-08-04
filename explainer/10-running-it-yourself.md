# 10 — Running it yourself

Everything here is runnable. If a claim in this folder is wrong, these commands
are how you find out.

## Setup

```bash
git clone https://github.com/yugvyas/quantyx
cd quantyx

# Python 3.10–3.13. NOT 3.14 — dbt does not support it yet.
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

Adzuna keys are optional but matter a lot — without them the dataset skews
heavily non-India, because the three ATS sources are per-company boards dominated
by US employers:

```bash
cp .env.example .env    # then add ADZUNA_APP_ID and ADZUNA_APP_KEY
```

Free at [developer.adzuna.com](https://developer.adzuna.com).

## The daily cycle

```bash
python -m pipeline.run --dry-run --limit 5   # fetch, write nothing
python -m pipeline.run                       # real run, writes partitions

cd dbt && dbt build --profiles-dir .         # transform + 53 tests
cd .. && python -m pipeline.stats            # regenerate the README block

cd dashboard && npm install
npm run sources && npm run dev               # localhost:3000/quantyx
```

**Order matters.** `pipeline.run` writes raw JSONL; `dbt build` turns it into
what the dashboard reads. Fetching alone changes nothing visible.

## Verifying the claims

| Claim | Command |
| --- | --- |
| 126 tests pass, no network | `pytest tests/` |
| The deploy gate actually fires | `scripts/verify_drift_detection.sh` |
| Every published number is reproducible | `cd dbt && dbt build --profiles-dir .` |
| The registry is not stale | `python -m pipeline.validate_registry` |
| The pipeline commits its own data | `git log --author=quantyx-bot --oneline` |
| Chart colours are colourblind-safe | Palette + validator command in [`DESIGN.md`](../DESIGN.md) |

The drift-detection script is the interesting one — it deliberately corrupts data
and asserts the tests fail:

```
  simulated collapse: 92 -> 3 observations
  ok  assert_volume_not_collapsed correctly failed
  simulated dead source: dropped 'lever' (2 rows)
  ok  assert_no_source_disappeared correctly failed
  ok  both tests pass on healthy data
```

## Gotchas that will bite you

**Use `.venv`, not system Python.** `python3` on macOS is likely 3.14, which
dbt-duckdb does not support.

**Run bare `pytest`, not `python -m pytest`.** The latter puts the working
directory on `sys.path` and hides import errors that CI will catch. (`pythonpath`
is set in `pyproject.toml` now, but the habit still matters for reproducing CI.)

**`evidence build` does not run `evidence sources`.** It consumes parquet from a
previous run. On a clean checkout you must run `npm run sources` first — and to
genuinely reproduce CI you must delete `.evidence/` entirely, not just
`.evidence/meta`.

**The dev server lives at `/quantyx`**, because `deployment.basePath` is set for
GitHub Pages. Plain `localhost:3000` redirects there.

**Don't build sample data on the default target.** Use `--target ci`, or you will
overwrite the real database and the dashboard will show 124 fixture postings:

```bash
cd dbt && dbt build --profiles-dir . --target ci \
    --vars '{data_dir: ../tests/sample_data}'
```

## Deploying your own

1. Push to GitHub, enable **Settings → Pages → Source: GitHub Actions**.
2. Add repository secrets:
   - `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` — for India coverage.
   - `PIPELINE_PAT` — a fine-grained PAT with `contents: write`. **Strongly
     recommended.** GitHub disables scheduled workflows on public repos after 60
     days with no *user* activity, and `GITHUB_TOKEN` commits do not reset that
     clock. Without it the cron dies silently after two months. See
     [07 — Automation](07-automation.md).
3. Set `deployment.basePath` in `dashboard/evidence.config.yaml` to `/<your-repo>`.
4. Run the `Daily pipeline` workflow once by hand to seed the data.

## Extending it

**More companies** — add rows to `registry/candidates.csv`, then:

```bash
python -m pipeline.validate_registry --input registry/candidates.csv \
    --prune-to registry/companies.csv --min-jobs 1
```

Try each company against **all three** ATS vendors. A single-vendor miss proves
nothing — CRED, Zomato and Paytm were all written off before that was discovered.

**More skills** — add a row to `dbt/seeds/skills_dictionary.csv`. Anchor the
pattern with `\b` and remember DuckDB uses RE2, so **no lookahead**.

**Broader India coverage** — widen `DEFAULT_QUERIES` in
`pipeline/sources/adzuna.py`. There is budget spare: 24 calls/day used against
roughly 33 allowed.

**Design changes** — read [`DESIGN.md`](../DESIGN.md) first. Several rules there
look like taste and are not; the colour slot order in particular is a
colourblindness-safety mechanism.

---

Back to the [index](README.md).
