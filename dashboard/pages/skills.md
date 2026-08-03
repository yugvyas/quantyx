---
title: Skills in demand
description: Which tools and techniques employers actually ask for.
---

```sql top_skills
select canonical_skill, category, posting_count, pct_of_all_postings
from quantyx.skill_frequency
order by posting_count desc
limit 25
```

```sql by_category
select category, sum(posting_count) as mentions, count(*) as distinct_skills
from quantyx.skill_frequency
group by category
order by mentions desc
```

```sql early_career_skills
select canonical_skill, category, early_career_count
from quantyx.skill_frequency
where early_career_count > 0
order by early_career_count desc
limit 20
```

```sql trend_top
select observed_date, canonical_skill, pct_of_open_postings
from quantyx.skill_trends
where canonical_skill in (
    select canonical_skill from quantyx.skill_frequency
    order by posting_count desc limit 6
)
order by observed_date, canonical_skill
```

```sql all_skills
select canonical_skill, category, posting_count, active_posting_count,
       india_posting_count, early_career_count, pct_of_all_postings
from quantyx.skill_frequency
order by posting_count desc
```

Skills are detected by matching a curated dictionary of ~110 regular
expressions against each posting's title and description. Every number here
traces back to a pattern you can read in
[`dbt/seeds/skills_dictionary.csv`](https://github.com/yugvyas/quantyx/blob/main/dbt/seeds/skills_dictionary.csv)
— there is no model guessing in the loop.

## Most requested skills

{#if top_skills.length > 0}

<BarChart
    data={top_skills}
    x=canonical_skill
    y=posting_count
    swapXY=true
    yAxisTitle="Postings mentioning skill"
/>

{:else}

> No skills tagged yet — this fills in after the first pipeline run.

{/if}

## Demand by category

{#if by_category.length > 0}

<BarChart
    data={by_category}
    x=category
    y=mentions
    swapXY=true
    yAxisTitle="Total mentions"
/>

{/if}

## What early-career roles ask for

Filtered to intern, new-grad and junior postings — the mix differs from the
overall market, which is dominated by senior roles.

{#if early_career_skills.length > 0}

<BarChart
    data={early_career_skills}
    x=canonical_skill
    y=early_career_count
    swapXY=true
    yAxisTitle="Early-career postings"
/>

{:else}

> No intern, new-grad or junior postings tagged yet. Early-career roles are a
> small slice of this market, so this section stays empty until enough of them
> accumulate.

{/if}

## Share of open postings over time

Measured as a *share* of postings open that day, not a raw count: as the
company registry grows the absolute number rises for reasons that have nothing
to do with the market.

{#if trend_top.length > 0}

<LineChart
    data={trend_top}
    x=observed_date
    y=pct_of_open_postings
    series=canonical_skill
    yAxisTitle="% of open postings"
    markers=true
/>

{:else}

> Needs at least one completed run before there is a trend to plot.

{/if}

## All skills

<DataTable data={all_skills} search=true rows=20>
    <Column id=canonical_skill title="Skill"/>
    <Column id=category title="Category"/>
    <Column id=posting_count title="Postings" contentType=colorscale/>
    <Column id=active_posting_count title="Open now"/>
    <Column id=india_posting_count title="India"/>
    <Column id=early_career_count title="Early career"/>
    <Column id=pct_of_all_postings title="% of all" fmt='0.0"%"'/>
</DataTable>
