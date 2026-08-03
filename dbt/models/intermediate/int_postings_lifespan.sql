{{ config(materialized='view') }}

-- Turns "a full record on first sight + a daily sighting log" back into one
-- row per posting with a lifespan attached.
--
-- This is what a plain daily snapshot cannot give you: because we know the
-- first and last day a posting was observed, we can measure how long roles
-- stay open, and which are still live right now.

with postings as (

    select *
    from {{ ref('stg_postings') }}
    -- Defensive: a posting should be written exactly once, on the day it is
    -- first seen. If a re-run ever duplicated one, keep the earliest.
    qualify row_number() over (
        partition by posting_key
        order by first_seen_date asc, fetched_at asc
    ) = 1

),

sightings as (

    select
        posting_key,
        min(observed_date)          as first_observed_date,
        max(observed_date)          as last_observed_date,
        count(distinct observed_date) as days_observed
    from {{ ref('stg_observations') }}
    group by 1

),

-- The most recent day the pipeline ran at all. A posting is "active" if it
-- was still present on that day; comparing against today's date instead would
-- mark everything stale whenever the cron misses a run.
latest_run as (

    select max(observed_date) as last_run_date
    from {{ ref('stg_observations') }}

)

select
    p.posting_key,
    p.source,
    p.posting_id,
    p.title,
    p.company,
    p.url,
    p.location,
    p.is_remote,
    p.is_india,
    p.seniority,
    p.comp_min,
    p.comp_max,
    p.comp_currency,
    p.comp_period,
    p.posted_date,
    p.description,

    coalesce(s.first_observed_date, p.first_seen_date) as first_seen_date,
    coalesce(s.last_observed_date, p.first_seen_date)  as last_seen_date,
    coalesce(s.days_observed, 1)                       as days_observed,

    date_diff(
        'day',
        coalesce(s.first_observed_date, p.first_seen_date),
        coalesce(s.last_observed_date, p.first_seen_date)
    ) + 1 as days_open,

    coalesce(s.last_observed_date, p.first_seen_date) >= r.last_run_date
        as is_active,

    r.last_run_date

from postings p
left join sightings s on s.posting_key = p.posting_key
cross join latest_run r
