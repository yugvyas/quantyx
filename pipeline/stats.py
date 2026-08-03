"""Rewrite the stats block in README.md from the built marts.

Every number published here is read out of `agg_pipeline_stats`, which is
derived from the partitions on disk. Nothing is hand-typed or rounded up, so
any figure quoted from this repo can be reproduced by cloning it and running
`dbt build`. That is deliberate: cite these numbers, not aspirational ones.

    python -m pipeline.stats             # rewrite README.md
    python -m pipeline.stats --check     # exit 1 if README is stale
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "quantyx.duckdb"
DEFAULT_README = REPO_ROOT / "README.md"

START_MARKER = "<!-- STATS:START -->"
END_MARKER = "<!-- STATS:END -->"

QUERY = """
select
    unique_postings,
    total_observations,
    days_of_history,
    first_run_date,
    last_run_date,
    companies_tracked,
    sources_tracked,
    skill_tags_applied,
    distinct_skills_seen,
    active_postings,
    india_postings,
    remote_postings,
    postings_with_comp,
    early_career_postings
from agg_pipeline_stats
"""


def fetch_stats(db_path: Path) -> dict[str, object]:
    if not db_path.exists():
        raise FileNotFoundError(f"{db_path} not found — run `dbt build` first")

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        cursor = con.execute(QUERY)
        columns = [d[0] for d in cursor.description]
        row = cursor.fetchone()
    finally:
        con.close()

    if row is None:
        raise ValueError("agg_pipeline_stats is empty")
    return dict(zip(columns, row, strict=True))


def render(stats: dict[str, object]) -> str:
    def num(key: str) -> str:
        value = stats.get(key)
        return f"{value:,}" if isinstance(value, int) else str(value)

    return "\n".join(
        [
            START_MARKER,
            "",
            f"**{num('unique_postings')}** unique postings · "
            f"**{num('total_observations')}** total observations · "
            f"**{num('days_of_history')}** days of history · "
            f"**{num('companies_tracked')}** companies · "
            f"**{num('sources_tracked')}** sources",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Unique postings | {num('unique_postings')} |",
            f"| Total observations | {num('total_observations')} |",
            f"| Days of history | {num('days_of_history')} |",
            f"| Date range | {stats['first_run_date']} → {stats['last_run_date']} |",
            f"| Currently open | {num('active_postings')} |",
            f"| Companies tracked | {num('companies_tracked')} |",
            f"| Skill tags applied | {num('skill_tags_applied')} |",
            f"| Distinct skills seen | {num('distinct_skills_seen')} |",
            f"| India-located postings | {num('india_postings')} |",
            f"| Remote postings | {num('remote_postings')} |",
            f"| With advertised pay | {num('postings_with_comp')} |",
            f"| Intern / new-grad / junior | {num('early_career_postings')} |",
            "",
            f"_Regenerated automatically on every pipeline run "
            f"(last: {stats['last_run_date']})._",
            "",
            END_MARKER,
        ]
    )


def splice(readme: str, block: str) -> str:
    """Replace the marked region, or append it if the markers are absent."""
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)

    if start == -1 or end == -1 or end < start:
        separator = "" if readme.endswith("\n") else "\n"
        return f"{readme}{separator}\n{block}\n"

    return readme[:start] + block + readme[end + len(END_MARKER) :]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh README stats from the marts.")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--readme", default=str(DEFAULT_README))
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if the README is out of date"
    )
    args = parser.parse_args(argv)

    readme_path = Path(args.readme)
    stats = fetch_stats(Path(args.db))
    updated = splice(readme_path.read_text(encoding="utf-8"), render(stats))

    if args.check:
        if updated != readme_path.read_text(encoding="utf-8"):
            print(
                "README stats are stale — run `python -m pipeline.stats`", file=sys.stderr
            )
            return 1
        print("README stats are up to date")
        return 0

    readme_path.write_text(updated, encoding="utf-8")
    print(f"updated {readme_path} ({stats['unique_postings']} unique postings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
