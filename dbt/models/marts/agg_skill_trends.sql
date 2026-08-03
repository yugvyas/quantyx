{{ config(materialized='table') }}

-- Skill demand over time, measured against the postings open on each day.
--
-- The share matters more than the raw count: as the registry grows the
-- absolute number of postings rises for reasons that have nothing to do with
-- the market, and a raw-count chart would read that as a demand spike.

with daily_open as (

    select
        o.observed_date,
        o.posting_key,
        p.is_india
    from {{ ref('stg_observations') }} o
    inner join {{ ref('fct_postings') }} p using (posting_key)

),

daily_totals as (

    select
        observed_date,
        count(distinct posting_key)                            as postings_open,
        count(distinct posting_key) filter (where is_india)     as india_postings_open
    from daily_open
    group by 1

),

daily_skills as (

    select
        d.observed_date,
        s.canonical_skill,
        s.category,
        count(distinct d.posting_key)                          as postings_with_skill,
        count(distinct d.posting_key) filter (where d.is_india) as india_postings_with_skill
    from daily_open d
    inner join {{ ref('int_posting_skills') }} s using (posting_key)
    group by 1, 2, 3

)

select
    s.observed_date,
    s.canonical_skill,
    s.category,
    s.postings_with_skill,
    s.india_postings_with_skill,
    t.postings_open,
    t.india_postings_open,
    round(100.0 * s.postings_with_skill / nullif(t.postings_open, 0), 2)
        as pct_of_open_postings
from daily_skills s
inner join daily_totals t using (observed_date)
order by s.observed_date, s.postings_with_skill desc
