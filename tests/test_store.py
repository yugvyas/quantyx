"""Storage tests: dedupe, partitioning, and re-run idempotency."""

from __future__ import annotations

import gzip
import json
from datetime import date

import pytest

from pipeline import store
from pipeline.schema import Posting, Source


def _posting(posting_id: str, source: Source = Source.GREENHOUSE, **kwargs) -> Posting:
    base = dict(
        source=source,
        posting_id=posting_id,
        title="Data Scientist",
        company="Acme",
        url="https://example.com",
    )
    base.update(kwargs)
    return Posting(**base)


def test_write_and_read_back_new_postings(tmp_path):
    postings = [_posting("1"), _posting("2"), _posting("3", source=Source.LEVER)]
    counts = store.write_new_postings(postings, date(2026, 1, 5), tmp_path)

    assert counts == {"greenhouse": 2, "lever": 1}
    assert (tmp_path / "postings" / "2026-01-05" / "greenhouse.jsonl.gz").exists()
    assert (tmp_path / "postings" / "2026-01-05" / "lever.jsonl.gz").exists()

    keys = store.known_keys(tmp_path)
    assert keys == {"greenhouse:1", "greenhouse:2", "lever:3"}


def test_known_keys_is_empty_for_a_fresh_tree(tmp_path):
    assert store.known_keys(tmp_path) == set()


def test_observations_are_deduplicated(tmp_path):
    postings = [_posting("1"), _posting("1"), _posting("2")]
    written = store.write_observations(postings, date(2026, 1, 5), tmp_path)

    assert written == 2
    path = tmp_path / "observations" / "2026-01-05.jsonl.gz"
    with gzip.open(path, "rt") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    assert {r["posting_id"] for r in rows} == {"1", "2"}
    assert all(r["observed_date"] == "2026-01-05" for r in rows)


def test_exclude_date_makes_reruns_idempotent(tmp_path):
    """A second run on the same day must rebuild that day's partition in full.

    Without `exclude_date`, run two would see run one's postings as already
    known, write an empty partition, and silently destroy the day's data.
    """
    run_day = date(2026, 1, 5)
    postings = [_posting("1"), _posting("2")]

    store.write_new_postings(postings, run_day, tmp_path)

    # Second run of the same day, same upstream data.
    known = store.known_keys(tmp_path, exclude_date=run_day)
    assert known == set()

    still_new = [p for p in postings if p.key not in known]
    store.write_new_postings(still_new, run_day, tmp_path)

    assert store.known_keys(tmp_path) == {"greenhouse:1", "greenhouse:2"}


def test_prior_days_still_count_as_known(tmp_path):
    store.write_new_postings([_posting("1")], date(2026, 1, 4), tmp_path)
    known = store.known_keys(tmp_path, exclude_date=date(2026, 1, 5))
    assert known == {"greenhouse:1"}


def test_partition_dates_are_sorted(tmp_path):
    for day in [date(2026, 1, 7), date(2026, 1, 5), date(2026, 1, 6)]:
        store.write_observations([_posting("1")], day, tmp_path)

    assert store.partition_dates(tmp_path) == [
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 7),
    ]


def test_corrupt_partition_does_not_crash_known_keys(tmp_path):
    """A truncated .gz must not wedge every future run."""
    store.write_new_postings([_posting("1")], date(2026, 1, 4), tmp_path)
    bad = tmp_path / "postings" / "2026-01-05"
    bad.mkdir(parents=True)
    (bad / "greenhouse.jsonl.gz").write_bytes(b"not actually gzip")

    assert store.known_keys(tmp_path) == {"greenhouse:1"}


def test_writes_are_atomic_on_failure(tmp_path):
    """A crash mid-write must leave no partial file behind."""
    target = tmp_path / "postings" / "2026-01-05" / "greenhouse.jsonl.gz"

    def exploding_lines():
        yield "ok"
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        store._write_gzip_atomic(target, exploding_lines())

    assert not target.exists()
    assert list(target.parent.glob("*.tmp")) == []


def test_partition_is_byte_stable_for_identical_content(tmp_path):
    """Identical data must produce an identical file, or every run makes a
    spurious git diff and the commit history becomes meaningless noise."""
    day = date(2026, 1, 5)
    path = tmp_path / "postings" / day.isoformat() / "greenhouse.jsonl.gz"

    fixed = _posting("1", fetched_at="2026-01-05T00:00:00Z")
    store.write_new_postings([fixed], day, tmp_path)
    first = path.read_bytes()
    store.write_new_postings([fixed], day, tmp_path)

    assert path.read_bytes() == first
