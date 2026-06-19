"""Functional: true end-to-end coverage over the real TCP wire protocol.

Most tests in this suite call the firmware object directly for speed
(thousands of in-process calls in a load test would be needlessly slow and
flaky over real sockets). This file is the deliberately small set that
exercises the full client -> socket -> server -> firmware path, to catch
transport-layer bugs that in-process calls can't see.
"""


def test_show_version_over_the_wire(live_dut):
    """show version must round-trip correctly through the real TCP/JSON protocol."""
    result = live_dut.show_version()
    assert result["ok"]
    assert result["data"]["hostname"] == "switch01"


def test_set_and_read_back_over_the_wire(live_dut):
    """A config write followed by a status read must round-trip consistently over the wire."""
    live_dut.set_admin_status("eth1", "up")
    live_dut.set_port_speed("eth1", "10G")
    status = live_dut.show_interface("eth1")
    assert status["data"]["admin_status"] == "up"
    assert status["data"]["oper_speed"] == "10G"


def test_unknown_command_returns_clean_error_not_a_dropped_connection(live_dut):
    """An unrecognized command must get a structured error response, not a closed socket."""
    result = live_dut.raw("frobnicate the flux capacitor")
    assert result["ok"] is False
    assert "unknown command" in result["message"].lower()
