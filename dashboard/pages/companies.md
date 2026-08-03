---
title: Companies
description: Who is hiring, and how long their roles stay open.
---

```sql top_companies
select company, source, total_postings, active_postings, india_postings,
       early_career_postings
from quantyx.company_activity
order by total_postings desc
limit 25
```

```sql all_companies
select company, source, total_postings, active_postings, india_postings,
       remote_postings, early_career_postings, median_days_open_closed,
       first_seen_date, last_seen_date
from quantyx.company_activity
order by total_postings desc
```

```sql time_to_close
select company, median_days_open_closed, total_postings
from quantyx.company_activity
where median_days_open_closed is not null
order by median_days_open_closed desc
limit 20
```

## Most active employers

<BarChart
    data={top_companies}
    x=company
    y=total_postings
    swapXY=true
    yAxisTitle="Data/AI postings tracked"
/>

## How long roles stay open

Measured only over roles that have actually closed — including still-open
ones would drag every median toward "however long this pipeline has been
running", which says more about the pipeline than the market.

{#if time_to_close.length === 0}

> No postings have closed yet. This chart needs a few days of history before
> it can say anything.

{:else}

<BarChart
    data={time_to_close}
    x=company
    y=median_days_open_closed
    swapXY=true
    yAxisTitle="Median days open (closed roles)"
/>

{/if}

## All companies

<DataTable data={all_companies} search=true rows=20>
    <Column id=company title="Company"/>
    <Column id=source title="Source"/>
    <Column id=total_postings title="Total"/>
    <Column id=active_postings title="Open now"/>
    <Column id=india_postings title="India"/>
    <Column id=remote_postings title="Remote"/>
    <Column id=early_career_postings title="Early career"/>
    <Column id=median_days_open_closed title="Median days open"/>
</DataTable>
