"""Functional: single, non-overlapping port speed configuration.

Note: this deliberately does NOT test back-to-back speed changes -- that
scenario is the historical defect covered in
tests/regression/test_bug_001_speed_race.py. This file only covers the
baseline "does the feature work at all" case.
"""
import pytest

from dut.firmware import ALLOWED_SPEEDS


@pytest.mark.parametrize("speed", ALLOWED_SPEEDS)
def test_set_speed_applies_to_admin_and_oper(firmware, speed):
    """A single speed change must be reflected in both admin_speed and oper_speed."""
    firmware.execute("set interface eth1 admin up")
    result = firmware.execute(f"set interface eth1 speed {speed}")
    assert result.ok
    status = firmware.execute("show interface eth1")
    assert status.data["admin_speed"] == speed
    assert status.data["oper_speed"] == speed


def test_unsupported_speed_is_rejected(firmware):
    """A speed value outside the supported set must be rejected, not silently accepted."""
    result = firmware.execute("set interface eth1 speed 200G")
    assert not result.ok


def test_default_duplex_is_full(firmware):
    """Ports must default to full duplex, matching modern switch behavior."""
    result = firmware.execute("show interface eth1")
    assert result.data["duplex"] == "full"
