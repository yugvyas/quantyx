-- Fails when a source that was producing postings stops appearing entirely.
--
-- The volume test looks at the total, so one dead source among several can
-- hide inside the noise. This catches that case specifically: any source seen
-- in the trailing window but absent from the latest run is a broken
-- integration, not a quiet hiring market.

with latest as (
    select max(observed_date) as run_date from {{ ref('stg_observations') }}
),

recently_active as (

    select distinct o.source
    from {{ ref('stg_observations') }} o
    cross join latest l
    where o.observed_date < l.run_date
      and o.observed_date >= l.run_date - interval ({{ var('drift_min_history_days') }}) day

),

present_now as (

    select distinct o.source
    from {{ ref('stg_observations') }} o
    cross join latest l
    where o.observed_date = l.run_date

),

history as (
    select count(distinct observed_date) as days_available
    from {{ ref('stg_observations') }}
)

select
    r.source as missing_source,
    l.run_date
from recently_active r
cross join latest l
cross join history h
where h.days_available >= 2
  and r.source not in (select source from present_now)
