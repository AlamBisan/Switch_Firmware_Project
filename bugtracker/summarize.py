"""Generate reports/summary.md from the latest JUnit results + open bug reports.

Models the JD's "keep track of testing progress and generate summary
reports of testing activities" -- a quick, reviewable digest instead of
scrolling raw pytest terminal output.

Usage: python -m bugtracker.summarize   (run after `pytest`)
"""
from __future__ import annotations

import pathlib
import xml.etree.ElementTree as ET

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS_XML = PROJECT_ROOT / "reports" / "results.xml"
SUMMARY_MD = PROJECT_ROOT / "reports" / "summary.md"
BUGS_DIR = PROJECT_ROOT / "bugs"

CATEGORIES = ("functional", "regression", "performance", "security", "uncategorized")


def _category_of(classname: str) -> str:
    normalized = classname.replace(".", "/")
    for category in CATEGORIES:
        if f"tests/{category}" in normalized or normalized.startswith(f"{category}/"):
            return category
    return "uncategorized"


def main() -> int:
    if not RESULTS_XML.exists():
        print(f"{RESULTS_XML} not found -- run `pytest` first.")
        return 1

    tree = ET.parse(RESULTS_XML)
    suite = tree.getroot().find("testsuite")

    totals = {c: {"passed": 0, "failed": 0} for c in CATEGORIES}
    for testcase in suite.findall("testcase"):
        category = _category_of(testcase.get("classname", ""))
        failed = testcase.find("failure") is not None or testcase.find("error") is not None
        totals[category]["failed" if failed else "passed"] += 1

    open_bugs = sorted(BUGS_DIR.glob("*.md")) if BUGS_DIR.exists() else []

    lines = [
        "# Test Run Summary",
        "",
        f"- **Total tests**: {suite.get('tests')}",
        f"- **Passed**: {int(suite.get('tests')) - int(suite.get('failures', 0)) - int(suite.get('errors', 0))}",
        f"- **Failed**: {suite.get('failures', 0)}",
        f"- **Errors**: {suite.get('errors', 0)}",
        f"- **Duration**: {float(suite.get('time', 0)):.2f}s",
        "",
        "## By Category",
        "",
        "| Category | Passed | Failed |",
        "|---|---|---|",
    ]
    for category in CATEGORIES:
        counts = totals[category]
        if counts["passed"] or counts["failed"]:
            lines.append(f"| {category} | {counts['passed']} | {counts['failed']} |")

    lines += ["", f"## Open Bugs ({len(open_bugs)})", ""]
    if open_bugs:
        for bug_path in open_bugs:
            lines.append(f"- [{bug_path.stem}](../bugs/{bug_path.name})")
    else:
        lines.append("None -- all known defects verified fixed.")

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
