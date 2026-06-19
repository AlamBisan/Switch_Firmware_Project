"""Re-run a bug's regression test against both firmware builds to verify a fix.

Models the JD's "verify bug fixes provided by R&D team, and raise if not
fixed" workflow: rather than trusting R&D's word that BUG-001 is fixed, this
re-runs the exact regression test that originally caught it -- once against
the baseline (unfixed) build to confirm the defect still reproduces there,
and once against the build with that bug marked fixed.

Usage:
    python -m bugtracker.verify_fix BUG-001
    python -m bugtracker.verify_fix BUG-001 BUG-003 BUG-005
    python -m bugtracker.verify_fix --all
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from dut.firmware import ALL_BUGS

BUG_TEST_MAP = {
    "BUG-001": "tests/regression/test_bug_001_speed_race.py",
    "BUG-002": "tests/performance/test_counter_wraparound.py",
    "BUG-003": "tests/security/test_vlan_boundary.py",
    "BUG-004": "tests/regression/test_bug_004_thermal_warning.py",
    "BUG-005": "tests/security/test_malformed_commands.py",
}


def _run_pytest(test_path: str, fixed_bugs: str) -> int:
    env = os.environ.copy()
    if fixed_bugs:
        env["SWITCHFW_FIXED_BUGS"] = fixed_bugs
    else:
        env.pop("SWITCHFW_FIXED_BUGS", None)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", test_path],
        env=env,
    )
    return result.returncode


def verify(bug_id: str) -> bool:
    test_path = BUG_TEST_MAP[bug_id]
    print(f"\n=== {bug_id}: re-running {test_path} ===")

    print(f"--- baseline (no fixes applied) -- expecting FAIL ---")
    baseline_rc = _run_pytest(test_path, fixed_bugs="")

    print(f"--- with {bug_id} marked fixed -- expecting PASS ---")
    fixed_rc = _run_pytest(test_path, fixed_bugs=bug_id)

    verified = baseline_rc != 0 and fixed_rc == 0
    verdict = "VERIFIED FIXED" if verified else "NOT VERIFIED -- raise back to R&D"
    print(f"\n{bug_id}: baseline exit={baseline_rc} (expected != 0), "
          f"fixed exit={fixed_rc} (expected == 0) -> {verdict}")
    return verified


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bug_ids", nargs="*", help="Bug IDs to verify, e.g. BUG-001")
    parser.add_argument("--all", action="store_true", help="Verify every known bug")
    args = parser.parse_args()

    bug_ids = sorted(ALL_BUGS) if args.all else args.bug_ids
    if not bug_ids:
        parser.error("specify one or more bug IDs, or pass --all")

    unknown = [b for b in bug_ids if b not in BUG_TEST_MAP]
    if unknown:
        parser.error(f"unknown bug id(s): {unknown}; known: {sorted(BUG_TEST_MAP)}")

    results = {bug_id: verify(bug_id) for bug_id in bug_ids}

    print("\n=== Summary ===")
    for bug_id, ok in results.items():
        print(f"  {bug_id}: {'VERIFIED FIXED' if ok else 'NOT VERIFIED'}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
