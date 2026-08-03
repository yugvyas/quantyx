"""Source adapters, one per upstream job-data provider."""

from pipeline.sources.adzuna import AdzunaSource
from pipeline.sources.ashby import AshbySource
from pipeline.sources.base import (
    FetchError,
    FetchResult,
    SourceAdapter,
    build_client,
    gather_bounded,
    get_json,
)
from pipeline.sources.greenhouse import GreenhouseSource
from pipeline.sources.lever import LeverSource

__all__ = [
    "AdzunaSource",
    "AshbySource",
    "FetchError",
    "FetchResult",
    "GreenhouseSource",
    "LeverSource",
    "SourceAdapter",
    "build_client",
    "gather_bounded",
    "get_json",
]
