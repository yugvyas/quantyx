---
title: Compensation
description: Advertised pay, grouped by currency and period — never blended.
---

```sql groups
select comp_currency, comp_period,
       sum(posting_count) as postings
from quantyx.compensation
group by 1, 2
order by postings desc
```

```sql by_group
select comp_currency, comp_period, seniority, posting_count,
       comp_p25, comp_median, comp_p75, comp_min, comp_max,
       comp_currency || ' / ' || comp_period as pay_basis
from quantyx.compensation
order by posting_count desc
```

```sql pay_bases
select distinct comp_currency || ' / ' || comp_period as pay_basis,
       comp_currency, comp_period
from quantyx.compensation
order by pay_basis
```

## Why there is no single salary chart

An intern stipend quoted in **INR per month** and a staff salary quoted in
**USD per year** are not the same kind of number. Dividing the annual figure
by twelve to force them onto one axis produces a chart that is confidently
wrong — it implies a comparison the underlying data does not support.

So each currency-and-period combination is reported as its own distribution.
Only postings with an **advertised** figure are included: Adzuna fills missing
salaries with a machine-learning *prediction*, and those are discarded at
ingest rather than presented as employer-stated pay.

## Pay bases present in the data

<DataTable data={groups}>
    <Column id=comp_currency title="Currency"/>
    <Column id=comp_period title="Period"/>
    <Column id=postings title="Postings"/>
</DataTable>

## Median advertised pay

One chart per pay basis, each on its own axis. Putting them on a shared axis
would be the same mistake as blending them: an INR/month figure and a USD/year
figure against one scale invites a comparison the data does not support.

{#if pay_bases.length === 0}

> No postings with advertised pay yet. Most employers do not publish a salary,
> and Adzuna's machine-predicted figures are discarded at ingest rather than
> shown as employer-stated pay.

{/if}

{#each pay_bases as basis}

### {basis.pay_basis}

<BarChart
    data={by_group.filter(d => d.pay_basis === basis.pay_basis)}
    x=seniority
    y=comp_median
    swapXY=true
    yAxisTitle={'Median ' + basis.pay_basis}
/>

{/each}

## Full distributions

<DataTable data={by_group} rows=20>
    <Column id=pay_basis title="Pay basis"/>
    <Column id=seniority title="Level"/>
    <Column id=posting_count title="Postings"/>
    <Column id=comp_p25 title="p25"/>
    <Column id=comp_median title="Median"/>
    <Column id=comp_p75 title="p75"/>
</DataTable>
