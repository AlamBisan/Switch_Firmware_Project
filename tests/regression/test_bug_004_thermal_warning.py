"""Regression test for BUG-004.

Originally found: after enough reboot cycles to push temperature_c past the
80C thermal threshold, the firmware never set the thermal_warning flag --
a monitoring system polling `show version` would never know the device was
running hot.

Run `python -m bugtracker.verify_fix BUG-004` to re-run this test against
both the unfixed and fixed firmware builds.
"""

from dut.firmware import THERMAL_THRESHOLD_C


def test_thermal_warning_raised_after_temperature_crosses_threshold(firmware):
    """Enough reboot cycles to cross the thermal threshold must set thermal_warning."""
    # Each reboot adds 3C starting from 45C; 12 reboots -> 81C, past the 80C threshold.
    for _ in range(12):
        firmware.execute("reboot")

    version = firmware.execute("show version")
    assert version.data["temperature_c"] >= THERMAL_THRESHOLD_C
    assert version.data["thermal_warning"] is True, (
        "thermal_warning was not raised despite crossing the threshold -- BUG-004 has resurfaced"
    )


def test_thermal_warning_not_raised_below_threshold(firmware):
    """A single reboot (well below threshold) must not raise a false thermal warning."""
    firmware.execute("reboot")
    version = firmware.execute("show version")
    assert version.data["temperature_c"] < THERMAL_THRESHOLD_C
    assert version.data["thermal_warning"] is False
