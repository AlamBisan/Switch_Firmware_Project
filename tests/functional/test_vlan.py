"""Functional: VLAN assignment within the valid range.

Complements tests/security/test_vlan_boundary.py, which checks that
out-of-range VLAN IDs get rejected. This file checks that legitimate,
in-range VLAN IDs (including the documented edges 1 and 4094) work.
"""
import pytest

from dut.firmware import VLAN_MAX, VLAN_MIN


@pytest.mark.parametrize("vlan_id", [VLAN_MIN, 100, VLAN_MAX])
def test_valid_vlan_is_accepted(firmware, vlan_id):
    """In-range VLAN IDs, including the 802.1Q boundary values, must be accepted."""
    result = firmware.execute(f"set interface eth1 vlan {vlan_id}")
    assert result.ok
    status = firmware.execute("show interface eth1")
    assert status.data["vlan"] == vlan_id


def test_port_default_vlan_is_1(firmware):
    """Untouched ports must default to VLAN 1 (the standard default VLAN)."""
    result = firmware.execute("show interface eth1")
    assert result.data["vlan"] == 1
