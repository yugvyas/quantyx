"""The company registry: which ATS board belongs to which company.

Greenhouse, Lever and Ashby expose per-company job boards, so the breadth of
this pipeline is set by this file rather than by a search query. It is a
hand-curated CSV on purpose — it is the one place a human decides what
"the India DS/AI market" means for this project.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "registry" / "companies.csv"

VALID_ATS = frozenset({"greenhouse", "lever", "ashby"})


@dataclass(frozen=True)
class CompanyRef:
    company: str
    ats: str
    slug: str
    hq_country: str = ""

    def __post_init__(self) -> None:
        if self.ats not in VALID_ATS:
            raise ValueError(
                f"{self.company}: unknown ats {self.ats!r} "
                f"(expected one of {sorted(VALID_ATS)})"
            )


def load_registry(path: Path | None = None) -> list[CompanyRef]:
    """Read the registry CSV, skipping blank rows and `#` comments."""
    target = path or REGISTRY_PATH
    if not target.exists():
        return []

    refs: list[CompanyRef] = []
    seen: set[tuple[str, str]] = set()

    with target.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            slug = (row.get("slug") or "").strip()
            ats = (row.get("ats") or "").strip().lower()
            company = (row.get("company") or "").strip()
            if not slug or slug.startswith("#") or not ats or not company:
                continue

            # A duplicate (ats, slug) would double-count every posting on that
            # board, so drop it here rather than in the dedupe layer.
            identity = (ats, slug)
            if identity in seen:
                continue
            seen.add(identity)

            refs.append(
                CompanyRef(
                    company=company,
                    ats=ats,
                    slug=slug,
                    hq_country=(row.get("hq_country") or "").strip(),
                )
            )

    return refs


def by_ats(refs: list[CompanyRef], ats: str) -> list[CompanyRef]:
    return [ref for ref in refs if ref.ats == ats]
