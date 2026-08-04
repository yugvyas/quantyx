---
title: Method
description: Where the numbers come from, and what they do not say.
---

```sql stats
select * from quantyx.pipeline_stats
```

```sql sources
select source, count(*) as postings, count(distinct company) as companies
from quantyx.postings
group by source
order by postings desc, source
```

<Panel
  label="Where the data comes from"
  intro="Four job APIs, all used as their operators intend — official endpoints with published terms, not scraped pages. Nothing here comes from a site whose robots.txt disallows it."
>

| Channel | Access | Covers |
| --- | --- | --- |
| Adzuna (India) | Official API, free tier | The broad Indian job market |
| Greenhouse | Public job board API | Per-company boards |
| Lever | Public postings API | Per-company boards |
| Ashby | Public job board API | Per-company boards, structured pay |

<div class="subtable">
  <span class="placard">What each channel has actually contributed</span>
  <DataTable data={sources}>
      <Column id=source title="Channel"/>
      <Column id=postings title="Roles"/>
      <Column id=companies title="Companies"/>
  </DataTable>
</div>

The original plan for this project was to scrape Internshala. That was
abandoned after reading its `robots.txt`, which disallows
`/internship/search/`, `/internship/details/` and every query-string URL —
exactly the pages a scraper would need. Beyond the compliance problem, a
scraper fighting anti-bot defences stops working within weeks, which would
defeat the entire premise of a repository that stays current.

</Panel>

<Panel label="How a posting becomes a row">

<ol class="steps">
  <li><span class="placard">Fetch</span><p>Each channel is queried daily. A channel that fails is reported and skipped; it never takes the run down with it.</p></li>
  <li><span class="placard">Normalize</span><p>Four different response shapes collapse into one schema. Ashby nests compensation, Lever uses epoch milliseconds, Greenhouse needs a flag to return descriptions at all, Adzuna paginates.</p></li>
  <li><span class="placard">Filter</span><p>A posting is kept only if its <strong>title</strong> names a data or AI role. Descriptions are deliberately not used: nearly every engineering job mentions machine learning somewhere, and matching on that would inflate every count on this site.</p></li>
  <li><span class="placard">Store</span><p>Full records are written once, on the day a posting is first seen, plus a small daily log of which postings were still open. That is what makes <code>days_open</code> and <code>is_active</code> possible without re-committing every description every day.</p></li>
  <li><span class="placard">Transform</span><p>dbt builds staging → intermediate → marts on DuckDB.</p></li>
  <li><span class="placard">Gate</span><p>The build fails, and nothing is published, if a channel disappears, if volume collapses against its trailing average, if a required field stops being populated, or if a pay figure is incoherent.</p></li>
</ol>

</Panel>

<Panel
  label="What these numbers do not say"
  intro="These limits are the reason to trust the rest. They are stated here rather than buried because a measurement without its error bars is decoration."
>

<div class="limits">
  <div class="limit">
    <StatusLamp state="caution" label="Seniority"/>
    <p>Inferred from the job title. Most postings do not state a level, so a large share sits in <em>unknown</em> — and that bucket is excluded from charts rather than quietly folded into another level.</p>
  </div>
  <div class="limit">
    <StatusLamp state="caution" label="Days open"/>
    <p>A lower bound. It counts from the first day this pipeline saw a posting, not from when the employer published it.</p>
  </div>
  <div class="limit">
    <StatusLamp state="caution" label="Compensation"/>
    <p>Sparse and self-selected: only <Value data={stats} column=postings_with_comp/> of <Value data={stats} column=unique_postings/> roles advertise pay, and employers who publish a salary are not a random sample. Predicted salaries are discarded.</p>
  </div>
  <div class="limit">
    <StatusLamp state="caution" label="Coverage"/>
    <p>Bounded by the company registry. Roles at companies not in it, and not surfaced by Adzuna, are invisible here.</p>
  </div>
  <div class="limit">
    <StatusLamp state="caution" label="Duplicates"/>
    <p>One row per requisition. A role advertised in three cities appears three times, because each is a separate opening.</p>
  </div>
</div>

</Panel>

<Panel
  label="Verifiable scale"
  intro="Every figure below is derived from files committed to the repository. Clone it, run dbt build, and you will get these same numbers."
>

<div class="scale">
  <Readout label="Unique postings" value={stats[0].unique_postings}/>
  <Readout label="Observations" value={stats[0].total_observations}/>
  <Readout label="Days recorded" value={stats[0].days_of_history}/>
  <Readout label="Companies" value={stats[0].companies_tracked}/>
  <Readout label="Skill tags applied" value={stats[0].skill_tags_applied}/>
</div>

</Panel>

<style>
  /* The listing arrived unlabelled after a gap, reading as an orphaned
     fragment of the table above it. */
  .subtable {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-block: 1.75rem;
  }

  .steps {
    list-style: none;
    margin: 0;
    padding: 0;
    border: 1px solid var(--rule);
    border-radius: 2px;
  }

  .steps li {
    display: grid;
    grid-template-columns: 8rem 1fr;
    gap: 1.25rem;
    padding: 0.875rem 1.125rem;
    border-bottom: 1px solid var(--rule);
    background: var(--panel-raised);
  }

  .steps li:last-child {
    border-bottom: 0;
  }

  .steps p {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.65;
    color: var(--ink-dim);
  }

  .limits {
    display: grid;
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-radius: 2px;
  }

  .limit {
    background: var(--panel-raised);
    padding: 0.875rem 1.125rem;
    display: grid;
    grid-template-columns: 9rem 1fr;
    gap: 1.25rem;
    align-items: start;
  }

  .limit p {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.65;
    color: var(--ink-dim);
  }

  .scale {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-radius: 2px;
  }

  .scale :global(.readout-well) {
    border: 0;
    border-radius: 0;
    box-shadow: none;
  }

  @media (max-width: 900px) {
    .scale {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  @media (max-width: 640px) {
    .steps li,
    .limit {
      grid-template-columns: 1fr;
      gap: 0.5rem;
    }
    .scale {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
