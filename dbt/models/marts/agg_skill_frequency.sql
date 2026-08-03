{{ config(materialized='table') }}

-- How often each skill is asked for, overall and among the slices that matter
-- for someone job-hunting: India-located roles, and intern / early-career roles.

with tagged as (

    select
        s.canonical_skill,
        s.category,
        p.posting_key,
        p.is_india,
        p.is_active,
        p.seniority
    from {{ ref('int_posting_skills') }} s
    inner join {{ ref('fct_postings') }} p using (posting_key)

),

total as (
    select count(*) as total_postings from {{ ref('fct_postings') }}
)

select
    t.canonical_skill,
    t.category,

    count(*)                                                  as posting_count,
    count(*) filter (where t.is_active)                       as active_posting_count,
    count(*) filter (where t.is_india)                        as india_posting_count,
    count(*) filter (where t.seniority in ('intern', 'new_grad', 'junior'))
                                                              as early_career_count,

    round(100.0 * count(*) / nullif(max(total.total_postings), 0), 2)
                                                              as pct_of_all_postings

from tagged t
cross join total
group by 1, 2
order by posting_count desc
