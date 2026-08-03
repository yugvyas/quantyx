{{ config(materialized='view') }}

-- Every posting ever recorded, read straight off the gzipped JSONL partitions.
-- DuckDB globs and decompresses these natively, so there is no load step to
-- keep in sync with the raw files.
--
-- union_by_name is essential: it is what lets a new field appear in a later
-- partition without breaking the read of every older one. Columns absent from
-- an older file arrive as NULL rather than as a hard error.

with raw as (

    select *
    from read_json_auto(
        '{{ var("data_dir") }}/postings/*/*.jsonl.gz',
        union_by_name = true,
        filename = true
    )

),

typed as (

    select
        lower(trim(source))                    as source,
        cast(posting_id as varchar)            as posting_id,
        lower(trim(source)) || ':' || cast(posting_id as varchar) as posting_key,

        trim(title)                            as title,
        trim(company)                          as company,
        url,
        nullif(trim(coalesce(location, '')), '') as location,

        coalesce(cast(is_remote as boolean), false) as is_remote,
        coalesce(cast(is_india  as boolean), false) as is_india,

        cast(comp_min as double)               as comp_min,
        cast(comp_max as double)               as comp_max,
        nullif(upper(trim(coalesce(comp_currency, ''))), '') as comp_currency,
        nullif(lower(trim(coalesce(comp_period, ''))), '')   as comp_period,

        try_cast(posted_date as date)          as posted_date,
        coalesce(nullif(trim(coalesce(seniority, '')), ''), 'unknown') as seniority,
        description,

        try_cast(fetched_at as timestamp)      as fetched_at,
        -- The partition folder is the day we first saw the posting. Deriving it
        -- from the path makes first_seen independent of any field in the row.
        try_cast(
            regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1) as date
        )                                      as first_seen_date

    from raw
    where posting_id is not null
      and nullif(trim(coalesce(title, '')), '') is not null

)

select * from typed
