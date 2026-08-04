"""Adzuna India — official API, free tier.

    GET https://api.adzuna.com/v1/api/jobs/in/search/{page}

The free tier is roughly 1,000 calls/month (~33/day), so this adapter runs
against an explicit per-run call budget and never paginates unbounded.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from pipeline.parsing import looks_remote, parse_iso_date, to_float
from pipeline.schema import CompPeriod, Posting, Source
from pipeline.sources.base import FetchResult, SourceAdapter, get_json

log = logging.getLogger(__name__)

API_BASE = "https://api.adzuna.com/v1/api/jobs/in/search"
RESULTS_PER_PAGE = 50

# Search terms that define "DS/AI" for the broad-market source. Kept narrow
# enough that the limited call budget is spent on relevant results.
DEFAULT_QUERIES = (
    "data scientist",
    "machine learning engineer",
    "data analyst intern",
    "data engineer",
    "artificial intelligence intern",
    "data science intern",
)


def parse_job(raw: dict[str, Any]) -> Posting | None:
    """Normalize one Adzuna result.

    Adzuna fills missing salaries with an ML *prediction* and flags it via
    `salary_is_predicted`. Those figures are model output, not advertised pay,
    so they are dropped — including them would quietly poison every salary
    distribution on the dashboard.
    """
    job_id = raw.get("id")
    title = raw.get("title")
    if job_id is None or not title:
        return None

    company = (raw.get("company") or {}).get("display_name") or "Unknown"
    location = (raw.get("location") or {}).get("display_name")
    description = raw.get("description")

    is_predicted = str(raw.get("salary_is_predicted", "0")).strip() == "1"
    comp_min = None if is_predicted else to_float(raw.get("salary_min"))
    comp_max = None if is_predicted else to_float(raw.get("salary_max"))
    has_comp = comp_min is not None or comp_max is not None

    return Posting(
        source=Source.ADZUNA,
        posting_id=str(job_id),
        title=str(title),
        company=str(company),
        url=str(raw.get("redirect_url") or ""),
        location=location,
        is_remote=looks_remote(location, title, description),
        comp_min=comp_min,
        comp_max=comp_max,
        # The /in/ endpoint quotes annual INR.
        comp_currency="INR" if has_comp else None,
        comp_period=CompPeriod.YEAR if has_comp else None,
        posted_date=parse_iso_date(raw.get("created")),
        description=description,
    )


class AdzunaSource(SourceAdapter):
    name = Source.ADZUNA.value

    def __init__(
        self,
        app_id: str | None = None,
        app_key: str | None = None,
        queries: tuple[str, ...] = DEFAULT_QUERIES,
        max_calls: int = 24,
        max_days_old: int = 7,
    ) -> None:
        # Strip whitespace: pasting a key into a secrets form or .env very
        # easily carries a trailing newline, which httpx then URL-encodes into
        # the query string as %0A. Adzuna happens to tolerate that today, but
        # it is a silent time-bomb — the request looks correct in logs while
        # the credential is subtly wrong.
        self.app_id = (app_id or os.getenv("ADZUNA_APP_ID", "")).strip()
        self.app_key = (app_key or os.getenv("ADZUNA_APP_KEY", "")).strip()
        self.queries = queries
        self.max_calls = max_calls
        self.max_days_old = max_days_old

    @property
    def configured(self) -> bool:
        return bool(self.app_id and self.app_key)

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        result = FetchResult(source=self.name)

        if not self.configured:
            # Not an error: the ATS sources need no credentials, so the
            # pipeline stays useful for anyone who has not set Adzuna keys.
            log.info("adzuna: ADZUNA_APP_ID/ADZUNA_APP_KEY unset, skipping source")
            return result

        calls_used = 0
        # Divide the budget evenly so one broad query cannot starve the rest.
        pages_per_query = max(1, self.max_calls // max(1, len(self.queries)))

        for query in self.queries:
            for page in range(1, pages_per_query + 1):
                if calls_used >= self.max_calls:
                    log.info("adzuna: call budget of %d exhausted", self.max_calls)
                    return result

                try:
                    payload = await get_json(
                        client,
                        f"{API_BASE}/{page}",
                        params={
                            "app_id": self.app_id,
                            "app_key": self.app_key,
                            "results_per_page": RESULTS_PER_PAGE,
                            "what": query,
                            "max_days_old": self.max_days_old,
                            "content-type": "application/json",
                        },
                    )
                except Exception as exc:
                    result.errors.append(f"query={query!r} page={page}: {exc}")
                    break
                finally:
                    calls_used += 1

                rows = (payload or {}).get("results") or []
                for raw in rows:
                    try:
                        posting = parse_job(raw)
                    except Exception as exc:
                        log.warning("adzuna: unparseable result: %s", exc)
                        continue
                    if posting is not None:
                        result.postings.append(posting)

                # Short page means we reached the end of this query's results.
                if len(rows) < RESULTS_PER_PAGE:
                    break

        return result
