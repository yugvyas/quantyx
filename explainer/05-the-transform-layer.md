# 05 — The transform layer

dbt on DuckDB, in `dbt/`. **11 models, 53 tests**, all passing.

```bash
cd dbt && dbt build --profiles-dir .
```

## No load step

DuckDB reads the gzipped JSONL partitions directly:

```sql
from read_json_auto(
    '{{ var("data_dir") }}/postings/*/*.jsonl.gz',
    union_by_name = true,
    filename      = true
)
```

Two flags carry real weight.

**`union_by_name = true`** is what lets a new field appear in a later partition
without breaking the read of every older one. Columns absent from an older file
arrive as `NULL` instead of raising. Without it, the first schema change would
break every historical file at once.

**`filename = true`** exposes the source path, which is how `first_seen_date` is
derived:

```sql
try_cast(regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1) as date) as first_seen_date
```

The partition folder *is* the first-sighting date. Deriving it from the path
rather than from a field in the row means it cannot disagree with where the file
actually lives.

## The layers

```
staging/        stg_postings, stg_observations
                  ↓  typing, trimming, key construction
intermediate/   int_postings_lifespan   ← first/last seen, days_open, is_active
                int_posting_skills      ← long-format posting × skill
                  ↓
marts/          fct_postings            ← one row per posting, the grain
                agg_skill_frequency     agg_skill_trends
                agg_compensation        agg_market_daily
                agg_company_activity    agg_pipeline_stats
```

`fct_postings` deliberately drops the full description. It has already been
consumed by `int_posting_skills`, and carrying it makes the table — and every
dashboard query against it — needlessly heavy.

`agg_pipeline_stats` is the one the README's stats block reads. Every figure it
produces is derived from files on disk, which is what makes the scale claims
checkable.

## The skills dictionary

`dbt/seeds/skills_dictionary.csv` — **109 skills**, each a hand-written regex.

```csv
canonical_skill,category,pattern
Python,language,"\bpython\b"
SQL,language,"\bsql\b"
scikit-learn,ml_framework,"scikit[ -]?learn|\bsklearn\b"
C++,language,"c\+\+"
```

Matching is a cross join filtered by regex:

```sql
from postings p
cross join skills s
where regexp_matches(p.searchable_text, s.pattern)
```

### Why a dictionary and not a model

Every number on the Skills page traces back to a pattern you can read in one CSV.
There is no embedding, no NER, no API call in the daily path, and no version of
"the model decided". For a project whose entire argument is verifiability, that
trade is obviously right — and it also means the daily cron has no external
dependency that can rate-limit or go down.

### Two constraints that shaped the file

**DuckDB uses RE2, which has no lookahead.** The first draft used
`java(?!script)` to avoid matching JavaScript. RE2 rejects it outright. The fix
is `\bjava\b` — "javascript" has no word boundary after "java", so it does not
match.

**Word boundaries are not optional.** Unanchored, `sql` matches inside "MySQL",
"PostgreSQL" and "GraphQL", and the SQL count becomes fiction. Every pattern is
`\b`-anchored, and all 109 were verified to compile under RE2 and match correctly
before the models were written.

## The tests

53 total: dbt's generic tests (`unique`, `not_null`, `accepted_values`,
`relationships`) plus **4 singular tests** that are the actual deploy gate. Those
get their own file — [06 — The deploy gate](06-the-deploy-gate.md).

## Two targets, on purpose

`dbt/profiles.yml` defines `dev` and `ci`:

```yaml
dev:  path: "../quantyx.duckdb"      # what the dashboard reads
ci:   path: "../quantyx_ci.duckdb"   # sample and corrupted-data builds
```

Without this, running the CI build locally against `tests/sample_data` silently
overwrote the real database, and the dashboard started showing 124 fixture
postings. The scratch target exists specifically to make that impossible.

Note the exception: the **dashboard** CI job deliberately uses the default `dev`
target, because a fresh runner has no real database to protect and Evidence's
connection points at the `dev` file. That asymmetry is commented in `ci.yml`,
because it looks like an inconsistency and is not.

---

Next: [06 — The deploy gate](06-the-deploy-gate.md).
