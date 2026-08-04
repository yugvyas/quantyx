---
title: quantyx
description: A self-updating measurement of the Indian data and AI job market.
---

```sql stats
select * from quantyx.pipeline_stats
```

```sql by_source
select source, count(*) as postings, count(distinct company) as companies
from quantyx.postings
group by source
```

```sql daily
select * from quantyx.market_daily order by observed_date
```

```sql workplace_mix
select observed_date, 'Remote' as arrangement, postings_remote as postings
from quantyx.market_daily
union all
select observed_date, 'On-site' as arrangement, postings_onsite as postings
from quantyx.market_daily
order by observed_date
```

```sql top_skills
select canonical_skill, posting_count
from quantyx.skill_frequency
order by posting_count desc, canonical_skill
limit 12
```

<div class="board power-on">

<div class="board-head">
  <div class="board-title">
    <!-- U+2011 non-breaking hyphen: CSS breaks lines at an ordinary hyphen,
         which stranded "re-" at the end of a line on desktop. -->
    <h1>The Indian data &amp; AI job market, re&#8209;derived every morning.</h1>
    <p>
      Four job APIs in, raw data committed to git, dbt on DuckDB out — republished
      only when it passes its own tests. Nobody touches it.
    </p>
  </div>

  <div class="board-state">
    <div class="well state-well">
      <span class="placard">Last run</span>
      <span class="readout stamp"><Value data={stats} column=last_run_date/></span>
      <StatusLamp state="nominal" label="Nominal"/>
    </div>
    <a class="action" href="https://github.com/yugvyas/quantyx" rel="noopener">
      Read the source
      <span aria-hidden="true">→</span>
    </a>
  </div>
</div>

<div class="board-module">
  <div class="module-label">
    <span class="placard">Ingest channels</span>
    <span class="module-note">Official APIs, used as their operators intend</span>
  </div>
  <ChannelStrip data={by_source}/>
</div>

<div class="board-module">
  <div class="module-label">
    <span class="placard">The gate</span>
    <span class="module-note">Why a quiet upstream failure cannot reach this page</span>
  </div>
  <TheGate lastRun={stats[0].last_run_date} daysOfHistory={stats[0].days_of_history}/>
</div>

</div>

<div class="tallies">
  <Readout label="Roles open now" value={stats[0].active_postings} note="Currently listed across every channel"/>
  <Readout label="Tracked to date" value={stats[0].unique_postings} unit="roles"/>
  <Readout label="India-located" value={stats[0].india_postings} unit="roles"/>
  <Readout label="Companies" value={stats[0].companies_tracked}/>
  <Readout label="Days of history" value={stats[0].days_of_history} note="Grows by one every morning"/>
</div>

<Panel
  label="Market activity"
  intro="Roles open on each day the pipeline has run, and the roles it had never seen before. New listings are the cleaner signal: the open total moves slowly, discoveries spike."
  annotation="{stats[0].days_of_history} day(s) recorded"
>

