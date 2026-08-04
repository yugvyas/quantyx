"""Source adapter tests — real fixtures for shape, synthetic cases for edges.

No network calls: CI must not depend on a third party's uptime or on a
particular company happening to have a job open.
"""

from __future__ import annotations

from datetime import date

import pytest

from pipeline.registry import CompanyRef
from pipeline.schema import CompPeriod, Posting, Seniority, Source
from pipeline.sources import adzuna, ashby, greenhouse, lever


@pytest.fixture
def acme():
    return CompanyRef(company="Acme Data", ats="greenhouse", slug="acme", hq_country="IN")


# --------------------------------------------------------------------------
# Real-payload shape tests
# --------------------------------------------------------------------------


def test_greenhouse_parses_real_payload(greenhouse_payload, acme):
    jobs = greenhouse_payload["jobs"]
    postings = [greenhouse.parse_job(job, acme) for job in jobs]

    assert postings and all(isinstance(p, Posting) for p in postings)
    for posting in postings:
        assert posting.source is Source.GREENHOUSE
        assert posting.posting_id and posting.title
        # Greenhouse omits the company name; it must come from the registry.
        assert posting.company == "Acme Data"
        assert posting.url.startswith("http")


def test_greenhouse_description_is_flattened_text(greenhouse_payload, acme):
    posting = greenhouse.parse_job(greenhouse_payload["jobs"][0], acme)
    assert posting.description
    # `content` arrives HTML-escaped; neither raw tags nor entities survive.
    assert "<p>" not in posting.description
    assert "&lt;" not in posting.description
    assert "&amp;" not in posting.description


def test_lever_parses_real_payload(lever_payload):
    ref = CompanyRef(company="Meesho", ats="lever", slug="meesho", hq_country="IN")
    postings = [lever.parse_job(job, ref) for job in lever_payload]

    assert postings and all(p is not None for p in postings)
    for posting in postings:
        assert posting.source is Source.LEVER
        assert posting.posted_date is not None  # epoch millis must decode
        assert isinstance(posting.posted_date, date)


def test_ashby_parses_real_payload(ashby_payload):
    ref = CompanyRef(company="Weaviate", ats="ashby", slug="weaviate", hq_country="NL")
    postings = [p for p in (ashby.parse_job(j, ref) for j in ashby_payload["jobs"]) if p]

    assert postings
    for posting in postings:
        assert posting.source is Source.ASHBY
        assert posting.url.startswith("http")


# --------------------------------------------------------------------------
# Edge cases the real fixtures happen not to cover
# --------------------------------------------------------------------------


def test_lever_extracts_salary_range(acme):
    ref = CompanyRef(company="Acme", ats="lever", slug="acme")
    posting = lever.parse_job(
        {
            "id": "abc-123",
            "text": "Senior Data Scientist",
            "categories": {"location": "Bengaluru"},
            "createdAt": 1739562532425,
            "hostedUrl": "https://jobs.lever.co/acme/abc-123",
            "workplaceType": "remote",
            "salaryRange": {
                "min": 2500000,
                "max": 4000000,
                "currency": "INR",
                "interval": "per-year-salary",
            },
        },
        ref,
    )

    assert posting.comp_min == 2500000
    assert posting.comp_max == 4000000
    assert posting.comp_currency == "INR"
    assert posting.comp_period is CompPeriod.YEAR
    assert posting.is_remote is True


def test_lever_hybrid_is_not_remote(acme):
    ref = CompanyRef(company="Acme", ats="lever", slug="acme")
    posting = lever.parse_job(
        {
            "id": "x",
            "text": "Data Analyst",
            "categories": {"location": "Remote-friendly Pune office"},
            "workplaceType": "hybrid",
            "hostedUrl": "https://example.com",
        },
        ref,
    )
    # Hybrid requires presence; counting it as remote overstates remote share.
    assert posting.is_remote is False


