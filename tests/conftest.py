"""Shared fixtures for the SwitchFW test suite.

`SWITCHFW_FIXED_BUGS` (comma-separated bug IDs, e.g. "BUG-001,BUG-003") lets
the same test files run against the "buggy" build (default: nothing fixed,
bugs reproduce) or a "fixed" build, without changing any test code. This is
what verify_fix.py uses to demonstrate fix verification.
"""
import os
import threading

import pytest

from dut.client import SwitchClient
from dut.firmware import SwitchFirmware
from dut.server import SwitchServer
from dut.topology import build_switches, load_topology

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fixed_bugs_from_env() -> set:
    raw = os.environ.get("SWITCHFW_FIXED_BUGS", "")
    return {b.strip() for b in raw.split(",") if b.strip()}


@pytest.fixture
def firmware():
    """A fresh in-process mock firmware instance, fast path for most tests."""
    return SwitchFirmware(fixed_bugs=_fixed_bugs_from_env())


@pytest.fixture
def live_dut():
    """A real TCP server + connected client, for true end-to-end coverage."""
    fw = SwitchFirmware(fixed_bugs=_fixed_bugs_from_env())
    server = SwitchServer(fw, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.address
    client = SwitchClient(host, port)
    yield client
    client.close()
    server.shutdown()
    server.server_close()


@pytest.fixture
def two_switch_topology():
    """Two simulated switches joined by an uplink, for cross-device coverage."""
    topo = load_topology(os.path.join(PROJECT_ROOT, "topology.yaml"))
    return build_switches(topo, fixed_bugs=_fixed_bugs_from_env())
