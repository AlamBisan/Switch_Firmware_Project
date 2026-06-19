# Bug Report: test_out_of_range_vlan_is_rejected[9999]

- **Test ID**: `tests/security/test_vlan_boundary.py::test_out_of_range_vlan_is_rejected[9999]`
- **Category**: security
- **Severity**: High
- **Detected**: 2026-06-19T20:16:00
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
VLAN IDs outside 1-4094 must be rejected, not silently applied.

## Reproduction
```
pytest -v "tests/security/test_vlan_boundary.py::test_out_of_range_vlan_is_rejected[9999]"
```

## Failure Details
```
firmware = <dut.firmware.SwitchFirmware object at 0x000001CF25561C70>
invalid_vlan = 9999

    @pytest.mark.parametrize("invalid_vlan", [0, 4095, 9999, -1])
    def test_out_of_range_vlan_is_rejected(firmware, invalid_vlan):
        """VLAN IDs outside 1-4094 must be rejected, not silently applied."""
        result = firmware.execute(f"set interface eth1 vlan {invalid_vlan}")
>       assert not result.ok, (
            f"VLAN {invalid_vlan} was accepted -- BUG-003 (missing VLAN range validation) has resurfaced"
        )
E       AssertionError: VLAN 9999 was accepted -- BUG-003 (missing VLAN range validation) has resurfaced
E       assert not True
E        +  where True = CommandResult(ok=True, message='OK', data={}).ok

tests\security\test_vlan_boundary.py:17: AssertionError
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
