"""Raw storage: gzipped JSONL partitions committed to git.

Two datasets, deliberately split:

* `data/postings/<date>/<source>.jsonl.gz` — the full record, written **once**,
  on the day a posting is first seen.
* `data/observations/<date>.jsonl.gz` — just `(source, posting_id)` for every
  posting still open that day. Tiny.

Storing full snapshots daily would re-commit every description every day and
push the repo toward a gigabyte within a year. The observation log costs a few
KB/day and still lets dbt derive last_seen_date, days_open and is_active.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import tempfile
from collections import Counter
from collections.abc import Iterable, Iterator
from datetime import date
from pathlib import Path

from pipeline.schema import Posting

log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
POSTINGS_DIR = "postings"
OBSERVATIONS_DIR = "observations"


def _write_gzip_atomic(path: Path, lines: Iterable[str]) -> None:
    """Write a gzip file atomically.

    A run killed mid-write would otherwise leave a truncated .gz that fails
    every subsequent dbt build until someone deletes it by hand.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        # mtime=0 keeps the gzip header byte-identical for identical content,
        # so an unchanged partition produces no spurious git diff.
        with gzip.GzipFile(filename="", mode="wb", fileobj=tmp.open("wb"), mtime=0) as gz:
            for line in lines:
                gz.write(line.encode("utf-8"))
                gz.write(b"\n")
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def _read_gzip_jsonl(path: Path) -> Iterator[dict]:
    try:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    log.warning("skipping malformed line in %s", path)
    except (OSError, EOFError, gzip.BadGzipFile) as exc:
        log.warning("could not read %s: %s", path, exc)


def known_keys(data_dir: Path | None = None, exclude_date: date | None = None) -> set[str]:
    """Every `source:posting_id` already stored, optionally ignoring one date.

    `exclude_date` makes re-runs idempotent: the current day's partition is
    treated as not-yet-written, so a second run of the same day rebuilds that
    partition in full instead of finding everything "already known" and
    writing an empty file that loses the first run's work.
    """
    root = (data_dir or DATA_DIR) / POSTINGS_DIR
    if not root.exists():
        return set()

    skip = exclude_date.isoformat() if exclude_date else None
    keys: set[str] = set()

    for partition in sorted(root.iterdir()):
        if not partition.is_dir() or partition.name == skip:
            continue
        for path in sorted(partition.glob("*.jsonl.gz")):
            for record in _read_gzip_jsonl(path):
                source = record.get("source")
                posting_id = record.get("posting_id")
                if source and posting_id:
                    keys.add(f"{source}:{posting_id}")

    return keys


def write_new_postings(
    postings: Iterable[Posting], run_date: date, data_dir: Path | None = None
) -> Counter[str]:
    """Write first-sighting records, one file per source. Overwrites the date."""
    root = (data_dir or DATA_DIR) / POSTINGS_DIR / run_date.isoformat()
    grouped: dict[str, list[str]] = {}

    for posting in postings:
        grouped.setdefault(posting.source.value, []).append(
            posting.model_dump_json(exclude_none=False)
        )

    counts: Counter[str] = Counter()
    for source, lines in grouped.items():
        _write_gzip_atomic(root / f"{source}.jsonl.gz", lines)
        counts[source] = len(lines)

    return counts


def write_observations(
    postings: Iterable[Posting], run_date: date, data_dir: Path | None = None
) -> int:
    """Write the day's sighting log. Overwrites the date's file."""
    root = (data_dir or DATA_DIR) / OBSERVATIONS_DIR
    observed = run_date.isoformat()

    seen: set[tuple[str, str]] = set()
    lines: list[str] = []
    for posting in postings:
        identity = (posting.source.value, posting.posting_id)
        if identity in seen:
            continue
        seen.add(identity)
        lines.append(
            json.dumps(
                {
                    "source": identity[0],
                    "posting_id": identity[1],
                    "observed_date": observed,
                },
                separators=(",", ":"),
            )
        )

    _write_gzip_atomic(root / f"{observed}.jsonl.gz", lines)
    return len(lines)


def partition_dates(data_dir: Path | None = None) -> list[date]:
    """Every date with an observation log, ascending."""
    root = (data_dir or DATA_DIR) / OBSERVATIONS_DIR
    if not root.exists():
        return []

    dates: list[date] = []
    for path in root.glob("*.jsonl.gz"):
        try:
            dates.append(date.fromisoformat(path.name.removesuffix(".jsonl.gz")))
        except ValueError:
            continue
    return sorted(dates)
