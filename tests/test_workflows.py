"""GitHub Actions workflow sanity checks.

A malformed workflow does not fail loudly — GitHub reports a run with zero
jobs and no logs, which is easy to mistake for "nothing ran". These tests
catch it locally instead.

The specific bug that motivated them: a plain YAML scalar cannot contain
": ", so

    run: dbt build --vars '{data_dir: ../tests/sample_data}'

is a parse error, while the same text under `run: |` is fine.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

WORKFLOW_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"
WORKFLOWS = sorted(WORKFLOW_DIR.glob("*.yml"))


def test_workflow_directory_is_not_empty():
    assert WORKFLOWS, f"no workflows found in {WORKFLOW_DIR}"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_parses(path: Path):
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict), f"{path.name} did not parse to a mapping"


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_has_triggers_and_jobs(path: Path):
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))

    # PyYAML resolves the bare key `on:` to the boolean True.
    triggers = parsed.get("on", parsed.get(True))
    assert triggers, f"{path.name} declares no triggers"

    jobs = parsed.get("jobs")
    assert jobs, f"{path.name} declares no jobs"
    for name, job in jobs.items():
        assert job.get("runs-on"), f"{path.name}:{name} has no runs-on"
        assert job.get("steps"), f"{path.name}:{name} has no steps"
