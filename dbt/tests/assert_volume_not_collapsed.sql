-- Fails when the latest run returned far fewer postings than recent history.
--
-- This is the tripwire for a source that broke quietly: an API that starts
-- returning an empty list, a changed field name that makes every row fail
-- validation, a board token that went stale. Without it the pipeline would
-- cheerfully publish a dashboard showing a market collapse that never happened.
--
-- It deliberately no-ops until there is enough history to have an opinion, so
-- a fresh repo does not fail its own build on day one.

with daily as (

    select observed_date, count(*) as observations
    from {{ ref('stg_observations') }}
    group by 1

),

history as (
    select count(*) as days_available from daily
),

latest as (
    select max(observed_date) as run_date from daily
),

current_run as (
    select d.observed_date, d.observations
    from daily d
    inner join latest l on d.observed_date = l.run_date
),

trailing_window as (
    select avg(d.observations) as avg_observations
    from daily d
    cross join latest l
    where d.observed_date < l.run_date
      and d.observed_date >= l.run_date - interval ({{ var('drift_min_history_days') }}) day
)

select
    c.observed_date,
    c.observations                as current_observations,
    round(t.avg_observations, 1)  as trailing_avg_observations,
    {{ var('drift_min_ratio') }}  as min_ratio
from current_run c
cross join trailing_window t
cross join history h
where h.days_available >= {{ var('drift_min_history_days') }}
  and t.avg_observations is not null
  and c.observations < {{ var('drift_min_ratio') }} * t.avg_observations
