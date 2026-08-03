"""Shared test fixtures.

The `*_sample.json` files are real, unedited responses from each ATS (trimmed
to a couple of jobs). Testing against real payloads is the point — a
hand-written fixture only ever proves the parser matches our imagination.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.registry import CompanyRef

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str):
    with (FIXTURES / name).open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture
def greenhouse_payload():
    return load_fixture("greenhouse_sample.json")


@pytest.fixture
def lever_payload():
    return load_fixture("lever_sample.json")


@pytest.fixture
def ashby_payload():
    return load_fixture("ashby_sample.json")


@pytest.fixture
def company():
    return CompanyRef(company="Acme Data", ats="greenhouse", slug="acme", hq_country="IN")