def test_ashby_intern_employment_type_wins(acme):
    ref = CompanyRef(company="Acme", ats="ashby", slug="acme")
    posting = ashby.parse_job(
        {
            "id": "job-1",
            "title": "Data Scientist",  # title alone gives no seniority signal
            "location": "Bengaluru",
            "isListed": True,
            "isRemote": False,
            "employmentType": "Intern",
            "jobUrl": "https://jobs.ashbyhq.com/acme/job-1",
            "publishedAt": "2026-01-15T10:30:00.000Z",
        },
        ref,
    )
    assert posting.seniority is Seniority.INTERN
    assert posting.posted_date == date(2026, 1, 15)


def test_ashby_unlisted_posting_is_skipped(acme):
    ref = CompanyRef(company="Acme", ats="ashby", slug="acme")
    assert (
        ashby.parse_job({"id": "d", "title": "Data Scientist", "isListed": False}, ref)
        is None
    )


def test_ashby_picks_salary_over_equity(acme):
    ref = CompanyRef(company="Acme", ats="ashby", slug="acme")
    posting = ashby.parse_job(
        {
            "id": "job-2",
            "title": "ML Engineer",
            "isListed": True,
            "jobUrl": "https://example.com",
            "compensation": {
                "summaryComponents": [
                    {"compensationType": "Equity", "minValue": 1, "maxValue": 2},
                    {
                        "compensationType": "Salary",
                        "minValue": 150000,
                        "maxValue": 200000,
                        "currencyCode": "usd",
                        "interval": "1 YEAR",
                    },
                ]
            },
        },
        ref,
    )
    assert posting.comp_min == 150000
    assert posting.comp_currency == "USD"  # normalized upper-case
    assert posting.comp_period is CompPeriod.YEAR


def test_adzuna_drops_predicted_salary():
    """Adzuna fills gaps with an ML-predicted salary; it is not advertised pay."""
    raw = {
        "id": "999",
        "title": "Data Scientist",
        "company": {"display_name": "Acme"},
        "location": {"display_name": "Bengaluru, Karnataka"},
        "salary_min": 800000,
        "salary_max": 1200000,
        "salary_is_predicted": "1",
        "redirect_url": "https://example.com",
        "created": "2026-01-10T00:00:00Z",
    }
    posting = adzuna.parse_job(raw)
    assert posting.comp_min is None
    assert posting.comp_max is None
    assert posting.comp_currency is None


def test_adzuna_keeps_advertised_salary():
    raw = {
        "id": "1000",
        "title": "Data Scientist",
        "company": {"display_name": "Acme"},
        "location": {"display_name": "Pune"},
        "salary_min": 800000,
        "salary_max": 1200000,
        "salary_is_predicted": "0",
        "redirect_url": "https://example.com",
        "created": "2026-01-10T00:00:00Z",
    }
    posting = adzuna.parse_job(raw)
    assert posting.comp_min == 800000
    assert posting.comp_currency == "INR"
    assert posting.comp_period is CompPeriod.YEAR


@pytest.mark.parametrize(
    "raw",
    [
        {},
        {"id": None, "title": "Data Scientist"},
        {"id": "1", "title": ""},
        {"id": "1"},
    ],
)
def test_parsers_reject_identity_less_rows(raw, acme):
    """A row with no id or title cannot be deduped, so it must not become a Posting."""
    assert greenhouse.parse_job(raw, acme) is None
    assert adzuna.parse_job(raw) is None


def test_adzuna_source_skips_cleanly_without_credentials():
    source = adzuna.AdzunaSource(app_id="", app_key="")
    assert source.configured is False


def test_adzuna_strips_whitespace_from_credentials(monkeypatch):
    """A key pasted with a trailing newline must not reach the query string.

    httpx URL-encodes it to %0A, which looks fine in logs while quietly
    corrupting the credential.
    """
    monkeypatch.setenv("ADZUNA_APP_ID", "  abc123\n")
    monkeypatch.setenv("ADZUNA_APP_KEY", "\ndef456  ")

    source = adzuna.AdzunaSource()

    assert source.app_id == "abc123"
    assert source.app_key == "def456"
    assert source.configured is True


def test_adzuna_whitespace_only_credentials_count_as_unset():
    source = adzuna.AdzunaSource(app_id="   ", app_key="\n")
    assert source.configured is False
