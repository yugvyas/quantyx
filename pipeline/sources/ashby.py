"""Ashby job boards — public, no auth.

    GET https://api.ashbyhq.com/posting-api/job-board/{name}?includeCompensation=true

Ashby is the richest of the three ATS feeds: an explicit `isRemote` flag, an
`employmentType` that names interns directly, and structured compensation
components.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from pipeline.parsing import looks_remote, parse_iso_date, parse_period, to_float
from pipeline.registry import CompanyRef
from pipeline.schema import Posting, Seniority, Source, html_to_text
from pipeline.sources.base import FetchResult, SourceAdapter, gather_bounded, get_json

log = logging.getLogger(__name__)

API_BASE = "https://api.ashbyhq.com/posting-api/job-board"


def _salary_component(compensation: dict[str, Any]) -> dict[str, Any] | None:
    """Pick the salary component out of Ashby's compensation summary.

    A posting may also carry equity or bonus components; only cash salary is
    comparable across postings.
    """
    for component in compensation.get("summaryComponents") or []:
        if not isinstance(component, dict):
            continue
        if str(component.get("compensationType", "")).lower() == "salary":
            return component
    return None


def parse_job(raw: dict[str, Any], company: CompanyRef) -> Posting | None:
    """Normalize one Ashby job posting."""
    job_id = raw.get("id")
    title = raw.get("title")
    if not job_id or not title:
        return None

    # Unlisted postings are drafts or internal-only; they are not open roles.
    if raw.get("isListed") is False:
        return None

    location = raw.get("location")
    description = raw.get("descriptionPlain") or html_to_text(raw.get("descriptionHtml"))

    comp_min = comp_max = None
    currency = period = None
    component = _salary_component(raw.get("compensation") or {})
    if component:
        comp_min = to_float(component.get("minValue"))
        comp_max = to_float(component.get("maxValue"))
        if comp_min is not None or comp_max is not None:
            currency = component.get("currencyCode")
            period = parse_period(component.get("interval"))

    # employmentType is authoritative when it says "Intern"; the text-based
    # classifier only has the title to go on.
    seniority = Seniority.UNKNOWN
    if str(raw.get("employmentType", "")).strip().lower() == "intern":
        seniority = Seniority.INTERN

    return Posting(
        source=Source.ASHBY,
        posting_id=str(job_id),
        title=str(title),
        company=company.company,
        url=str(raw.get("jobUrl") or raw.get("applyUrl") or ""),
        location=location,
        is_remote=bool(raw.get("isRemote")) or looks_remote(location, title),
        comp_min=comp_min,
        comp_max=comp_max,
        comp_currency=currency,
        comp_period=period,
        posted_date=parse_iso_date(raw.get("publishedAt")),
        description=description,
        seniority=seniority,
    )


class AshbySource(SourceAdapter):
    name = Source.ASHBY.value

    def __init__(self, companies: list[CompanyRef], concurrency: int = 5) -> None:
        self.companies = companies
        self.concurrency = concurrency

    async def _fetch_board(
        self, client: httpx.AsyncClient, company: CompanyRef
    ) -> list[dict[str, Any]] | None:
        payload = await get_json(
            client,
            f"{API_BASE}/{company.slug}",
            params={"includeCompensation": "true"},
            allow_404=True,
        )
        if payload is None:
            return None
        return list(payload.get("jobs") or [])

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
                    log.warning("ashby %s: unparseable job: %s", company.slug, exc)
                    continue
                if posting is not None:
                    result.postings.append(posting)

        return result
