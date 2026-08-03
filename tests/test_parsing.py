"""Parsing helper tests."""

from __future__ import annotations

from datetime import date

import pytest

from pipeline.parsing import (
    looks_remote,
    parse_epoch_millis,
    parse_iso_date,
    parse_period,
    to_float,
)
from pipeline.schema import CompPeriod, Posting, Source, html_to_text


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("per-year-salary", CompPeriod.YEAR),  # Lever
        ("1 YEAR", CompPeriod.YEAR),  # Ashby
        ("per-month-salary", CompPeriod.MONTH),
        ("1 MONTH", CompPeriod.MONTH),
        ("per-hour-wage", CompPeriod.HOUR),
        ("annually", CompPeriod.YEAR),
        ("per annum", CompPeriod.YEAR),
        (None, None),
        ("", None),
        ("per-widget", None),
    ],
)
def test_parse_period(raw, expected):
    assert parse_period(raw) is expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2026-01-15T10:30:00.000Z", date(2026, 1, 15)),
        ("2026-01-15T10:30:00+00:00", date(2026, 1, 15)),
        ("2026-01-15", date(2026, 1, 15)),
        ("2026-01-15T23:30:00-05:00", date(2026, 1, 16)),  # normalized to UTC
        (None, None),
        ("", None),
        ("garbage", None),
    ],
)
def test_parse_iso_date(raw, expected):
    assert parse_iso_date(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        (1739562532425, date(2025, 2, 14)),
        ("1739562532425", date(2025, 2, 14)),
        (0, None),
        (-1, None),
        (None, None),
        ("nonsense", None),
    ],
)
def test_parse_epoch_millis(raw, expected):
    assert parse_epoch_millis(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [(100, 100.0), ("2500.5", 2500.5), (0, None), (-5, None), (None, None), (True, None)],
)
def test_to_float(raw, expected):
    assert to_float(raw) == expected


@pytest.mark.parametrize(
    "fields,expected",
    [
        (("Remote - India",), True),
        (("Work from home",), True),
        (("Hybrid - Bengaluru",), False),  # hybrid requires presence
        (("Bengaluru, India",), False),
        ((None, "Fully Remote"), True),
        ((None, None), False),
    ],
)
def test_looks_remote(fields, expected):
    assert looks_remote(*fields) is expected


def test_html_to_text_strips_markup_and_entities():
    raw = "&lt;p&gt;We use &lt;b&gt;Python&lt;/b&gt; &amp;amp; SQL.&lt;/p&gt;"
    assert html_to_text(raw) == "We use Python & SQL."


def test_html_to_text_preserves_word_boundaries_across_tags():
    """Collapsing block tags to nothing would glue list items into
    "PythonSQL" and silently break skill matching."""
    text = html_to_text("<ul><li>Python</li><li>SQL</li></ul>")
    assert "PythonSQL" not in text
    assert "Python" in text and "SQL" in text


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_html_to_text_handles_empty(raw):
    assert html_to_text(raw) is None


def test_posting_key_is_source_scoped():
    posting = Posting(
        source=Source.LEVER,
        posting_id="abc",
        title="Data Scientist",
        company="Acme",
        url="https://example.com",
    )
    assert posting.key == "lever:abc"


@pytest.mark.parametrize("bad", ["", "   "])
def test_posting_rejects_blank_identity(bad):
    with pytest.raises(ValueError):
        Posting(
            source=Source.LEVER,
            posting_id=bad,
            title="Data Scientist",
            company="Acme",
            url="https://example.com",
        )
