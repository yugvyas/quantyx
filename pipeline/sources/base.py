"""Shared plumbing for source adapters: polite HTTP, retries, bounded fanout."""

from __future__ import annotations

import asyncio
import logging
import os
import random
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Iterable
from dataclasses import dataclass, field
from typing import Any, TypeVar

import httpx

from pipeline.schema import Posting

log = logging.getLogger(__name__)

T = TypeVar("T")

# Identify ourselves honestly. These are public APIs used as intended, and a
# contactable UA is what separates a good citizen from an anonymous bot.
CONTACT_URL = os.getenv("QUANTYX_CONTACT_URL", "https://github.com/yugvyas/quantyx")
USER_AGENT = f"quantyx-job-pipeline/0.1 (+{CONTACT_URL})"

DEFAULT_TIMEOUT = httpx.Timeout(20.0, connect=10.0)
MAX_ATTEMPTS = 4
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


class FetchError(Exception):
    """Raised when a single upstream call fails after exhausting retries."""


@dataclass
class FetchResult:
    """Outcome of one source's run.

    Errors are collected rather than raised so that a single dead company
    slug — or one whole dead source — never takes down the daily run.
    """

    source: str
    postings: list[Posting] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def build_client(**kwargs: Any) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        timeout=DEFAULT_TIMEOUT,
        follow_redirects=True,
        **kwargs,
    )


def _retry_delay(attempt: int, response: httpx.Response | None) -> float:
    """Exponential backoff with jitter, but obey Retry-After when given."""
    if response is not None:
        header = response.headers.get("Retry-After")
        if header:
            try:
                return min(float(header), 60.0)
            except ValueError:
                pass
    return min(2.0**attempt, 30.0) + random.uniform(0, 0.5)


async def get_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    allow_404: bool = False,
) -> Any | None:
    """GET a URL and decode JSON, retrying transient failures.

    Returns None for a 404 when `allow_404` is set — ATS slugs go stale as
    companies churn, and a missing board is expected noise, not an outage.
    """
    last_error: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        response = None
        try:
            response = await client.get(url, params=params)
            if response.status_code == 404 and allow_404:
                return None
            if response.status_code in RETRY_STATUS:
                raise FetchError(f"HTTP {response.status_code} from {url}")
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, FetchError, ValueError) as exc:
            last_error = exc
            if attempt == MAX_ATTEMPTS - 1:
                break
            delay = _retry_delay(attempt, response)
            log.warning(
                "%s (attempt %d/%d), retrying in %.1fs",
                exc,
                attempt + 1,
                MAX_ATTEMPTS,
                delay,
            )
            await asyncio.sleep(delay)

    raise FetchError(f"GET {url} failed after {MAX_ATTEMPTS} attempts: {last_error}")


async def gather_bounded(
    awaitables: Iterable[Awaitable[T]], limit: int = 5
) -> list[T | BaseException]:
    """Run awaitables with at most `limit` in flight, never raising.

    Bounded so we stay a well-behaved client of free public APIs.
    """
    semaphore = asyncio.Semaphore(limit)

    async def _run(aw: Awaitable[T]) -> T:
        async with semaphore:
            return await aw

    return await asyncio.gather(*(_run(aw) for aw in awaitables), return_exceptions=True)


class SourceAdapter(ABC):
    """One upstream job-data provider."""

    name: str

    @abstractmethod
    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        """Fetch and normalize all currently-open postings from this source."""
        raise NotImplementedError
