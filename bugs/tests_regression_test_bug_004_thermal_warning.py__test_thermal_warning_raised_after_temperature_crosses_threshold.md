# Bug Report: test_thermal_warning_raised_after_temperature_crosses_threshold

- **Test ID**: `tests/regression/test_bug_004_thermal_warning.py::test_thermal_warning_raised_after_temperature_crosses_threshold`
- **Category**: regression
- **Severity**: High
- **Detected**: 2026-06-19T20:16:00
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
Enough reboot cycles to cross the thermal threshold must set thermal_warning.

## Reproduction
```
pytest -v "tests/regression/test_bug_004_thermal_warning.py::test_thermal_warning_raised_after_temperature_crosses_threshold"
```

## Failure Details
```
firmware = <dut.firmware.SwitchFirmware object at 0x000001CF25560050>

    def test_thermal_warning_raised_after_temperature_crosses_threshold(firmware):
        """Enough reboot cycles to cross the thermal threshold must set thermal_warning."""
        # Each reboot adds 3C starting from 45C; 12 reboots -> 81C, past the 80C threshold.
        for _ in range(12):
            firmware.execute("reboot")
    
        version = firmware.execute("show version")
        assert version.data["temperature_c"] >= THERMAL_THRESHOLD_C
>       assert version.data["thermal_warning"] is True, (
            "thermal_warning was not raised despite crossing the threshold -- BUG-004 has resurfaced"
        )
E       AssertionError: thermal_warning was not raised despite crossing the threshold -- BUG-004 has resurfaced
E       assert False is True

tests\regression\test_bug_004_thermal_warning.py:23: AssertionError
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
