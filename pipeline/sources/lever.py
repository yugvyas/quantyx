"""Lever job boards — public, no auth.

    GET https://api.lever.co/v0/postings/{company}?mode=json

Returns a bare JSON array. `createdAt` is epoch milliseconds and
`salaryRange.interval` is prose like "per-year-salary".
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from pipeline.parsing import (
    looks_remote,
    parse_epoch_millis,
    parse_period,
    to_float,
)
from pipeline.registry import CompanyRef
from pipeline.schema import Posting, Source, html_to_text
from pipeline.sources.base import FetchResult, SourceAdapter, gather_bounded, get_json

log = logging.getLogger(__name__)

API_BASE = "https://api.lever.co/v0/postings"


def parse_job(raw: dict[str, Any], company: CompanyRef) -> Posting | None:
    """Normalize one Lever posting."""
    job_id = raw.get("id")
    title = raw.get("text")
    if not job_id or not title:
        return None

    categories = raw.get("categories") or {}
    location = categories.get("location")
    workplace = (raw.get("workplaceType") or "").strip().lower()

    # Prefer the plain-text description Lever already provides; fall back to
    # flattening the HTML variant.
    description = raw.get("descriptionPlain") or html_to_text(raw.get("description"))

    salary = raw.get("salaryRange") or {}
    comp_min = to_float(salary.get("min"))
    comp_max = to_float(salary.get("max"))
    has_comp = comp_min is not None or comp_max is not None

    return Posting(
        source=Source.LEVER,
        posting_id=str(job_id),
        title=str(title),
        company=company.company,
        url=str(raw.get("hostedUrl") or raw.get("applyUrl") or ""),
        location=location,
        is_remote=workplace == "remote"
        or (workplace != "hybrid" and looks_remote(location, title)),
        comp_min=comp_min,
        comp_max=comp_max,
        comp_currency=salary.get("currency") if has_comp else None,
        comp_period=parse_period(salary.get("interval")) if has_comp else None,
        posted_date=parse_epoch_millis(raw.get("createdAt")),
        description=description,
    )


class LeverSource(SourceAdapter):
    name = Source.LEVER.value

    def __init__(self, companies: list[CompanyRef], concurrency: int = 5) -> None:
        self.companies = companies
        self.concurrency = concurrency

    async def _fetch_board(
        self, client: httpx.AsyncClient, company: CompanyRef
    ) -> list[dict[str, Any]] | None:
        payload = await get_json(
            client,
            f"{API_BASE}/{company.slug}",
            params={"mode": "json"},
            allow_404=True,
        )
        if payload is None:
            return None
        return list(payload) if isinstance(payload, list) else []

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        result = FetchResult(source=self.name)
        if not self.companies:
            return result

        outcomes = await gather_bounded(
            (self._fetch_board(client, company) for company in self.companies),
            limit=self.concurrency,
        )

        for company, jobs in zip(self.companies, outcomes, strict=True):
            if isinstance(jobs, BaseException):
                result.errors.append(f"{company.slug}: {jobs}")
                continue
            if jobs is None:
                result.errors.append(f"{company.slug}: board not found (404)")
                continue
            for raw in jobs:
                try:
                    posting = parse_job(raw, company)
                except Exception as exc:
                    log.warning("lever %s: unparseable job: %s", company.slug, exc)
                    continue
                if posting is not None:
                    result.postings.append(posting)

        return result
