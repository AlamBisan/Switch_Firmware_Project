# Test Plan & Traceability Matrix

Scope: mock Ethernet switch management-plane firmware (`dut/firmware.py`),
exercised both directly (component-level) and over its TCP/JSON management
interface (`dut/server.py` + `dut/client.py`), across a single device and a
2-switch topology (`topology.yaml`).

## Requirements

| Req ID | Requirement |
|---|---|
| FW-REQ-01 | Port admin-status control must deterministically drive oper-status |
| FW-REQ-02 | Port speed/duplex configuration must always be reflected in oper state |
| FW-REQ-03 | VLAN assignment must enforce the 802.1Q valid range (1-4094) |
| FW-REQ-04 | Traffic/error counters must behave correctly under sustained load |
| FW-REQ-05 | System version/thermal reporting must accurately reflect device state |
| FW-REQ-06 | The CLI command parser must reject malformed input cleanly, never crash |
| FW-REQ-07 | Multi-device topologies must allow verifying cross-device config consistency |
| FW-REQ-08 | The TCP/JSON management transport must round-trip commands correctly |

## Traceability Matrix

| Feature | Req ID | Test Case ID | Test File | Type | Automated | Status |
|---|---|---|---|---|---|---|
| Admin/oper status | FW-REQ-01 | TC-FUNC-001 | `tests/functional/test_port_status.py` | Functional | Yes | Passing |
| Speed/duplex config | FW-REQ-02 | TC-FUNC-002 | `tests/functional/test_speed_duplex.py` | Functional | Yes | Passing |
| VLAN assignment (valid range) | FW-REQ-03 | TC-FUNC-003 | `tests/functional/test_vlan.py` | Functional | Yes | Passing |
| Version/system info | FW-REQ-05 | TC-FUNC-004 | `tests/functional/test_version_info.py` | Functional | Yes | Passing |
| Cross-device trunk VLAN consistency | FW-REQ-07 | TC-FUNC-005 | `tests/functional/test_topology_vlan_consistency.py` | Functional | Yes | Passing |
| End-to-end wire protocol | FW-REQ-08 | TC-FUNC-006 | `tests/functional/test_socket_integration.py` | Functional (E2E) | Yes | Passing |
| Back-to-back speed changes | FW-REQ-02 | TC-REG-001 | `tests/regression/test_bug_001_speed_race.py` | Regression | Yes | **Failing (BUG-001 open)** |
| Thermal warning after reboot cycles | FW-REQ-05 | TC-REG-002 | `tests/regression/test_bug_004_thermal_warning.py` | Regression | Yes | **Failing (BUG-004 open)** |
| Counter behavior under sustained load | FW-REQ-04 | TC-PERF-001 | `tests/performance/test_counter_wraparound.py` | Performance | Yes | **Failing (BUG-002 open)** |
| Repeated reboot/command timing budget | FW-REQ-05 | TC-PERF-002 | `tests/performance/test_reboot_cycle_timing.py` | Performance | Yes | Passing |
| VLAN boundary/negative values | FW-REQ-03 | TC-SEC-001 | `tests/security/test_vlan_boundary.py` | Security | Yes | **Failing (BUG-003 open)** |
| Malformed command robustness | FW-REQ-06 | TC-SEC-002 | `tests/security/test_malformed_commands.py` | Security | Yes | **Failing (BUG-005 open)** |

43 automated test cases total (parametrized cases counted individually by
pytest): 29 passing, 14 failing against the current baseline build — see
`reports/summary.md` for the live counts and `bugs/` for the generated
reports behind each failure.

## Why two test levels (direct calls vs. the real socket)

Most suites call `SwitchFirmware` directly (the `firmware` fixture) — fast
and deterministic, which matters for the performance suite's hundreds of
iterations. A small, deliberate subset (`test_socket_integration.py`) goes
through the real TCP/JSON transport (the `live_dut` fixture) to catch bugs
that only exist at the transport layer. BUG-005 is the case study for why
this matters: testing only over the socket would never have found it,
because the server's outer `except Exception` safety net (`dut/server.py`)
catches the raw exception and returns a generic error — the underlying
parser defect only surfaces when the parser is exercised directly.

## Bug-to-test map

| Bug ID | Found via | Verify with |
|---|---|---|
| BUG-001 | TC-REG-001 | `python -m bugtracker.verify_fix BUG-001` |
| BUG-002 | TC-PERF-001 | `python -m bugtracker.verify_fix BUG-002` |
| BUG-003 | TC-SEC-001 | `python -m bugtracker.verify_fix BUG-003` |
| BUG-004 | TC-REG-002 | `python -m bugtracker.verify_fix BUG-004` |
| BUG-005 | TC-SEC-002 | `python -m bugtracker.verify_fix BUG-005` |
