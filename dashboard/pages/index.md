---
title: India DS/AI Job Market
description: A self-updating view of data and AI hiring, rebuilt every day.
---

```sql stats
select * from quantyx.pipeline_stats
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

```sql seniority_mix
select
    'Intern'   as seniority, sum(postings_intern)   as postings from quantyx.market_daily
    where observed_date = (select max(observed_date) from quantyx.market_daily)
union all
select 'New grad', sum(postings_new_grad) from quantyx.market_daily
    where observed_date = (select max(observed_date) from quantyx.market_daily)
union all
select 'Junior', sum(postings_junior) from quantyx.market_daily
    where observed_date = (select max(observed_date) from quantyx.market_daily)
union all
select 'Mid+', sum(postings_mid_plus) from quantyx.market_daily
    where observed_date = (select max(observed_date) from quantyx.market_daily)
```

<BigValue data={stats} value=active_postings title="Open right now"/>
<BigValue data={stats} value=unique_postings title="Postings tracked"/>
<BigValue data={stats} value=companies_tracked title="Companies"/>
<BigValue data={stats} value=days_of_history title="Days of history"/>

Every number on this site is rebuilt from scratch each morning by a scheduled
job that pulls from four job APIs, stores the raw results in git, and
transforms them with dbt. Last run: **<Value data={stats} column=last_run_date/>**.

{#if daily.length < 2}

> **This dataset is still filling up.** It has
> <Value data={stats} column=days_of_history/> day of history so far.
> The time-series charts are hidden until there are at least two runs to
> compare — a single point plotted on a date axis renders a two-year span
> with one dot on it, which looks like data but says nothing.

{:else}

## Postings open over time

<LineChart
    data={daily}
    x=observed_date
    y=postings_open
    yAxisTitle="Postings open"
    markers=true
/>

## New postings discovered each day

Roles the pipeline had never seen before. This is the cleanest signal of
hiring activity — total open count moves slowly, but new listings spike.

<BarChart
    data={daily}
    x=observed_date
    y=postings_new
    yAxisTitle="New postings"
/>

## Remote vs on-site

<LineChart
    data={workplace_mix}
    x=observed_date
    y=postings
    series=arrangement
    yAxisTitle="Postings"
    markers=true
/>

{/if}

## Career stage

Most postings do not state a level in the title, so "Unknown" is excluded
rather than guessed at — see the [methodology](/methodology).

<BarChart
    data={seniority_mix}
    x=seniority
    y=postings
    swapXY=true
    yAxisTitle="Postings"
/>

<LastRefreshed prefix="Data last updated"/>
