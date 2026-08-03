-- Compensation values that cannot be true.
--
-- Guards the salary charts against the failure mode that matters most: a
-- currency or period that goes missing, or a min above a max, silently
-- skewing a published distribution.

select
    posting_key,
    source,
    comp_min,
    comp_max,
    comp_currency,
    comp_period,
    case
        when comp_min > comp_max then 'min_above_max'
        when comp_currency is null then 'missing_currency'
        when comp_period is null then 'missing_period'
        when comp_min <= 0 or comp_max <= 0 then 'non_positive'
    end as problem
from {{ ref('fct_postings') }}
where has_compensation
  and (
        comp_min > comp_max
     or comp_currency is null
     or comp_period is null
     or comp_min <= 0
     or comp_max <= 0
  )
