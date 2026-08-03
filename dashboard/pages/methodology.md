---
title: Methodology
description: Where the numbers come from, and what they do not say.
---

```sql stats
select * from quantyx.pipeline_stats
```

```sql sources
select source, count(*) as postings, count(distinct company) as companies
from quantyx.postings
group by source
order by postings desc
```

## Where the data comes from

Four job APIs, all used as their operators intend — official endpoints with
published terms, not scraped pages. Nothing here comes from a site whose
`robots.txt` disallows it.

| Source | Access | What it covers |
| --- | --- | --- |
| Adzuna (India) | Official API, free tier | Broad Indian job market |
| Greenhouse | Public job board API | Per-company boards |
| Lever | Public postings API | Per-company boards |
| Ashby | Public job board API | Per-company boards, structured pay |

<DataTable data={sources}>
    <Column id=source title="Source"/>
    <Column id=postings title="Postings"/>
    <Column id=companies title="Companies"/>
</DataTable>

## How a posting becomes a row

1. **Fetch.** Each source is queried daily. A source that fails is reported
   and skipped — it never takes the run down with it.
2. **Normalize.** Four different response shapes collapse into one schema.
3. **Filter.** A posting is kept only if its **title** names a data/AI role.
   Descriptions are not used for this: nearly every engineering job mentions
   machine learning somewhere, and matching on that would inflate every count.
4. **Store.** Full records are written once, on the day a posting is first
   seen. A tiny daily log records which postings were still open. That is what
   makes `days_open` and `is_active` possible without re-storing every
   description every day.
5. **Transform.** dbt builds staging → intermediate → marts on DuckDB.
6. **Test.** The build fails — and nothing is published — if a source
   disappears, if volume collapses against its trailing average, if a required
   field stops being populated, or if a pay figure is incoherent.

## What these numbers do not say

- **Seniority is inferred from the title.** Most postings do not state a
  level, so a large share sits in "Unknown". That bucket is excluded from
  charts rather than silently folded into another level.
- **`days_open` is a lower bound.** It counts from the first day this
  pipeline saw a posting, not from when it was actually published.
- **Compensation is sparse and self-selected.** Only
  <Value data={stats} column=postings_with_comp/> of
  <Value data={stats} column=unique_postings/> postings advertise pay, and
  employers who publish salary are not a random sample. Predicted salaries are
  discarded.
- **Coverage is set by the company registry.** Roles at companies not in the
  registry, and not surfaced by Adzuna, are invisible here.
- **One posting per requisition.** A role advertised in three cities appears
  three times, because each is a separate opening.

## Verifiable scale

<DataTable data={stats}>
    <Column id=unique_postings title="Unique postings"/>
    <Column id=total_observations title="Observations"/>
    <Column id=days_of_history title="Days"/>
    <Column id=companies_tracked title="Companies"/>
    <Column id=skill_tags_applied title="Skill tags"/>
</DataTable>

Every figure is derived from files committed to the repository. Clone it, run
`dbt build`, and you will get these same numbers.
