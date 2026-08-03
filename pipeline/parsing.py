"""Date and compensation parsing shared across source adapters.

Each upstream encodes these differently (ISO strings, epoch millis, prose
intervals like "per-year-salary" or "1 YEAR"), so the messy part lives here
rather than being re-derived in four places.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

from pipeline.schema import CompPeriod

_PERIOD_PATTERNS: tuple[tuple[re.Pattern[str], CompPeriod], ...] = (
    (re.compile(r"\bhour|hourly\b", re.I), CompPeriod.HOUR),
    (re.compile(r"\bday|daily\b", re.I), CompPeriod.DAY),
    (re.compile(r"\bweek|weekly\b", re.I), CompPeriod.WEEK),
    (re.compile(r"\bmonth|monthly\b", re.I), CompPeriod.MONTH),
    (re.compile(r"\byear|annual|annum|yearly\b", re.I), CompPeriod.YEAR),
)


def parse_period(raw: str | None) -> CompPeriod | None:
    """Map a free-form interval label to a CompPeriod.

    Handles Lever's "per-year-salary" and Ashby's "1 YEAR" with one rule.
    """
    if not raw:
        return None
    for pattern, period in _PERIOD_PATTERNS:
        if pattern.search(raw):
            return period
    return None


def parse_iso_date(raw: str | None) -> date | None:
    """Parse an ISO-8601 timestamp to a UTC calendar date."""
    if not raw:
        return None
    text = str(raw).strip()
    if not text:
        return None
    # fromisoformat in 3.11 handles most shapes but not a trailing "Z".
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = datetime.strptime(text[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc)
    return parsed.date()


def parse_epoch_millis(raw: object) -> date | None:
    """Parse a millisecond epoch (Lever's `createdAt`) to a UTC date."""
    if raw is None:
        return None
    try:
        millis = float(raw)
    except (TypeError, ValueError):
        return None
    if millis <= 0:
        return None
    try:
        return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc).date()
    except (OverflowError, OSError, ValueError):
        return None


def to_float(raw: object) -> float | None:
    """Coerce a numeric-ish value to float, rejecting non-positive amounts."""
    if raw is None or isinstance(raw, bool):
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    return value


_REMOTE_RE = re.compile(r"\bremote\b|\bwork from home\b|\bwfh\b", re.I)
_HYBRID_RE = re.compile(r"\bhybrid\b", re.I)


def looks_remote(*fields: str | None) -> bool:
    """Heuristic remote detection for sources with no explicit flag.

    Hybrid is deliberately not counted as remote — it requires presence, and
    conflating the two would overstate the remote share on the dashboard.
    """
    for value in fields:
        if not value:
            continue
        if _HYBRID_RE.search(value):
            continue
        if _REMOTE_RE.search(value):
            return True
    return False
