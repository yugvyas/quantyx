select
    posting_key,
    source,
    title,
    company,
    location,
    url,
    seniority,
    is_remote,
    is_india,
    comp_min,
    comp_max,
    comp_currency,
    comp_period,
    has_compensation,
    posted_date,
    first_seen_date,
    last_seen_date,
    days_open,
    is_active
from fct_postings
order by first_seen_date desc, company
