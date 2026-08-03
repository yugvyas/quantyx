{{ config(materialized='table') }}

-- The numbers the README badge quotes.
--
-- Every figure here is derived from data actually on disk, so any claim made
-- about the size of this dataset can be verified by anyone who clones the
-- repo and runs `dbt build`. That is the whole point: cite these, not
-- aspirational round numbers.

with postings as (select * from {{ ref('fct_postings') }}),
     observations as (select * from {{ ref('stg_observations') }}),
     skills as (select * from {{ ref('int_posting_skills') }})

select
    (select count(*) from postings)                              as unique_postings,
    (select count(*) from observations)                          as total_observations,
    (select count(distinct observed_date) from observations)     as days_of_history,
    (select min(observed_date) from observations)                as first_run_date,
    (select max(observed_date) from observations)                as last_run_date,

    (select count(distinct company) from postings)               as companies_tracked,
    (select count(distinct source) from postings)                as sources_tracked,
    (select count(*) from skills)                                as skill_tags_applied,
    (select count(distinct canonical_skill) from skills)         as distinct_skills_seen,

    (select count(*) from postings where is_active)              as active_postings,
    (select count(*) from postings where is_india)               as india_postings,
    (select count(*) from postings where is_remote)              as remote_postings,
    (select count(*) from postings where has_compensation)       as postings_with_comp,
    (select count(*) from postings where seniority in ('intern', 'new_grad', 'junior'))
                                                                 as early_career_postings
