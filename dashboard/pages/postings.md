---
title: Postings
description: Every posting the pipeline has tracked, searchable.
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
    comp_period,
    url
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

<BigValue data={counts} value=total title="Total tracked"/>
<BigValue data={counts} value=open_now title="Open now"/>
<BigValue data={counts} value=india title="India-located"/>
<BigValue data={counts} value=with_pay title="With advertised pay"/>

Search by title, company or location. `days_open` counts from the first day
the pipeline saw the posting, so it is a lower bound for roles that were
already live before tracking began.

<DataTable data={postings} search=true rows=25>
    <Column id=title title="Role"/>
    <Column id=company title="Company"/>
    <Column id=location title="Location"/>
    <Column id=seniority title="Level"/>
    <Column id=arrangement title="Arrangement"/>
    <Column id=status title="Status"/>
    <Column id=days_open title="Days open"/>
    <Column id=first_seen_date title="First seen"/>
    <Column id=source title="Source"/>
</DataTable>
