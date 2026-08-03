"""Generate the committed sample dataset used by CI.

CI must not depend on live APIs, but the drift tests need real history to be
meaningful — the volume-collapse test does nothing until 7 days exist. This
derives a small, multi-day dataset from a real pipeline run: genuine titles,
companies and descriptions, with synthetic first-seen and closing dates spread
across a window so lifespan logic has something to chew on.

    python scripts/make_sample_data.py

Re-run it after a schema change so the fixtures track the real shape.
"""

from __future__ import annotations

import gzip
import json
import random
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "data"
TARGET_DIR = REPO_ROOT / "tests" / "sample_data"

DAYS = 8
POSTINGS_PER_SOURCE = 60
DESCRIPTION_CHARS = 1200
SEED = 20260803


def load_real_postings() -> list[dict]:
    records: list[dict] = []
    for partition in sorted((SOURCE_DIR / "postings").glob("*/*.jsonl.gz")):
        with gzip.open(partition, "rt", encoding="utf-8") as handle:
            by_source = [json.loads(line) for line in handle if line.strip()]
        records.extend(by_source[:POSTINGS_PER_SOURCE])
    return records


def write_gzip(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(filename="", mode="wb", fileobj=path.open("wb"), mtime=0) as gz:
        for row in rows:
            gz.write(json.dumps(row, separators=(",", ":")).encode("utf-8"))
            gz.write(b"\n")


def main() -> int:
    rng = random.Random(SEED)
    records = load_real_postings()
    if not records:
        raise SystemExit(
            f"no source data under {SOURCE_DIR} — run `python -m pipeline.run` first"
        )

    last_day = date(2026, 8, 3)
    days = [last_day - timedelta(days=DAYS - 1 - i) for i in range(DAYS)]

    # Assign a lifespan to each posting: a day it appears, and a day it closes
    # (or None if it is still open on the final day).
    lifespans: list[tuple[dict, date, date]] = []
    for record in records:
        start_idx = rng.randrange(0, DAYS)
        # Weight toward still-open so the final day has a healthy count.
        still_open = rng.random() < 0.55
        end_idx = DAYS - 1 if still_open else rng.randrange(start_idx, DAYS)
        lifespans.append((record, days[start_idx], days[end_idx]))

    # Guarantee every source is present on the final day, or
    # assert_no_source_disappeared would fire on clean sample data.
    seen_final: set[str] = {r["source"] for r, _, end in lifespans if end == last_day}
    for record, start, end in lifespans:
        if record["source"] not in seen_final:
            lifespans[lifespans.index((record, start, end))] = (record, start, last_day)
            seen_final.add(record["source"])

    if TARGET_DIR.exists():
        for stale in TARGET_DIR.rglob("*.jsonl.gz"):
            stale.unlink()

    # Full records land in the partition for the day they first appear.
    for day in days:
        by_source: dict[str, list[dict]] = {}
        for record, start, _ in lifespans:
            if start != day:
                continue
            trimmed = dict(record)
            if trimmed.get("description"):
                trimmed["description"] = trimmed["description"][:DESCRIPTION_CHARS]
            by_source.setdefault(record["source"], []).append(trimmed)

        for source, rows in by_source.items():
            write_gzip(
                TARGET_DIR / "postings" / day.isoformat() / f"{source}.jsonl.gz", rows
            )

    # Observation logs: one entry per posting per day it was open.
    for day in days:
        rows = [
            {
                "source": record["source"],
                "posting_id": record["posting_id"],
                "observed_date": day.isoformat(),
            }
            for record, start, end in lifespans
            if start <= day <= end
        ]
        write_gzip(TARGET_DIR / "observations" / f"{day.isoformat()}.jsonl.gz", rows)
        print(f"  {day}: {len(rows)} observations")

    total = sum(1 for _ in lifespans)
    print(f"\nwrote {total} postings across {DAYS} days to {TARGET_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
