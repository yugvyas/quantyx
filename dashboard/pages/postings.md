---
title: Postings
description: Every role the pipeline has tracked, searchable.
---

```sql postings
select
    title,
    company,
    location,
    seniority,
    source,
    case when is_india then 'India' else '—' end as india,
    case when is_remote then 'Remote' else 'On-site' end as arrangement,
    case when is_active then 'Open' else 'Closed' end as status,
    days_open,
    first_seen_date,
    comp_currency,
    comp_min,
    comp_max,
    comp_period
from quantyx.postings
order by first_seen_date desc, company
```

```sql counts
select
    count(*) as total,
    count(*) filter (where is_active) as open_now,
    count(*) filter (where is_india) as india,
    count(*) filter (where has_compensation) as with_pay
from quantyx.postings
```

<div class="tallies">
  <Readout label="Tracked to date" value={counts[0].total} lead={true}/>
  <Readout label="Open now" value={counts[0].open_now}/>
  <Readout label="India-located" value={counts[0].india}/>
  <Readout label="Advertising pay" value={counts[0].with_pay}/>
</div>

Search by role, company or location. Two things worth knowing before you read
the columns: `days_open` counts from the first day this pipeline saw the
posting, not from when it was published, so it is a lower bound for anything
already live before tracking began — and a role advertised in three cities
appears three times, because each is a separate requisition.

<Panel label="All roles" annotation="{counts[0].total} rows">

<DataTable data={postings} search=true rows=25>
    <Column id=title title="Role"/>
    <Column id=company title="Company"/>
    <Column id=location title="Location"/>
    <Column id=seniority title="Level"/>
    <Column id=arrangement title="Arrangement"/>
    <Column id=status title="Status"/>
    <Column id=days_open title="Days open"/>
    <Column id=first_seen_date title="First seen"/>
    <Column id=source title="Channel"/>
</DataTable>

</Panel>

<style>
  .tallies {
    display: grid;
    grid-template-columns: 1.3fr repeat(3, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-radius: 2px;
    margin-bottom: 1.75rem;
  }

  .tallies :global(.readout-well) {
    border: 0;
    border-radius: 0;
    box-shadow: none;
  }

  @media (max-width: 860px) {
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
