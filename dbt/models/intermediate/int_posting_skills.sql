{{ config(materialized='view') }}

-- Long-format posting x skill tagging.
--
-- Every skill is a hand-written regex in the `skills_dictionary` seed, so any
-- number on the skills dashboard traces back to a pattern you can read. The
-- patterns are anchored with \b because DuckDB uses RE2: without the anchors
-- "SQL" matches inside "MySQL" and "GraphQL" and the counts become fiction.
-- (RE2 has no lookahead, so the seed must not use any.)

with postings as (

    select
        posting_key,
        source,
        posting_id,
        lower(coalesce(title, '') || ' ' || coalesce(description, '')) as searchable_text
    from {{ ref('int_postings_lifespan') }}

),

skills as (

    select canonical_skill, category, pattern
    from {{ ref('skills_dictionary') }}

)

select
    p.posting_key,
    p.source,
    p.posting_id,
    s.canonical_skill,
    s.category
from postings p
cross join skills s
where regexp_matches(p.searchable_text, s.pattern)
