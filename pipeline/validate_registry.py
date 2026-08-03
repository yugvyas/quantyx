"""Check that every ATS slug in the registry still resolves.

Companies migrate between ATS vendors and rename their boards, so registry
entries rot silently — a dead slug just contributes zero postings forever.
Run this to find them:

    python -m pipeline.validate_registry
    python -m pipeline.validate_registry --input candidates.csv --prune-to registry/companies.csv
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx

from pipeline.registry import CompanyRef, load_registry
from pipeline.sources import ashby, greenhouse, lever
from pipeline.sources.base import build_client, gather_bounded, get_json

log = logging.getLogger("validate_registry")

STATUS_OK = "ok"
STATUS_MISSING = "not_found"
STATUS_ERROR = "error"


@dataclass
class CheckResult:
    ref: CompanyRef
    status: str
    job_count: int = 0
    detail: str = ""

    @property
    def healthy(self) -> bool:
        return self.status == STATUS_OK


async def check(client: httpx.AsyncClient, ref: CompanyRef) -> CheckResult:
    """Ping one board and report whether it resolves and how many jobs it has."""
    endpoints = {
        "greenhouse": (f"{greenhouse.API_BASE}/{ref.slug}/jobs", {"content": "false"}),
        "lever": (f"{lever.API_BASE}/{ref.slug}", {"mode": "json"}),
        "ashby": (f"{ashby.API_BASE}/{ref.slug}", {}),
    }
    url, params = endpoints[ref.ats]

    try:
        payload = await get_json(client, url, params=params, allow_404=True)
    except Exception as exc:
        return CheckResult(ref, STATUS_ERROR, detail=str(exc)[:120])

    if payload is None:
        return CheckResult(ref, STATUS_MISSING)

    if isinstance(payload, list):
        count = len(payload)
    elif isinstance(payload, dict):
        count = len(payload.get("jobs") or [])
    else:
        return CheckResult(ref, STATUS_ERROR, detail="unexpected payload shape")

    return CheckResult(ref, STATUS_OK, job_count=count)


async def check_all(refs: list[CompanyRef], concurrency: int = 6) -> list[CheckResult]:
    async with build_client() as client:
        outcomes = await gather_bounded(
            (check(client, ref) for ref in refs), limit=concurrency
        )

    results: list[CheckResult] = []
    for ref, outcome in zip(refs, outcomes, strict=True):
        if isinstance(outcome, BaseException):
            results.append(CheckResult(ref, STATUS_ERROR, detail=str(outcome)[:120]))
        else:
            results.append(outcome)
    return results


def write_registry(results: list[CheckResult], path: Path, min_jobs: int = 0) -> int:
    """Write only the healthy entries back out as a registry CSV."""
    healthy = [r for r in results if r.healthy and r.job_count >= min_jobs]
    healthy.sort(key=lambda r: (r.ref.ats, r.ref.company.lower()))

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["company", "ats", "slug", "hq_country"])
        for result in healthy:
            writer.writerow(
                [result.ref.company, result.ref.ats, result.ref.slug, result.ref.hq_country]
            )
    return len(healthy)


def load_candidates(path: Path) -> list[CompanyRef]:
    return load_registry(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ATS slugs in the registry.")
    parser.add_argument(
        "--input", default=None, help="CSV to check (default: the registry)"
    )
    parser.add_argument("--prune-to", default=None, help="write healthy rows to this CSV")
    parser.add_argument(
        "--min-jobs", type=int, default=0, help="with --prune-to, drop boards below this"
    )
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument(
        "--strict", action="store_true", help="exit nonzero if any entry is unhealthy"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.WARNING, format="%(levelname)-8s %(message)s")

    refs = load_candidates(Path(args.input)) if args.input else load_registry()
    if not refs:
        print("no registry entries to check", file=sys.stderr)
        return 1

    results = asyncio.run(check_all(refs, args.concurrency))

    healthy = [r for r in results if r.healthy]
    unhealthy = [r for r in results if not r.healthy]

    for result in sorted(healthy, key=lambda r: -r.job_count):
        print(
            f"  ok        {result.ref.ats:<11} {result.ref.slug:<28} {result.job_count:>4} jobs"
        )
    for result in unhealthy:
        detail = f" ({result.detail})" if result.detail else ""
        print(f"  {result.status:<9} {result.ref.ats:<11} {result.ref.slug:<28}{detail}")

    print(f"\n{len(healthy)}/{len(results)} boards healthy, {len(unhealthy)} dead")

    if args.prune_to:
        written = write_registry(results, Path(args.prune_to), args.min_jobs)
        print(f"wrote {written} healthy entries to {args.prune_to}")

    return 1 if (args.strict and unhealthy) else 0


if __name__ == "__main__":
    sys.exit(main())
