# Bug Report: test_rejected_vlan_does_not_change_port_state

- **Test ID**: `tests/security/test_vlan_boundary.py::test_rejected_vlan_does_not_change_port_state`
- **Category**: security
- **Severity**: High
- **Detected**: 2026-06-19T20:16:00
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
A rejected VLAN write must leave the port's existing VLAN untouched.

## Reproduction
```
pytest -v "tests/security/test_vlan_boundary.py::test_rejected_vlan_does_not_change_port_state"
```

## Failure Details
```
firmware = <dut.firmware.SwitchFirmware object at 0x000001CF25561EB0>

    def test_rejected_vlan_does_not_change_port_state(firmware):
        """A rejected VLAN write must leave the port's existing VLAN untouched."""
        firmware.execute("set interface eth1 vlan 50")
        firmware.execute("set interface eth1 vlan 99999")  # should be rejected
        status = firmware.execute("show interface eth1")
>       assert status.data["vlan"] == 50
E       assert 99999 == 50

tests\security\test_vlan_boundary.py:27: AssertionError
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
