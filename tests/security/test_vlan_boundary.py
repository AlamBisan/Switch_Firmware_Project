"""Security/negative test that surfaces BUG-003.

Originally found: the firmware never validated VLAN IDs against the 802.1Q
valid range (1-4094) before applying them, silently accepting reserved or
out-of-range values that could cause undefined switching behavior.

Run `python -m bugtracker.verify_fix BUG-003` to re-run this test against
both the unfixed and fixed firmware builds.
"""
import pytest


@pytest.mark.parametrize("invalid_vlan", [0, 4095, 9999, -1])
def test_out_of_range_vlan_is_rejected(firmware, invalid_vlan):
    """VLAN IDs outside 1-4094 must be rejected, not silently applied."""
    result = firmware.execute(f"set interface eth1 vlan {invalid_vlan}")
    assert not result.ok, (
        f"VLAN {invalid_vlan} was accepted -- BUG-003 (missing VLAN range validation) has resurfaced"
    )


def test_rejected_vlan_does_not_change_port_state(firmware):
    """A rejected VLAN write must leave the port's existing VLAN untouched."""
    firmware.execute("set interface eth1 vlan 50")
    firmware.execute("set interface eth1 vlan 99999")  # should be rejected
    status = firmware.execute("show interface eth1")
    assert status.data["vlan"] == 50
