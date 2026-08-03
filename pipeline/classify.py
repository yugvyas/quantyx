"""Relevance and seniority classification.

This module decides what the dataset *is*. Every rule here is a plain regex
over text so that any claim the dashboard makes can be traced back to a
matchable pattern — no opaque model, no external API in the daily cron path.

Matching runs on the **title** by design. Descriptions mention "machine
learning" at nearly every startup; a role titled "Backend Engineer" that name
-drops ML is not a data role, and including it would inflate every count.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from pipeline.schema import Posting, Seniority


def _any_word(terms: Iterable[str]) -> re.Pattern[str]:
    """Compile an alternation of word-boundary-anchored terms.

    The alternation MUST be wrapped in a non-capturing group: `|` binds
    loosest, so `(?<!x)a|b|c(?!x)` would apply the lookbehind only to `a` and
    the lookahead only to `c`, letting "Internal" match the term "intern".
    """
    joined = "|".join(re.escape(term) for term in terms)
    return re.compile(rf"(?<![a-z0-9])(?:{joined})(?![a-z0-9])", re.IGNORECASE)


# Core data/AI role vocabulary. Short tokens like "nlp" and "llm" are safe
# here only because of the boundary guards in `_any_word`.
DATA_AI_TERMS = (
    "data scientist",
    "data science",
    "data analyst",
    "data analytics",
    "data engineer",
    "analytics engineer",
    "machine learning",
    "deep learning",
    "mlops",
    "ml engineer",
    "ml scientist",
    "ai engineer",
    "ai scientist",
    "ai research",
    "artificial intelligence",
    "applied scientist",
    "research scientist",
    "research engineer",
    "nlp",
    "natural language",
    "computer vision",
    "business intelligence",
    "bi analyst",
    "bi developer",
    "quantitative analyst",
    "quantitative research",
    "statistician",
    "llm",
    "generative ai",
    "genai",
    "recommendation systems",
    "decision scientist",
    "insights analyst",
)
DATA_AI_RE = _any_word(DATA_AI_TERMS)

# Roles that sit next to data work but are not data work. Applied after a
# positive match, so "AI Account Executive" is correctly rejected.
EXCLUDE_TERMS = (
    "sales",
    "account executive",
    "account manager",
    "recruiter",
    "talent acquisition",
    "customer success",
    "business development",
    "marketing manager",
    "technical writer",
    "copywriter",
    "designer",
    "solutions consultant",
    "sales engineer",
    "partner manager",
)
EXCLUDE_RE = _any_word(EXCLUDE_TERMS)

INTERN_RE = _any_word(
    ("intern", "internship", "trainee", "apprentice", "co-op", "summer analyst")
)
NEW_GRAD_RE = _any_word(
    (
        "new grad",
        "new graduate",
        "graduate program",
        "campus hire",
        "entry level",
        "entry-level",
        "fresher",
        "freshers",
        "university grad",
        "early career",
    )
)
JUNIOR_RE = _any_word(("junior", "jr", "associate"))
SENIOR_RE = _any_word(
    (
        "senior",
        "sr",
        "staff",
        "principal",
        "lead",
        "manager",
        "director",
        "head of",
        "vp",
        "vice president",
        "architect",
        "distinguished",
    )
)

# Indian metros and common spellings, plus the country itself. ATS boards are
# global, so this is what makes the dataset India-focused rather than generic.
INDIA_TERMS = (
    "india",
    "bengaluru",
    "bangalore",
    "mumbai",
    "delhi",
    "new delhi",
    "ncr",
    "gurgaon",
    "gurugram",
    "noida",
    "hyderabad",
    "chennai",
    "pune",
    "kolkata",
    "ahmedabad",
    "jaipur",
    "chandigarh",
    "kochi",
    "cochin",
    "coimbatore",
    "indore",
    "trivandrum",
    "thiruvananthapuram",
    "mysore",
    "mysuru",
    "vadodara",
    "nagpur",
    "bhubaneswar",
    "visakhapatnam",
    "karnataka",
    "maharashtra",
    "telangana",
    "tamil nadu",
    "kerala",
    "gujarat",
)
INDIA_RE = _any_word(INDIA_TERMS)


def is_data_ai_role(title: str) -> bool:
    """True when the title names a data/AI role and not an adjacent one."""
    if not title:
        return False
    if not DATA_AI_RE.search(title):
        return False
    return not EXCLUDE_RE.search(title)


def classify_seniority(title: str, description: str | None = None) -> Seniority:
    """Bucket a posting by career stage.

    Order matters. "Senior" is checked before the junior markers because
    "Senior Associate" is a mid-level role, while intern is checked first
    because it is the most specific signal available.
    """
    text = title or ""

    if INTERN_RE.search(text):
        return Seniority.INTERN
    if SENIOR_RE.search(text):
        return Seniority.MID_PLUS
    if NEW_GRAD_RE.search(text):
        return Seniority.NEW_GRAD
    if JUNIOR_RE.search(text):
        return Seniority.JUNIOR

    # Titles are often bare ("Data Scientist"). Fall back to the description
    # for interns only — that is the one case stated explicitly in the body.
    if description and INTERN_RE.search(description[:1500]):
        return Seniority.INTERN

    return Seniority.UNKNOWN


def is_india_based(location: str | None, *, is_remote: bool = False) -> bool:
    """True when the posting names an Indian location."""
    if not location:
        return False
    return bool(INDIA_RE.search(location))


def classify(posting: Posting) -> Posting:
    """Attach seniority and India tagging to a posting, in place-ish.

    Ashby supplies an authoritative `employmentType` of "Intern"; that already
    -assigned value is never overwritten by the weaker text heuristic.
    """
    if posting.seniority is Seniority.UNKNOWN:
        posting.seniority = classify_seniority(posting.title, posting.description)
    posting.is_india = is_india_based(posting.location, is_remote=posting.is_remote)
    return posting


def keep(posting: Posting) -> bool:
    """The dataset's inclusion rule."""
    return is_data_ai_role(posting.title)
