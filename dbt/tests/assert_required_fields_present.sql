-- Schema-drift tripwire: a field that silently stops being populated.
--
-- If an upstream renames `hostedUrl` or `absolute_url`, our parser keeps
-- running and keeps producing rows — the field just becomes NULL for every
-- posting from that source. Column-level not_null tests would fire on the
-- whole table and stay red forever because of older good data, so this checks
-- coverage *per source, on the latest partition only*.

with latest as (
    select max(first_seen_date) as run_date from {{ ref('stg_postings') }}
),

latest_rows as (

    select p.*
    from {{ ref('stg_postings') }} p
    cross join latest l
    where p.first_seen_date = l.run_date

),

coverage as (

    select
        source,
        count(*)                                        as rows_written,
        count(url)                                      as url_present,
        count(title)                                    as title_present,
        count(company)                                  as company_present
    from latest_rows
    group by 1

)

select
    source,
    rows_written,
    url_present,
    title_present,
    company_present
from coverage
-- Every one of these is populated by the adapter for every posting. Any gap
-- means the upstream payload changed shape.
where url_present     < rows_written
   or title_present   < rows_written
   or company_present < rows_written
