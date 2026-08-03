"""Classifier tests.

These rules decide what the dataset contains, so the regression risk is high:
a silently-broadened pattern inflates every count on the dashboard.
"""

from __future__ import annotations

import pytest

from pipeline.classify import (
    classify,
    classify_seniority,
    is_data_ai_role,
    is_india_based,
    keep,
)
from pipeline.schema import Posting, Seniority, Source


@pytest.mark.parametrize(
    "title",
    [
        "Data Scientist",
        "Senior Machine Learning Engineer",
        "Data Analyst",
        "Analytics Engineer II",
        "NLP Research Scientist",
        "Computer Vision Engineer",
        "MLOps Engineer",
        "Business Intelligence Developer",
        "LLM Applied Scientist",
        "Data Engineer, Platform",
    ],
)
def test_accepts_data_roles(title):
    assert is_data_ai_role(title)


@pytest.mark.parametrize(
    "title",
    [
        "Backend Engineer",
        "Product Manager",
        "Frontend Developer",
        "Software Engineer - HTML/CSS",
        "Internal Audit Associate",
        "Customer Support Specialist",
    ],
)
def test_rejects_non_data_roles(title):
    assert not is_data_ai_role(title)


@pytest.mark.parametrize(
    "title",
    [
        "AI Account Executive",
        "Data Analytics Sales Engineer",
        "Machine Learning Recruiter",
        "Analytics Technical Writer",
    ],
)
def test_rejects_roles_adjacent_to_data(title):
    """Mentioning AI does not make a sales or recruiting role a data role."""
    assert not is_data_ai_role(title)


def test_short_tokens_do_not_match_inside_words():
    """Regression: `|` binds loosest, so a naive alternation let "Internal"
    match the term "intern" and "HTML" match "ml"."""
    assert classify_seniority("Internal Audit Analyst") is Seniority.UNKNOWN
    assert not is_data_ai_role("HTML Email Developer")
    assert not is_data_ai_role("Retail Operations Manager")


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Data Science Intern", Seniority.INTERN),
        ("Summer Analyst, Data", Seniority.INTERN),
        ("Machine Learning Trainee", Seniority.INTERN),
        ("Senior Data Scientist", Seniority.MID_PLUS),
        ("Staff ML Engineer", Seniority.MID_PLUS),
        ("Head of Data Science", Seniority.MID_PLUS),
        ("Principal Data Engineer", Seniority.MID_PLUS),
        ("Data Analyst (Fresher)", Seniority.NEW_GRAD),
        ("New Grad Data Scientist", Seniority.NEW_GRAD),
        ("Junior Data Analyst", Seniority.JUNIOR),
        ("Associate Data Scientist", Seniority.JUNIOR),
        ("Data Scientist", Seniority.UNKNOWN),
    ],
)
def test_seniority_buckets(title, expected):
    assert classify_seniority(title) is expected


def test_senior_beats_junior_markers():
    """ "Senior Associate" is a mid-level role, not a junior one."""
    assert classify_seniority("Senior Associate, Data Science") is Seniority.MID_PLUS


def test_intern_falls_back_to_description():
    assert (
        classify_seniority("Data Scientist", "This is a 6 month internship in Pune.")
        is Seniority.INTERN
    )


def test_description_fallback_does_not_override_a_title_signal():
    assert (
        classify_seniority("Senior Data Scientist", "You will mentor our interns.")
        is Seniority.MID_PLUS
    )


@pytest.mark.parametrize(
    "location,expected",
    [
        ("Bengaluru, India", True),
        ("Bangalore", True),
        ("Remote - Pune", True),
        ("Gurugram, Haryana", True),
        ("Hyderabad, Telangana", True),
        ("San Francisco, CA", False),
        ("Remote US", False),
        ("London, UK", False),
        (None, False),
        ("", False),
    ],
)
def test_india_detection(location, expected):
    assert is_india_based(location) is expected


def _posting(**kwargs) -> Posting:
    base = dict(
        source=Source.GREENHOUSE,
        posting_id="1",
        title="Data Scientist",
        company="Acme",
        url="https://example.com",
    )
    base.update(kwargs)
    return Posting(**base)


def test_classify_does_not_overwrite_authoritative_seniority():
    """Ashby's employmentType is stronger evidence than our title heuristic."""
    posting = _posting(title="Senior Data Scientist", seniority=Seniority.INTERN)
    assert classify(posting).seniority is Seniority.INTERN


def test_classify_fills_unknown_seniority_and_india_flag():
    posting = classify(_posting(title="Data Science Intern", location="Bengaluru"))
    assert posting.seniority is Seniority.INTERN
    assert posting.is_india is True


def test_keep_matches_relevance_rule():
    assert keep(_posting(title="Data Scientist"))
    assert not keep(_posting(title="Warehouse Associate"))
