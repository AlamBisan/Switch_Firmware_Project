"""Regression test for BUG-001.

Originally found: issuing a second `set interface speed` before the first
change was ever polled (`show interface`) left oper_speed stale while
admin_speed showed the new value -- i.e. the firmware reported a speed that
didn't match what was actually configured.

Run `python -m bugtracker.verify_fix BUG-001` to re-run this test against
both the unfixed and fixed firmware builds.
"""


def test_back_to_back_speed_changes_stay_consistent(firmware):
    """Two speed changes issued back-to-back (no intervening poll) must both apply."""
    firmware.execute("set interface eth1 admin up")
    firmware.execute("set interface eth1 speed 10G")
    firmware.execute("set interface eth1 speed 25G")  # second change, no poll in between

    status = firmware.execute("show interface eth1")
    assert status.data["admin_speed"] == "25G"
    assert status.data["oper_speed"] == "25G", (
        "oper_speed is stale -- BUG-001 (speed/duplex race) has resurfaced"
    )


def test_polling_between_changes_avoids_the_race(firmware):
    """Polling status between each change must always keep oper_speed in sync (sanity check)."""
    firmware.execute("set interface eth1 admin up")
    firmware.execute("set interface eth1 speed 10G")
    firmware.execute("show interface eth1")  # poll acknowledges the change
    firmware.execute("set interface eth1 speed 25G")

    status = firmware.execute("show interface eth1")
    assert status.data["oper_speed"] == "25G"