{#if daily.length < 2}

> Two runs are needed before a trend exists. The pipeline has recorded
> <Value data={stats} column=days_of_history/> so far — a single point plotted on a date axis
> renders a two-year span with one dot on it, which looks like data but says nothing.

{:else}

<LineChart
    data={daily}
    x=observed_date
    y=postings_open
    yAxisTitle="Roles open"
    markers=true
/>

<BarChart
    data={daily}
    x=observed_date
    y=postings_new
    yAxisTitle="Newly discovered"
/>

### Remote against on-site

<LineChart
    data={workplace_mix}
    x=observed_date
    y=postings
    series=arrangement
    yAxisTitle="Roles"
    markers=true
/>

{/if}

</Panel>

<Panel
  label="What employers ask for"
  intro="Every skill is matched by a hand-written regular expression against the posting's title and description, so any number here traces back to a pattern you can read. There is no model guessing in the loop."
  annotation="Top 12 of {stats[0].distinct_skills_seen}"
>

{#if top_skills.length > 0}

<BarChart
    data={top_skills}
    x=canonical_skill
    y=posting_count
    swapXY=true
    yAxisTitle="Roles mentioning skill"
/>

{/if}

<p class="deeper">
  <a href="/skills">All {stats[0].distinct_skills_seen} skills, by category and career stage →</a>
</p>

</Panel>

<Panel
  label="How to check this"
  intro="The repository is the dataset. Every posting the pipeline has ever seen is committed as gzipped JSONL, so every number above can be recomputed from scratch by anyone who clones it. Nothing here is scraped from a site whose robots.txt disallows it — an earlier plan to scrape Internshala was abandoned when its robots.txt turned out to forbid exactly the pages it needed."
>

<div class="verify">
  <div class="verify-item">
    <span class="placard">Reproduce</span>
    <code>dbt build</code>
    <p>Rebuilds every figure on this site from the committed raw data.</p>
  </div>
  <div class="verify-item">
    <span class="placard">Prove the gate</span>
    <code>scripts/verify_drift_detection.sh</code>
    <p>Corrupts the sample dataset on purpose and asserts the drift tests fail.</p>
  </div>
  <div class="verify-item">
    <span class="placard">Read the history</span>
    <code>git log</code>
    <p>The daily commits are the pipeline's own. It writes its data and its statistics without a human.</p>
  </div>
</div>

<a class="action action-wide" href="https://github.com/yugvyas/quantyx" rel="noopener">
  github.com/yugvyas/quantyx
  <span aria-hidden="true">→</span>
</a>

</Panel>

<style>
  /* Evidence auto-renders the frontmatter title as h1.title. The status board
     carries its own headline, so on this page alone that heading is redundant.
     SvelteKit only loads a route's CSS for that route, so this stays off the
     deep pages, where h1.title is the real station designation. */
  :global(h1.title) {
    display: none;
  }

  .board {
    border: 1px solid var(--rule-strong);
    border-radius: 2px;
    background: var(--panel-raised);
  }

  .board-head {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 17rem;
    gap: 2.5rem;
    padding: 1.75rem 1.5rem 1.5rem;
  }

  .board-title h1 {
    margin: 0 0 0.875rem;
    font-family: var(--font-placard);
    font-size: clamp(1.6rem, 3vw, 2.5rem);
    line-height: 1.08;
    letter-spacing: -0.035em;
    font-weight: 700;
    color: var(--ink);
    text-wrap: balance;
    max-width: 22ch;
  }

  .board-title p {
    margin: 0;
    max-width: 54ch;
    font-size: 0.9375rem;
    line-height: 1.65;
    color: var(--ink-dim);
  }

  .board-state {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .state-well {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    padding: 0.875rem 1rem;
  }

  .stamp {
    font-size: 1.125rem;
    font-weight: 500;
  }

  /* Modules bolted into the board face, each behind its own engraved label. */
  .board-module {
    padding: 0 1.5rem 1.5rem;
  }

  .module-label {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    margin-bottom: 0.625rem;
    flex-wrap: wrap;
  }

  .module-note {
    font-family: var(--font-placard);
    font-size: 0.75rem;
    color: var(--ink-faint);
  }

  .action {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.75rem 1rem;
    border: 1px solid var(--lamp-caution);
    border-radius: 2px;
    background: transparent;
    color: var(--ink);
    font-family: var(--font-placard);
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    text-decoration: none;
    transition: background 140ms ease-out, color 140ms ease-out;
  }

  .action:hover {
    background: var(--lamp-caution);
    color: #0a0f11;
  }

  .action-wide {
    margin-top: 1.5rem;
    font-family: var(--font-readout);
    text-transform: none;
    letter-spacing: 0;
  }

  /* The generic counts sit below the board: they are context, not the proof. */
  .tallies {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-top: 0;
    border-radius: 0 0 2px 2px;
  }

  .tallies :global(.readout-well) {
    border: 0;
    border-radius: 0;
    box-shadow: none;
  }

  .verify {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-radius: 2px;
  }

  .verify-item {
    background: var(--panel-raised);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .verify-item code {
    font-family: var(--font-readout);
    font-size: 0.8125rem;
    color: var(--ink);
  }

  .verify-item p {
    margin: 0;
    font-size: 0.8125rem;
    line-height: 1.55;
    color: var(--ink-dim);
  }

  .deeper {
    margin-top: 1.25rem;
    font-size: 0.875rem;
  }

  @media (max-width: 1000px) {
    .tallies {
      grid-template-columns: repeat(3, 1fr);
    }
    .verify {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 780px) {
    .board-head {
      grid-template-columns: 1fr;
      gap: 1.25rem;
      padding: 1.5rem 1.25rem 1.25rem;
    }
    .board-module {
      padding: 0 1.25rem 1.25rem;
    }
    .tallies {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 420px) {
    .tallies {
      grid-template-columns: 1fr;
    }
  }
</style>
