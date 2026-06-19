# Bug Report: test_malformed_command_returns_clean_error_not_an_exception[show interface eth99]

- **Test ID**: `tests/security/test_malformed_commands.py::test_malformed_command_returns_clean_error_not_an_exception[show interface eth99]`
- **Category**: security
- **Severity**: High
- **Detected**: 2026-06-19T20:16:00
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
Malformed input must come back as ok=False, never raise an unhandled exception.

## Reproduction
```
pytest -v "tests/security/test_malformed_commands.py::test_malformed_command_returns_clean_error_not_an_exception[show interface eth99]"
```

## Failure Details
```
firmware = <dut.firmware.SwitchFirmware object at 0x000001CF255615B0>
malformed_cmd = 'show interface eth99'

    @pytest.mark.parametrize(
        "malformed_cmd",
        [
            "set interface eth1 speed",          # missing the value
            "set interface eth1 vlan",            # missing the value
            "set interface eth1 vlan abc",        # non-numeric value
            "show interface",                     # missing port name
            "show interface eth99",               # reference to a nonexistent port
            "set",                                 # missing everything
        ],
    )
    def test_malformed_command_returns_clean_error_not_an_exception(firmware, malformed_cmd):
        """Malformed input must come back as ok=False, never raise an unhandled exception."""
>       result = firmware.execute(malformed_cmd)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\security\test_malformed_commands.py:29: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
dut\firmware.py:181: in execute
    return self._dispatch(raw_cmd)
           ^^^^^^^^^^^^^^^^^^^^^^^
dut\firmware.py:194: in _dispatch
    return self.show_interface(tokens[2])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
dut\firmware.py:84: in show_interface
    port = self._port(port_name)
           ^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <dut.firmware.SwitchFirmware object at 0x000001CF255615B0>
name = 'eth99'

    def _port(self, name: str) -> Port:
>       return self.ports[name]  # KeyError on unknown port is intentional (see BUG-005)
               ^^^^^^^^^^^^^^^^
E       KeyError: 'eth99'

dut\firmware.py:68: KeyError
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
