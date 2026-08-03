#!/usr/bin/env bash
#
# Prove the drift tests actually fail on broken data.
#
# A test that has never been seen to fail is not evidence of anything. The
# whole deploy gate rests on these two tripwires, so CI deliberately breaks the
# data and asserts that dbt notices. If this script ever starts passing
# silently, the gate has become decorative.
#
# Run from anywhere:  scripts/verify_drift_detection.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DBT_DIR="$REPO_ROOT/dbt"
SAMPLE="$REPO_ROOT/tests/sample_data"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

PYTHON="${PYTHON:-python}"
DBT="${DBT:-dbt}"

fail() { printf '\n  FAILED: %s\n' "$1" >&2; exit 1; }

run_dbt_test() {
    # Returns 0 if the named test PASSES, 1 if it FAILS.
    (cd "$DBT_DIR" && "$DBT" test --profiles-dir . \
        --select "$1" --vars "{data_dir: $2}" --quiet) >/dev/null 2>&1
}

printf '\n=== Verifying drift detection ===\n\n'

# --------------------------------------------------------------------------
# Case 1: volume collapse — the latest run returns almost nothing.
# --------------------------------------------------------------------------
COLLAPSE="$WORK/collapse"
cp -R "$SAMPLE" "$COLLAPSE"

LATEST="$(ls "$COLLAPSE/observations"/*.jsonl.gz | sort | tail -1)"

"$PYTHON" - "$LATEST" <<'PY'
import gzip, json, sys

path = sys.argv[1]
with gzip.open(path, "rt", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

# Keep one row per source: sources all still present, but volume floors out.
kept, seen = [], set()
for row in rows:
    if row["source"] not in seen:
        seen.add(row["source"])
        kept.append(row)

with gzip.GzipFile(filename="", mode="wb", fileobj=open(path, "wb"), mtime=0) as gz:
    for row in kept:
        gz.write((json.dumps(row, separators=(",", ":")) + "\n").encode())
print(f"  simulated collapse: {len(rows)} -> {len(kept)} observations")
PY

(cd "$DBT_DIR" && "$DBT" run --profiles-dir . --vars "{data_dir: $COLLAPSE}" --quiet) \
    >/dev/null 2>&1 || fail "models would not even build on collapsed data"

if run_dbt_test assert_volume_not_collapsed "$COLLAPSE"; then
    fail "assert_volume_not_collapsed PASSED on collapsed data — the gate is broken"
fi
printf '  ok  assert_volume_not_collapsed correctly failed\n'

# --------------------------------------------------------------------------
# Case 2: a source disappears entirely while the others keep reporting.
# --------------------------------------------------------------------------
MISSING="$WORK/missing"
cp -R "$SAMPLE" "$MISSING"

LATEST="$(ls "$MISSING/observations"/*.jsonl.gz | sort | tail -1)"

"$PYTHON" - "$LATEST" <<'PY'
import gzip, json, sys
from collections import Counter

path = sys.argv[1]
with gzip.open(path, "rt", encoding="utf-8") as fh:
    rows = [json.loads(line) for line in fh if line.strip()]

# Drop the least common source so total volume barely moves — this is exactly
# the case the volume test cannot see.
counts = Counter(r["source"] for r in rows)
victim = min(counts, key=counts.get)
kept = [r for r in rows if r["source"] != victim]

with gzip.GzipFile(filename="", mode="wb", fileobj=open(path, "wb"), mtime=0) as gz:
    for row in kept:
        gz.write((json.dumps(row, separators=(",", ":")) + "\n").encode())
print(f"  simulated dead source: dropped {victim!r} ({counts[victim]} rows)")
PY

(cd "$DBT_DIR" && "$DBT" run --profiles-dir . --vars "{data_dir: $MISSING}" --quiet) \
    >/dev/null 2>&1 || fail "models would not build with a missing source"

if run_dbt_test assert_no_source_disappeared "$MISSING"; then
    fail "assert_no_source_disappeared PASSED with a dead source — the gate is broken"
fi
printf '  ok  assert_no_source_disappeared correctly failed\n'

# --------------------------------------------------------------------------
# Control: the same tests must PASS on healthy data, or they are just noise.
# --------------------------------------------------------------------------
(cd "$DBT_DIR" && "$DBT" run --profiles-dir . --vars "{data_dir: $SAMPLE}" --quiet) \
    >/dev/null 2>&1 || fail "models do not build on the clean sample dataset"

run_dbt_test assert_volume_not_collapsed "$SAMPLE" \
    || fail "assert_volume_not_collapsed fails on healthy data (false positive)"
run_dbt_test assert_no_source_disappeared "$SAMPLE" \
    || fail "assert_no_source_disappeared fails on healthy data (false positive)"
printf '  ok  both tests pass on healthy data\n'

printf '\n=== Drift detection verified ===\n\n'
