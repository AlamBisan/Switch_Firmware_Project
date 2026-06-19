# SwitchFW QA — Mock Ethernet Switch Firmware Test Automation Framework

A self-contained Python project that simulates an Ethernet switch's
management-plane firmware and puts it through the kind of QA process a
real firmware test team runs: functional/regression/performance/security
test design, an automation framework, seeded real-looking defects, and a
bug reporting + fix-verification workflow. No hardware required — built
to be cloned and run in a couple of minutes.

Built as a portfolio project targeting a **Firmware QA Engineer** role
(network switch/FW testing). See [JD coverage](#jd-coverage) below for how
each requirement of that kind of role maps to a piece of this repo.

## Architecture

```
 dut/client.py  <-- TCP / JSON-lines -->  dut/server.py  -->  dut/firmware.py
 (automation API)                        (mgmt CLI listener)   SwitchFirmware:
                                                                 ports, VLANs,
        ^ used by                                               counters, sensors,
        |                                                       5 seeded bugs
 tests/ (pytest)
   functional/   regression/   performance/   security/
        |  on failure                              |  every run
        v                                           v
 bugtracker/reporter.py --> bugs/*.md      reports/results.xml, report.html, summary.md
 bugtracker/verify_fix.py  (re-runs a bug's test before/after a fix)
```

- **`dut/`** — the device under test: `firmware.py` (state machine + 5
  seeded bugs), `server.py` (TCP management interface, like a switch's
  console/Telnet/Redfish-style endpoint), `client.py` (the automation
  library tests call into), `topology.py` (multi-switch setups).
- **`tests/`** — pytest suite split into the four categories named in the
  job description: functional, regression, performance, security.
- **`bugtracker/`** — auto-generates a Markdown bug report on every test
  failure, plus a `verify_fix.py` CLI that re-runs a bug's test against
  the unfixed and fixed firmware to confirm closure.
- **`docs/`** — requirement-to-test traceability matrix and networking
  concept notes.

## Quickstart

```bash
pip install -r requirements.txt
pytest -v                              # runs all 43 tests, writes reports/ and bugs/
python -m bugtracker.summarize         # writes reports/summary.md
python -m bugtracker.verify_fix --all  # demos the find-bug -> fix -> verify lifecycle
python -m dut.server                   # run the mock switch standalone on :9090
```

Run the suite as-is and you should see **14 failed, 29 passed** — those 14
failures are 5 real-looking firmware defects, seeded on purpose (see
below), each with an auto-generated report waiting in `bugs/`.

## The 5 seeded bugs

Each bug is gated behind a `fixed_bugs` flag in `SwitchFirmware`, so the
exact same code can represent the "buggy" and "R&D-fixed" build. Set
`SWITCHFW_FIXED_BUGS=BUG-001,BUG-003` (comma-separated) before running
pytest to flip specific ones, or use `verify_fix.py` to do it for you.

| ID | Defect | Category | Found by |
|---|---|---|---|
| BUG-001 | Back-to-back speed changes leave `oper_speed` stale while `admin_speed` shows the new value | Regression | `tests/regression/test_bug_001_speed_race.py` |
| BUG-002 | `rx_packets` counter saturates instead of wrapping cleanly under sustained load | Performance | `tests/performance/test_counter_wraparound.py` |
| BUG-003 | VLAN IDs outside the 802.1Q valid range (1-4094) are silently accepted | Security | `tests/security/test_vlan_boundary.py` |
| BUG-004 | Thermal warning is never raised even after temperature crosses the threshold | Regression | `tests/regression/test_bug_004_thermal_warning.py` |
| BUG-005 | Malformed CLI input (missing/invalid args) crashes the parser instead of returning a clean error | Security | `tests/security/test_malformed_commands.py` |

See [`docs/networking_primer.md`](docs/networking_primer.md) for what each
of these actually means in networking terms, and
[`docs/test_plan.md`](docs/test_plan.md) for the full traceability matrix.

## JD coverage

| Job description | This project |
|---|---|
| Review arch/requirements docs for new features | `docs/test_plan.md` traceability matrix derives test cases from named requirements (FW-REQ-01..08) |
| Design, develop, and perform tests for new features | 43 test cases across `tests/functional`, `regression`, `performance`, `security` |
| Automate tests in the automation framework, add new capabilities | `dut/client.py` automation library + pytest fixtures in `tests/conftest.py`, built to be extended with new commands/checks |
| Report bugs, assist repro/debug, verify fixes, raise if not fixed | `bugtracker/reporter.py` (auto bug reports with repro steps) + `bugtracker/verify_fix.py` (before/after fix verification) |
| Regression, performance, functional, security testing; track progress; generate summary reports | All 4 categories implemented; `reports/results.xml`, `report.html`, `summary.md` generated every run |
| Define and build setups/topologies for product coverage | `topology.yaml` + `tests/functional/test_topology_vlan_consistency.py` (2-switch uplink scenario) |
| Scripting in Python | Entire project |
| Knowledge of networking protocols | `docs/networking_primer.md`; VLAN/speed-duplex/counter/thermal modeling throughout |
| Knowledge of Linux/Windows OS | Pure-Python, OS-independent; developed and run on Windows |

## CV bullet drafts

- Built a Python (pytest) test automation framework for a simulated
  Ethernet switch firmware — 43 test cases across functional, regression,
  performance, and security categories, run against both single-device
  and multi-switch topologies.
- Found and documented 5 firmware defects (a config race condition,
  counter overflow, missing input validation, and a parser robustness
  issue) with auto-generated reproduction reports; built a CLI to verify
  fixes by re-running the originating regression test before/after.
- Designed a requirement-to-test-case traceability matrix and an
  automated reporting pipeline (JUnit XML, HTML, Markdown summaries) to
  track test coverage and execution status.

## Repo layout

```
dut/                  mock firmware, TCP server, automation client, topology loader
tests/                functional/, regression/, performance/, security/
bugtracker/           bug auto-reporter plugin, verify_fix CLI, summary generator
bugs/                 auto-generated bug reports (populated by running pytest)
reports/              auto-generated JUnit XML, HTML report, and summary.md
docs/                 test_plan.md (traceability matrix), networking_primer.md
topology.yaml         example 2-switch test topology
```
