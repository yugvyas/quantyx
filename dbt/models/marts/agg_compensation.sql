{{ config(materialized='table') }}

-- Compensation grouped by (currency, period) and never across them.
--
-- An INR/month intern stipend and a USD/year salary are not comparable, and
-- dividing an annual figure by 12 to "normalize" them produces a number that
-- is confidently wrong. Each currency+period combination is reported as its
-- own distribution; the dashboard renders them as separate charts.

with priced as (

    select
        source,
        company,
        title,
        seniority,
        is_india,
        is_remote,
        comp_currency,
        comp_period,
        -- Use the midpoint when a range is given, else whichever end exists.
        coalesce((comp_min + comp_max) / 2.0, comp_min, comp_max) as comp_point,
        comp_min,
        comp_max
    from {{ ref('fct_postings') }}
    where has_compensation
      and comp_currency is not null
      and comp_period is not null

)

select
    comp_currency,
    comp_period,
    seniority,

    count(*)                                              as posting_count,
    count(*) filter (where is_india)                      as india_posting_count,

    round(min(comp_point))                                as comp_min,
    round(percentile_cont(0.25) within group (order by comp_point)) as comp_p25,
    round(percentile_cont(0.50) within group (order by comp_point)) as comp_median,
    round(percentile_cont(0.75) within group (order by comp_point)) as comp_p75,
    round(max(comp_point))                                as comp_max,
    round(avg(comp_point))                                as comp_mean

from priced
group by 1, 2, 3
order by posting_count desc
