"""Greenhouse job boards — public, no auth.

GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from pipeline.parsing import looks_remote, parse_iso_date
from pipeline.registry import CompanyRef
from pipeline.schema import Posting, Source, html_to_text
from pipeline.sources.base import FetchResult, SourceAdapter, gather_bounded, get_json

log = logging.getLogger(__name__)

API_BASE = "https://boards-api.greenhouse.io/v1/boards"


def parse_job(raw: dict[str, Any], company: CompanyRef) -> Posting | None:
    """Normalize one Greenhouse job object.

    Greenhouse does not return the company name (the board token implies it),
    so it comes from the registry. `content` is HTML-escaped markup.
    """
    job_id = raw.get("id")
    title = raw.get("title")
    if job_id is None or not title:
        return None

    location = (raw.get("location") or {}).get("name")
    description = html_to_text(raw.get("content"))

    url = raw.get("absolute_url") or f"https://boards.greenhouse.io/{company.slug}"

    # Greenhouse exposes no structured salary on the public board endpoint,
    # so compensation is intentionally left null rather than guessed at.
    return Posting(
        source=Source.GREENHOUSE,
        posting_id=str(job_id),
        title=str(title),
        company=company.company,
        url=str(url),
        location=location,
        is_remote=looks_remote(location, title),
        posted_date=parse_iso_date(raw.get("first_published") or raw.get("updated_at")),
        description=description,
    )


class GreenhouseSource(SourceAdapter):
    name = Source.GREENHOUSE.value

    def __init__(self, companies: list[CompanyRef], concurrency: int = 5) -> None:
        self.companies = companies
        self.concurrency = concurrency

    async def _fetch_board(
        self, client: httpx.AsyncClient, company: CompanyRef
    ) -> tuple[CompanyRef, list[dict[str, Any]] | None]:
        payload = await get_json(
            client,
            f"{API_BASE}/{company.slug}/jobs",
            params={"content": "true"},
            allow_404=True,
        )
        if payload is None:
            return company, None
        return company, list(payload.get("jobs") or [])

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        result = FetchResult(source=self.name)
        if not self.companies:
            return result

        outcomes = await gather_bounded(
            (self._fetch_board(client, company) for company in self.companies),
            limit=self.concurrency,
        )

        for company, outcome in zip(self.companies, outcomes, strict=True):
            if isinstance(outcome, BaseException):
                result.errors.append(f"{company.slug}: {outcome}")
                continue
            _, jobs = outcome
            if jobs is None:
                result.errors.append(f"{company.slug}: board not found (404)")
                continue
            for raw in jobs:
                try:
                    posting = parse_job(raw, company)
                except Exception as exc:
                    log.warning("greenhouse %s: unparseable job: %s", company.slug, exc)
                    continue
                if posting is not None:
                    result.postings.append(posting)

        return result
