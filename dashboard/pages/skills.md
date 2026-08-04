---
title: Skills in demand
description: Which tools and techniques Indian data and AI employers actually ask for.
---

```sql top_skills
select canonical_skill, category, posting_count, pct_of_all_postings
from quantyx.skill_frequency
order by posting_count desc, canonical_skill
limit 25
```

```sql by_category
select category, sum(posting_count) as mentions, count(*) as distinct_skills
from quantyx.skill_frequency
group by category
order by mentions desc, category
```

```sql early_career_skills
select canonical_skill, category, early_career_count
from quantyx.skill_frequency
where early_career_count > 0
order by early_career_count desc, canonical_skill
limit 20
```

```sql india_skills
select canonical_skill, india_posting_count
from quantyx.skill_frequency
where india_posting_count > 0
order by india_posting_count desc, canonical_skill
limit 20
```

```sql trend_top
select observed_date, canonical_skill, pct_of_open_postings
from quantyx.skill_trends
where canonical_skill in (
    select canonical_skill from quantyx.skill_frequency
    order by posting_count desc, canonical_skill limit 6
)
order by observed_date, canonical_skill
```

```sql all_skills
select canonical_skill, category, posting_count, active_posting_count,
       india_posting_count, early_career_count, pct_of_all_postings
from quantyx.skill_frequency
order by posting_count desc, canonical_skill
```

```sql counts
select count(*) as tracked, sum(posting_count) as mentions
from quantyx.skill_frequency
```

Every skill is detected by matching a hand-written regular expression against
the posting's title and description. Nothing is inferred by a model, so any
number on this page traces back to a pattern you can read in
[`dbt/seeds/skills_dictionary.csv`](https://github.com/yugvyas/quantyx/blob/main/dbt/seeds/skills_dictionary.csv).
The patterns are word-boundary anchored on purpose: unanchored, `SQL` matches
inside "MySQL" and "GraphQL" and the counts become fiction.

<Panel label="Most requested" annotation="Top 25 of {counts[0].tracked}">

{#if top_skills.length > 0}

<BarChart
    data={top_skills}
    x=canonical_skill
    y=posting_count
    swapXY=true
    yAxisTitle="Roles mentioning skill"
/>

{:else}

> No skills tagged yet — this fills in after the first pipeline run.

{/if}

</Panel>

<Panel
  label="By category"
  intro="Techniques dominate the raw count because a single posting names several of them; language and framework counts are closer to one-per-posting."
>

{#if by_category.length > 0}

<BarChart
    data={by_category}
    x=category
    y=mentions
    swapXY=true
    yAxisTitle="Total mentions"
/>

{/if}

</Panel>

<Panel
  label="India-located roles"
  intro="The same dictionary, restricted to postings whose location names an Indian city or state. The ordering differs from the global market."
>

{#if india_skills.length > 0}

<BarChart
    data={india_skills}
    x=canonical_skill
    y=india_posting_count
    swapXY=true
    yAxisTitle="India-located roles"
/>

{:else}

> No India-located postings tagged yet.

{/if}

</Panel>

<Panel
  label="Early career"
  intro="Intern, new-grad and junior postings only. This is a small slice of a market dominated by senior roles, so treat the ordering as indicative rather than settled."
>

{#if early_career_skills.length > 0}

<BarChart
    data={early_career_skills}
    x=canonical_skill
    y=early_career_count
    swapXY=true
    yAxisTitle="Early-career roles"
/>

{:else}

> No intern, new-grad or junior postings tagged yet. Early-career roles are a
> small slice of this market, so this section stays empty until enough of them
> accumulate.

{/if}

</Panel>

<Panel
  label="Share over time"
  intro="Measured as a share of the roles open on each day, not a raw count: as the company registry grows the absolute number rises for reasons that have nothing to do with the market."
>

{#if trend_top.length > 1}

<LineChart
    data={trend_top}
    x=observed_date
    y=pct_of_open_postings
    series=canonical_skill
    yAxisTitle="% of open roles"
    markers=true
/>

{:else}

> Two runs are needed before a share can move. Check back tomorrow.

{/if}

</Panel>

<Panel label="Full listing" annotation="{counts[0].tracked} skills">

<DataTable data={all_skills} search=true rows=20>
    <Column id=canonical_skill title="Skill"/>
    <Column id=category title="Category"/>
    <Column id=posting_count title="Roles"/>
    <Column id=active_posting_count title="Open now"/>
    <Column id=india_posting_count title="India"/>
    <Column id=early_career_count title="Early career"/>
    <Column id=pct_of_all_postings title="% of all" fmt='0.0"%"'/>
</DataTable>

</Panel>
