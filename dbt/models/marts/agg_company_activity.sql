{{ config(materialized='table') }}

-- Who is actually hiring, and how fast their roles move.
--
-- median_days_open is only meaningful once a posting has closed, so it is
-- computed over closed roles only — including still-open ones would drag the
-- median toward "however long this pipeline has been running".

with closed as (

    select company, source, days_open
    from {{ ref('fct_postings') }}
    where not is_active

)

select
    p.company,
    p.source,

    count(*)                                          as total_postings,
    count(*) filter (where p.is_active)               as active_postings,
    count(*) filter (where p.is_india)                as india_postings,
    count(*) filter (where p.is_remote)               as remote_postings,
    count(*) filter (where p.seniority in ('intern', 'new_grad', 'junior'))
                                                      as early_career_postings,

    min(p.first_seen_date)                            as first_seen_date,
    max(p.last_seen_date)                             as last_seen_date,

    (select round(percentile_cont(0.5) within group (order by c.days_open))
     from closed c
     where c.company = p.company and c.source = p.source) as median_days_open_closed

from {{ ref('fct_postings') }} p
group by 1, 2
order by total_postings desc
