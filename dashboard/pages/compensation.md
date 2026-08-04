---
title: Compensation
description: Advertised pay, grouped by currency and period — never blended.
---

```sql groups
select comp_currency, comp_period, sum(posting_count) as postings
from quantyx.compensation
group by 1, 2
order by postings desc, comp_currency, comp_period
```

```sql pay_bases
select distinct comp_currency || ' / ' || comp_period as pay_basis,
       comp_currency, comp_period
from quantyx.compensation
order by pay_basis
```

```sql by_group
select comp_currency, comp_period, seniority, posting_count,
       comp_p25, comp_median, comp_p75, comp_min, comp_max,
       comp_currency || ' / ' || comp_period as pay_basis
from quantyx.compensation
order by posting_count desc, comp_currency, comp_period, seniority
```

```sql coverage
select
    count(*) as total,
    count(*) filter (where has_compensation) as with_pay
from quantyx.postings
```

<div class="caution-plate">
  <StatusLamp state="caution" label="Read this first"/>
  <p>
    An intern stipend quoted in <strong>INR per month</strong> and a staff salary quoted in
    <strong>USD per year</strong> are not the same kind of number. Dividing the annual figure by
    twelve to force them onto one axis produces a chart that is confidently wrong — it implies a
    comparison the underlying data does not support. So each currency-and-period combination is
    reported as its own distribution, on its own axis.
  </p>
</div>

<div class="coverage">
  <Readout label="Roles tracked" value={coverage[0].total}/>
  <Readout label="Advertising pay" value={coverage[0].with_pay} note="Employers who publish a figure are not a random sample"/>
  <p class="coverage-note">
    <span class="measure">
      Only postings with an <strong>advertised</strong> figure are counted. Adzuna fills missing
      salaries with a machine-learning <em>prediction</em>; those are discarded at ingest rather
      than presented as employer-stated pay, because a predicted salary plotted as a real one
      quietly poisons every distribution on this page.
    </span>
  </p>
</div>

<Panel label="Pay bases present">

<DataTable data={groups}>
    <Column id=comp_currency title="Currency"/>
    <Column id=comp_period title="Period"/>
    <Column id=postings title="Roles"/>
</DataTable>

</Panel>

<Panel
  label="Median advertised pay"
  intro="One chart per pay basis, each on its own axis. Bars are comparable only against others in the same chart."
>

{#if pay_bases.length === 0}

> No postings with advertised pay yet. Most employers do not publish a salary,
> and predicted figures are discarded at ingest.

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

</Panel>

<Panel
  label="Full distributions"
  intro="Quartiles rather than averages: a handful of very senior roles would drag a mean somewhere no actual posting sits."
>

<DataTable data={by_group} rows=20>
    <Column id=pay_basis title="Pay basis"/>
    <Column id=seniority title="Level"/>
    <Column id=posting_count title="Roles"/>
    <Column id=comp_p25 title="p25"/>
    <Column id=comp_median title="Median"/>
    <Column id=comp_p75 title="p75"/>
</DataTable>

</Panel>

<style>
  /* Lamp beside the text rather than above it, matching the limits plates on
     the Method page and using the full width instead of leaving it empty. */
  .caution-plate {
    display: grid;
    grid-template-columns: 11rem 1fr;
    gap: 1.25rem;
    align-items: start;
    border: 1px solid var(--rule);
    border-left: 1px solid var(--lamp-caution);
    background: var(--panel-inset);
    border-radius: 2px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.75rem;
  }

  @media (max-width: 640px) {
    .caution-plate {
      grid-template-columns: 1fr;
      gap: 0.625rem;
    }
  }

  .caution-plate p {
    margin: 0;
    font-size: 0.9375rem;
    line-height: 1.7;
    color: var(--ink-dim);
    max-width: 68ch;
  }

  /* A flush 1px-gap grid, matching every other module group on the site.
     The earlier version used a gapped three-column row with align-items:start,
     which left the two wells at different widths and heights — the only
     unaligned pair anywhere. Cells stretch, so their edges agree. */
  .coverage {
    display: grid;
    grid-template-columns: minmax(0, 13rem) minmax(0, 13rem) minmax(0, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-radius: 2px;
    margin-bottom: 1.75rem;
  }

  .coverage :global(.readout-well) {
    border: 0;
    border-radius: 0;
    box-shadow: none;
    height: 100%;
  }

  /* The cell's plate must span its column or the container's rule colour shows
     through as a phantom cell; the text inside keeps the site's measure, or
     uncapping it produces 100-character lines. Two different jobs. */
  .coverage-note .measure {
    display: inline-block;
    max-width: 68ch;
  }

  .coverage-note {
    max-width: none;
    margin: 0;
    padding: 0.875rem 1rem;
    background: var(--panel-raised);
    font-size: 0.8125rem;
    line-height: 1.6;
    color: var(--ink-dim);
  }

  @media (max-width: 860px) {
    .coverage {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .coverage-note {
      grid-column: 1 / -1;
    }
  }

  @media (max-width: 460px) {
    .coverage {
      grid-template-columns: 1fr;
    }
  }

</style>
