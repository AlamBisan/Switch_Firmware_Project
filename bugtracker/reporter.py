"""pytest plugin: auto-generate a structured bug report for every test failure.

Mirrors the JD's "report bugs found during execution" workflow -- instead of
manually filing a ticket after spotting a failure in the terminal, each
failing test writes its own repro-ready report to bugs/.
"""
from __future__ import annotations

import datetime
import pathlib
import re

import pytest

BUGS_DIR = pathlib.Path(__file__).resolve().parent.parent / "bugs"

CATEGORY_SEVERITY = {
    "functional": "Medium",
    "regression": "High",
    "performance": "Medium",
    "security": "High",
}


def _category_from_nodeid(nodeid: str) -> str:
    normalized = nodeid.replace("\\", "/")
    for category in CATEGORY_SEVERITY:
        if f"/{category}/" in normalized:
            return category
    return "uncategorized"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    _write_bug_report(item, report)


def _write_bug_report(item, report) -> None:
    category = _category_from_nodeid(item.nodeid)
    severity = CATEGORY_SEVERITY.get(category, "Medium")
    BUGS_DIR.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^\w.-]", "_", item.nodeid)
    report_path = BUGS_DIR / f"{safe_name}.md"
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    docstring = (item.function.__doc__ or "").strip() if hasattr(item, "function") else ""

    body = f"""# Bug Report: {item.name}

- **Test ID**: `{item.nodeid}`
- **Category**: {category}
- **Severity**: {severity}
- **Detected**: {timestamp}
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
{docstring or "Automated test failure detected during execution."}

## Reproduction
```
pytest -v "{item.nodeid}"
```

## Failure Details
```
{report.longreprtext}
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
"""
    report_path.write_text(body, encoding="utf-8")
