"""Functional: port admin/oper status (link enable/disable)."""
import pytest


def test_port_starts_admin_down(firmware):
    """New ports must boot in admin-down/oper-down state, matching real switch defaults."""
    result = firmware.execute("show interface eth1")
    assert result.data["admin_status"] == "down"
    assert result.data["oper_status"] == "down"


def test_admin_up_brings_oper_status_up(firmware):
    """Enabling a port administratively must bring oper_status up."""
    firmware.execute("set interface eth1 admin up")
    result = firmware.execute("show interface eth1")
    assert result.data["admin_status"] == "up"
    assert result.data["oper_status"] == "up"


def test_admin_down_brings_oper_status_down(firmware):
    """Disabling a port administratively must always force oper_status down."""
    firmware.execute("set interface eth1 admin up")
    firmware.execute("set interface eth1 admin down")
    result = firmware.execute("show interface eth1")
    assert result.data["oper_status"] == "down"


@pytest.mark.parametrize("bad_status", ["enabled", "1", "yes"])
def test_invalid_admin_status_is_rejected(firmware, bad_status):
    """Anything other than the literal 'up'/'down' must be rejected with a clean error."""
    result = firmware.execute(f"set interface eth1 admin {bad_status}")
    assert not result.ok
