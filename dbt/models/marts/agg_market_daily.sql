{{ config(materialized='table') }}

-- The daily pulse of the market: how many roles were open, how many were new,
-- and how the remote / India / seniority mix moved.

with daily as (

    select
        o.observed_date,
        p.posting_key,
        p.is_remote,
        p.is_india,
        p.seniority,
        p.has_compensation,
        p.first_seen_date
    from {{ ref('stg_observations') }} o
    inner join {{ ref('fct_postings') }} p using (posting_key)

)

select
    observed_date,

    count(distinct posting_key)                                   as postings_open,
    count(distinct posting_key) filter (where first_seen_date = observed_date)
                                                                  as postings_new,

    count(distinct posting_key) filter (where is_india)           as postings_india,
    count(distinct posting_key) filter (where is_remote)          as postings_remote,
    count(distinct posting_key) filter (where not is_remote)      as postings_onsite,
    count(distinct posting_key) filter (where has_compensation)   as postings_with_comp,

    count(distinct posting_key) filter (where seniority = 'intern')   as postings_intern,
    count(distinct posting_key) filter (where seniority = 'new_grad') as postings_new_grad,
    count(distinct posting_key) filter (where seniority = 'junior')   as postings_junior,
    count(distinct posting_key) filter (where seniority = 'mid_plus') as postings_mid_plus,

    round(100.0 * count(distinct posting_key) filter (where is_remote)
          / nullif(count(distinct posting_key), 0), 2)            as pct_remote,
    round(100.0 * count(distinct posting_key) filter (where is_india)
          / nullif(count(distinct posting_key), 0), 2)            as pct_india

from daily
group by 1
order by observed_date
