# Bug Report: test_back_to_back_speed_changes_stay_consistent

- **Test ID**: `tests/regression/test_bug_001_speed_race.py::test_back_to_back_speed_changes_stay_consistent`
- **Category**: regression
- **Severity**: High
- **Detected**: 2026-06-19T20:16:00
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
Two speed changes issued back-to-back (no intervening poll) must both apply.

## Reproduction
```
pytest -v "tests/regression/test_bug_001_speed_race.py::test_back_to_back_speed_changes_stay_consistent"
```

## Failure Details
```
firmware = <dut.firmware.SwitchFirmware object at 0x000001CF254E7A40>

    def test_back_to_back_speed_changes_stay_consistent(firmware):
        """Two speed changes issued back-to-back (no intervening poll) must both apply."""
        firmware.execute("set interface eth1 admin up")
        firmware.execute("set interface eth1 speed 10G")
        firmware.execute("set interface eth1 speed 25G")  # second change, no poll in between
    
        status = firmware.execute("show interface eth1")
        assert status.data["admin_speed"] == "25G"
>       assert status.data["oper_speed"] == "25G", (
            "oper_speed is stale -- BUG-001 (speed/duplex race) has resurfaced"
        )
E       AssertionError: oper_speed is stale -- BUG-001 (speed/duplex race) has resurfaced
E       assert '10G' == '25G'
E         
E         - 25G
E         + 10G

tests\regression\test_bug_001_speed_race.py:21: AssertionError
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
