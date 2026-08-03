{{ config(materialized='table') }}

-- One row per posting, with lifespan. The grain the rest of the marts join to.
-- The full description is deliberately dropped here: it has already been
-- consumed by int_posting_skills, and carrying it makes the table (and every
-- dashboard query against it) needlessly heavy.

select
    posting_key,
    source,
    posting_id,
    title,
    company,
    url,
    location,
    is_remote,
    is_india,
    seniority,

    comp_min,
    comp_max,
    comp_currency,
    comp_period,
    (comp_min is not null or comp_max is not null) as has_compensation,

    posted_date,
    first_seen_date,
    last_seen_date,
    days_open,
    days_observed,
    is_active,

    description is not null as has_description

from {{ ref('int_postings_lifespan') }}
