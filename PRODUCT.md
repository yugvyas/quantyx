# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: recruiters, hiring managers and engineering leads evaluating Yug Vyas
as a data-engineering candidate. They arrive from a resume link, mid-workday,
with many tabs open and roughly ninety seconds of attention, and they are
skeptical by default because most portfolio "data projects" are a static
notebook screenshot.

Secondary, and never at the primary's expense: people job-hunting for data/AI
roles in India, who can use the published figures to see which skills are
actually being asked for.

## Product Purpose

quantyx measures the Indian data/AI job market by re-deriving it from scratch
every morning, in public. A scheduled job pulls postings from four job APIs,
commits the raw results to its own git repository, transforms them with dbt on
DuckDB, and republishes a dashboard — but only if the data passes its own tests.

Success is a visitor concluding, quickly and correctly, that the person who
built this can build production data systems.

## Positioning

The repository is the dataset. There is no hidden database: every posting the
pipeline has ever seen is committed as gzipped JSONL, so every published number
can be recomputed by anyone who clones it. Two properties a neighbouring
"job board scraper" could not truthfully claim:

1. **It refuses to publish when it is wrong.** Four drift tests gate the deploy;
   if a source breaks quietly the run halts *before* publishing and the previous
   dashboard stays live. A script in CI deliberately corrupts the data to prove
   those tests actually fail.
2. **It knows how long a role stays open.** Full records are written once, on
   first sighting, plus a tiny daily sighting log — so the dataset supports
   posting-lifespan analysis that a daily snapshot cannot, at a fraction of the
   storage.

## Operating Context

Visitors are on desktop, in a browser, between other tasks. Many will click
through to GitHub to check whether the commit history is real. The site is
static, served from GitHub Pages, and queries parquet in the browser via DuckDB.

The pipeline itself runs unattended at 02:30 UTC (08:00 IST) daily.

## Capabilities and Constraints

- **Sources (all official APIs, used as intended):** Adzuna India (keyed),
  Greenhouse, Lever and Ashby public job-board APIs (no auth). Nothing is
  scraped from a site whose `robots.txt` disallows it — this was a deliberate
  reversal after Internshala's `robots.txt` was found to forbid the needed paths.
- **Coverage** is bounded by `registry/companies.csv` (90 verified company
  boards) plus Adzuna's breadth. Companies absent from both are invisible.
- **Seniority is inferred from job titles**, so a large share is `unknown`; that
  bucket is excluded from charts rather than folded into another level.
- **Compensation is sparse and self-selected**, and must never be blended across
  currency or period — an INR/month stipend and a USD/year salary are not
  comparable. Adzuna's machine-predicted salaries are discarded at ingest.
- **`days_open` is a lower bound**, counted from first sighting, not publication.
- **One row per requisition:** a role advertised in three cities appears
  three times.
- Built on Evidence.dev (SvelteKit + DuckDB-WASM); pages are Markdown with
  embedded SQL and components. Deployed to a GitHub Pages *project* path.

## Brand Commitments

- Name: **quantyx**.
- Byline: **Yug Vyas**, with a prominent link to
  `https://github.com/yugvyas/quantyx`. No email address or LinkedIn.
- Voice: plainly stated and unhyped. The project's credibility rests on
  admitting what the numbers do not say, so hedges and caveats are content, not
  clutter to be designed away.

## Evidence on Hand

All real, all reproducible, all live in the repository:

- ~950 unique postings, ~1,500 observations, 257 companies, 4 sources, growing
  daily. Exact current figures are generated into `README.md` by
  `pipeline/stats.py` from the built marts — never hand-written or rounded up.
- 406 India-located postings; 87 with advertised pay; ~101 distinct skills
  tagged via a hand-written regex dictionary of ~110 patterns.
- A real commit history in which the pipeline commits its own data daily.
- 126 passing tests, 53 dbt tests, and `scripts/verify_drift_detection.sh`,
  which corrupts the sample dataset in CI to prove the deploy gate fires.

There are no customers, no testimonials, no benchmarks and no pricing. None may
be invented.

## Product Principles

1. **Every published number must be reproducible from the repo.** Cite the
   generated figures; never a rounder, larger one.
2. **Refusing to publish is a feature.** The failure path is part of the story,
   not an embarrassment to hide.
3. **State the limits.** The caveats are what make the rest believable.
4. **Freshness is the proof.** A visitor should be able to tell, immediately,
   that this ran today and was not assembled by hand.
5. **The data serves the argument.** For the primary visitor the charts are
   evidence that the machine works, not the destination.

## Accessibility & Inclusion

No user-specific requirement was established. Default obligations apply:
keyboard operability, visible focus, sufficient contrast, and content that never
relies on colour alone to carry meaning.
