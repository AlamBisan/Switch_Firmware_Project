# Networking Concepts Behind This Project (Interview Prep Notes)

Short, practical notes on the real networking concepts each part of this
project is modeling — useful if asked "walk me through what you tested and
why it matters" in an interview.

## Admin status vs. oper status
Every switch port has two independent states: **admin status** (what an
operator/config wants — enabled or disabled) and **oper(ational) status**
(what's actually happening on the wire right now). They can disagree: a
port can be admin-up but oper-down because the link partner is unplugged,
still negotiating, or faulty. `tests/functional/test_port_status.py` checks
the simple cases; `tests/regression/test_bug_001_speed_race.py` checks a
case where they get out of sync incorrectly — the firmware applies a new
config but the hardware/oper state doesn't catch up to it.

## Speed/duplex negotiation
Ethernet links agree on a speed (1G/10G/25G/40G/100G here) and duplex mode
either via auto-negotiation or static configuration. In real hardware,
changing speed forces the link to retrain (briefly go down and come back
up) — that retraining window is exactly where race conditions like BUG-001
live: if a second config change lands before the first retrain finishes,
firmware can lose track of which speed the hardware actually settled on.

## VLANs (802.1Q)
A VLAN (Virtual LAN) lets one physical switch behave like several isolated
logical networks. VLAN IDs are a 12-bit field per the 802.1Q standard, so
the valid range is 1-4094 (0 and 4095 are reserved). `BUG-003` models a
classic firmware input-validation gap: accepting an out-of-range ID can
lead to undefined switching behavior or interoperability issues with other
vendors' gear. On a real uplink between two switches, both ends must agree
on which VLAN is "trunked" across the link, or traffic on that VLAN won't
pass — that's what `test_topology_vlan_consistency.py` checks across the
2-switch topology in `topology.yaml`.

## Counters and CRC errors
Switches expose hardware counters (packets in/out, errors, CRC failures)
that monitoring systems poll continuously. Real counters are fixed-width
registers that **wrap around** to zero when they overflow — that's normal
and monitoring tooling (e.g. SNMP) is built to expect it. A counter that
instead *saturates* (gets stuck at its max value) silently hides real
traffic volume from anyone monitoring the device — that's `BUG-002`, and
why it only shows up under sustained load, not a quick smoke test.

## Thermal management
Network ASICs throttle or shut down before reaching damaging temperatures,
and firmware is responsible for raising a warning before that point so
operators get a chance to react (e.g. check airflow, reduce load). A
threshold check that's missing or wired up incorrectly (`BUG-004`) means
monitoring never sees the warning, even though the hardware itself is
running hot.

## Management-plane CLI parsing
Real switches expose CLI/Telnet/SSH/Redfish management interfaces that
accept operator or automation commands as text or structured requests. A
parser that isn't defensive about malformed input (missing arguments, bad
types, references to nonexistent interfaces) is a robustness/security
defect, not just a UX annoyance — `BUG-005` and `tests/security/` model
exactly this class of issue, which is the kind of thing fuzz testing in a
real QA role is specifically looking for.
