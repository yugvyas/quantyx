"""Daily pipeline entrypoint: fetch -> classify -> dedupe -> store.

python -m pipeline.run                 # real run, writes partitions
python -m pipeline.run --dry-run       # fetch and report, write nothing
python -m pipeline.run --dry-run --limit 5
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from pipeline import classify, store
from pipeline.registry import by_ats, load_registry
from pipeline.schema import Posting
from pipeline.sources import (
    AdzunaSource,
    AshbySource,
    FetchResult,
    GreenhouseSource,
    LeverSource,
    SourceAdapter,
    build_client,
)

log = logging.getLogger("pipeline.run")

ALL_SOURCES = ("adzuna", "greenhouse", "lever", "ashby")


def build_sources(
    names: tuple[str, ...], limit: int | None, concurrency: int
) -> list[SourceAdapter]:
    """Instantiate the requested adapters, wiring ATS ones to the registry."""
    registry = load_registry()
    if not registry and any(n in names for n in ("greenhouse", "lever", "ashby")):
        log.warning("company registry is empty — ATS sources will return nothing")

    def companies(ats: str):
        refs = by_ats(registry, ats)
        return refs[:limit] if limit else refs

    builders = {
        "adzuna": lambda: AdzunaSource(),
        "greenhouse": lambda: GreenhouseSource(companies("greenhouse"), concurrency),
        "lever": lambda: LeverSource(companies("lever"), concurrency),
        "ashby": lambda: AshbySource(companies("ashby"), concurrency),
    }
    return [builders[name]() for name in names if name in builders]


async def fetch_all(sources: list[SourceAdapter]) -> list[FetchResult]:
    """Run every source. A source that raises is reported, never fatal."""
    async with build_client() as client:
        results = await asyncio.gather(
            *(source.fetch(client) for source in sources), return_exceptions=True
        )

    collected: list[FetchResult] = []
    for source, result in zip(sources, results, strict=True):
        if isinstance(result, BaseException):
            log.error("source %s failed entirely: %s", source.name, result)
            collected.append(FetchResult(source=source.name, errors=[str(result)]))
        else:
            collected.append(result)
    return collected


def select_relevant(results: list[FetchResult]) -> tuple[list[Posting], Counter[str]]:
    """Filter to data/AI roles, classify them, and drop intra-run duplicates."""
    kept: list[Posting] = []
    seen: set[str] = set()
    stats: Counter[str] = Counter()

    for result in results:
        for posting in result.postings:
            stats[f"fetched:{result.source}"] += 1
            if not classify.keep(posting):
                stats["dropped:not_data_role"] += 1
                continue
            if posting.key in seen:
                stats["dropped:duplicate_in_run"] += 1
                continue
            seen.add(posting.key)
            kept.append(classify.classify(posting))
            stats[f"kept:{result.source}"] += 1

    return kept, stats


def summarize(
    postings: list[Posting], new_postings: list[Posting], results: list[FetchResult]
) -> str:
    lines = ["", "=" * 62, "quantyx pipeline summary", "=" * 62]

    for result in results:
        status = "ok" if result.ok else f"{len(result.errors)} error(s)"
        lines.append(f"  {result.source:<12} {len(result.postings):>5} fetched   {status}")

    india = sum(1 for p in postings if p.is_india)
    remote = sum(1 for p in postings if p.is_remote)
    with_comp = sum(1 for p in postings if p.comp_min or p.comp_max)
    seniority = Counter(p.seniority.value for p in postings)

    lines += [
        "-" * 62,
        f"  relevant (data/AI roles) : {len(postings)}",
        f"  new since last run       : {len(new_postings)}",
        f"  india-located            : {india}",
        f"  remote                   : {remote}",
        f"  with real compensation   : {with_comp}",
        f"  seniority                : {dict(seniority)}",
        "=" * 62,
        "",
    ]
    return "\n".join(lines)


async def main_async(args: argparse.Namespace) -> int:
    run_date = (
        date.fromisoformat(args.date) if args.date else datetime.now(timezone.utc).date()
    )
    data_dir = Path(args.data_dir) if args.data_dir else None

    sources = build_sources(tuple(args.sources), args.limit, args.concurrency)
    log.info("running sources: %s (date=%s)", ", ".join(s.name for s in sources), run_date)

    results = await fetch_all(sources)

    for result in results:
        for error in result.errors[:10]:
            log.warning("%s: %s", result.source, error)
        if len(result.errors) > 10:
            log.warning("%s: ...and %d more errors", result.source, len(result.errors) - 10)

    postings, stats = select_relevant(results)
    log.info("classification: %s", dict(stats))

    if not postings:
        log.error("no relevant postings fetched — refusing to write an empty day")
        print(summarize(postings, [], results))
        return 1

    known = store.known_keys(data_dir, exclude_date=run_date)
    new_postings = [p for p in postings if p.key not in known]

    if args.dry_run:
        log.info("dry run: nothing written")
        for posting in new_postings[:10]:
            comp = (
                f"{posting.comp_currency} {posting.comp_min:,.0f}-{posting.comp_max:,.0f}"
                f"/{posting.comp_period}"
                if posting.comp_min and posting.comp_max and posting.comp_period
                else "—"
            )
            print(
                f"  [{posting.source.value:<10}] {posting.title[:52]:<52} "
                f"| {posting.company[:22]:<22} | {(posting.location or '—')[:24]:<24} "
                f"| {posting.seniority.value:<9} | {comp}"
            )
        print(summarize(postings, new_postings, results))
        return 0

    counts = store.write_new_postings(new_postings, run_date, data_dir)
    observed = store.write_observations(postings, run_date, data_dir)

    log.info("wrote %d new postings %s", sum(counts.values()), dict(counts))
    log.info("wrote %d observations for %s", observed, run_date)
    print(summarize(postings, new_postings, results))
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the quantyx daily pipeline.")
    parser.add_argument("--dry-run", action="store_true", help="fetch but write nothing")
    parser.add_argument(
        "--limit", type=int, default=None, help="max companies per ATS (smoke tests)"
    )
    parser.add_argument("--date", default=None, help="override run date (YYYY-MM-DD)")
    parser.add_argument("--data-dir", default=None, help="override the data directory")
    parser.add_argument(
        "--sources",
        nargs="+",
        default=list(ALL_SOURCES),
        choices=list(ALL_SOURCES),
        help="which sources to run",
    )
    parser.add_argument("--concurrency", type=int, default=5, help="max in-flight requests")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)-8s %(name)s: %(message)s",
    )
    load_dotenv()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
