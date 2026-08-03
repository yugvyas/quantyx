{{ config(materialized='view') }}

-- One row per (posting, day-it-was-still-open). This is the cheap log that
-- makes the lifespan model possible: full records are stored only on first
-- sight, so last_seen_date and days_open can only come from here.

with raw as (

    select *
    from read_json_auto(
        '{{ var("data_dir") }}/observations/*.jsonl.gz',
        union_by_name = true
    )

)

select distinct
    lower(trim(source))         as source,
    cast(posting_id as varchar) as posting_id,
    lower(trim(source)) || ':' || cast(posting_id as varchar) as posting_key,
    cast(observed_date as date) as observed_date
from raw
where posting_id is not null
  and observed_date is not null
