"""The shared contract every source normalizes into.

Four upstream APIs (Adzuna, Greenhouse, Lever, Ashby) return four very
different shapes. Everything downstream of this module — storage, dbt, the
dashboard — only ever sees a `Posting`.
"""

from __future__ import annotations

import html
import re
from datetime import date, datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Source(StrEnum):
    ADZUNA = "adzuna"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"


class CompPeriod(StrEnum):
    """The unit a compensation figure is quoted in.

    Kept explicit rather than normalized to a single unit: an Indian intern
    stipend in INR/month and a US salary in USD/year are not comparable, and
    blending them produces a chart that is confidently wrong.
    """

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class Seniority(StrEnum):
    INTERN = "intern"
    NEW_GRAD = "new_grad"
    JUNIOR = "junior"
    MID_PLUS = "mid_plus"
    UNKNOWN = "unknown"


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\r\f\v]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")
# Block-level tags whose boundaries carry meaning (list items, paragraphs).
# Collapsing them to spaces would glue "Python" and "SQL" into "PythonSQL"
# and break word-boundary skill matching downstream.
_BLOCK_RE = re.compile(
    r"</?(?:p|div|br|li|ul|ol|tr|h[1-6]|section|article)\b[^>]*>",
    re.IGNORECASE,
)


def html_to_text(raw: str | None) -> str | None:
    """Flatten an HTML job description to plain text.

    Greenhouse returns HTML-escaped markup in `content`; Ashby and Lever
    return HTML too. Skill matching runs on this output, so block boundaries
    become newlines to preserve word boundaries.
    """
    if not raw:
        return None
    text = html.unescape(raw)
    text = _BLOCK_RE.sub("\n", text)
    text = _TAG_RE.sub(" ", text)
    # Unescape again: some feeds double-encode (&amp;lt;p&amp;gt;).
    text = html.unescape(text)
    text = _WS_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip() or None


class Posting(BaseModel):
    """One job posting, normalized. One instance == one row in the raw store."""

    source: Source
    posting_id: str
    title: str
    company: str
    url: str

    location: str | None = None
    is_remote: bool = False

    comp_min: float | None = None
    comp_max: float | None = None
    comp_currency: str | None = None
    comp_period: CompPeriod | None = None

    posted_date: date | None = None
    description: str | None = None

    # Assigned by pipeline.classify, not by the source adapters.
    seniority: Seniority = Seniority.UNKNOWN
    is_india: bool = False

    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("posting_id", "title", "company", mode="before")
    @classmethod
    def _require_nonempty(cls, v: object) -> str:
        """Reject blank identity fields early.

        A posting with no ID cannot be deduped and would inflate counts on
        every run; better to drop it loudly at parse time than to silently
        corrupt the lifespan model.
        """
        s = str(v).strip() if v is not None else ""
        if not s:
            raise ValueError("must be a non-empty string")
        return s

    @field_validator("comp_currency", mode="before")
    @classmethod
    def _normalize_currency(cls, v: object) -> str | None:
        if v is None:
            return None
        s = str(v).strip().upper()
        return s or None

    @property
    def key(self) -> str:
        """Stable identity across runs. Dedupe and the lifespan model use this."""
        return f"{self.source.value}:{self.posting_id}"


class Observation(BaseModel):
    """A sighting of a posting on a given day.

    Written every run for every posting still open. Full records are stored
    only once (on first sight), so this tiny log is what lets dbt derive
    last_seen_date / days_open without re-storing descriptions daily.
    """

    source: Source
    posting_id: str
    observed_date: date
