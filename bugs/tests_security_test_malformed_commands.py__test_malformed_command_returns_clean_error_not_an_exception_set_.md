# Bug Report: test_malformed_command_returns_clean_error_not_an_exception[set]

- **Test ID**: `tests/security/test_malformed_commands.py::test_malformed_command_returns_clean_error_not_an_exception[set]`
- **Category**: security
- **Severity**: High
- **Detected**: 2026-06-19T20:16:00
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
Malformed input must come back as ok=False, never raise an unhandled exception.

## Reproduction
```
pytest -v "tests/security/test_malformed_commands.py::test_malformed_command_returns_clean_error_not_an_exception[set]"
```

## Failure Details
```
firmware = <dut.firmware.SwitchFirmware object at 0x000001CF255617F0>
malformed_cmd = 'set'

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
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <dut.firmware.SwitchFirmware object at 0x000001CF255617F0>
raw_cmd = 'set'

    def _dispatch(self, raw_cmd: str) -> CommandResult:
        tokens = raw_cmd.strip().split()
        if not tokens:
            return CommandResult(False, "ERROR: empty command")
        verb = tokens[0].lower()
    
        if verb == "show":
            sub = tokens[1].lower()
            if sub == "version":
                return self.show_version()
            if sub == "interface":
                return self.show_interface(tokens[2])
            if sub == "port-counters":
                return self.show_port_counters(tokens[2])
            return CommandResult(False, f"ERROR: unknown show target '{sub}'")
    
        if verb == "set":
>           sub = tokens[1].lower()
                  ^^^^^^^^^
E           IndexError: list index out of range

dut\firmware.py:200: IndexError
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
