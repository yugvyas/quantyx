---
title: Companies
description: Who is hiring for data and AI roles, and how long their listings stay open.
---

```sql top_companies
select company, source, total_postings, active_postings, india_postings,
       early_career_postings
from quantyx.company_activity
order by total_postings desc, company
limit 25
```

```sql india_companies
select company, india_postings
from quantyx.company_activity
where india_postings > 0
order by india_postings desc, company
limit 20
```

```sql all_companies
select company, source, total_postings, active_postings, india_postings,
       remote_postings, early_career_postings, median_days_open_closed,
       first_seen_date, last_seen_date
from quantyx.company_activity
order by total_postings desc, company
```

```sql time_to_close
select company, median_days_open_closed, total_postings
from quantyx.company_activity
where median_days_open_closed is not null
order by median_days_open_closed desc, company
limit 20
```

```sql counts
select count(distinct company) as companies, count(*) as rows_
from quantyx.company_activity
```

Coverage is set by the company registry — 90 verified job boards across
Greenhouse, Lever and Ashby — plus whatever Adzuna surfaces across the broader
Indian market. A company absent from both is invisible here, which is a limit
of the instrument, not a statement about their hiring.

<Panel label="Most active" annotation="Top 25 of {counts[0].companies}">

{#if top_companies.length > 0}

<BarChart
    data={top_companies}
    x=company
    y=total_postings
    swapXY=true
    yAxisTitle="Data/AI roles tracked"
/>

{/if}

</Panel>

<Panel
  label="Hiring in India"
  intro="Restricted to postings whose location names an Indian city or state. Several of these are US-headquartered companies staffing engineering centres in Bengaluru, Hyderabad and Pune."
>

{#if india_companies.length > 0}

<BarChart
    data={india_companies}
    x=company
    y=india_postings
    swapXY=true
    yAxisTitle="India-located roles"
/>

{:else}

> No India-located roles recorded yet.

{/if}

</Panel>

<Panel
  label="Time to close"
  intro="Measured only over roles that have actually disappeared. Including still-open ones would drag every median toward however long this pipeline has been running, which says more about the instrument than the market."
>

{#if time_to_close.length === 0}

> No postings have closed yet. This needs a few more days of history before it
> can say anything — and until it can, it says nothing rather than guessing.

{:else}

<BarChart
    data={time_to_close}
    x=company
    y=median_days_open_closed
    swapXY=true
    yAxisTitle="Median days open (closed roles)"
/>

{/if}

</Panel>

<Panel label="Full listing" annotation="{counts[0].companies} companies">

<DataTable data={all_companies} search=true rows=20>
    <Column id=company title="Company"/>
    <Column id=source title="Channel"/>
    <Column id=total_postings title="Total"/>
    <Column id=active_postings title="Open now"/>
    <Column id=india_postings title="India"/>
    <Column id=remote_postings title="Remote"/>
    <Column id=early_career_postings title="Early career"/>
    <Column id=median_days_open_closed title="Median days open"/>
</DataTable>

</Panel>
