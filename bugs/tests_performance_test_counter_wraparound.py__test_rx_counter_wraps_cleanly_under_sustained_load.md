# Bug Report: test_rx_counter_wraps_cleanly_under_sustained_load

- **Test ID**: `tests/performance/test_counter_wraparound.py::test_rx_counter_wraps_cleanly_under_sustained_load`
- **Category**: performance
- **Severity**: Medium
- **Detected**: 2026-06-19T20:16:00
- **Firmware version under test**: see `dut/firmware.py` (`fw_version`)

## Summary
Driving traffic well past COUNTER_MAX must wrap the counter, not saturate it.

## Reproduction
```
pytest -v "tests/performance/test_counter_wraparound.py::test_rx_counter_wraps_cleanly_under_sustained_load"
```

## Failure Details
```
firmware = <dut.firmware.SwitchFirmware object at 0x000001CF25427410>

    def test_rx_counter_wraps_cleanly_under_sustained_load(firmware):
        """Driving traffic well past COUNTER_MAX must wrap the counter, not saturate it."""
        packets_per_call = 100
        calls = 700  # 70,000 total packets, comfortably past the 65,535 boundary
        total_packets = packets_per_call * calls
    
        for _ in range(calls):
            firmware.execute(f"simulate traffic eth1 {packets_per_call}")
    
        counters = firmware.execute("show port-counters eth1")
        expected = total_packets % (COUNTER_MAX + 1)
>       assert counters.data["rx_packets"] == expected, (
            f"counter did not wrap correctly under load (got {counters.data['rx_packets']}, "
            f"expected {expected}) -- BUG-002 (counter saturation) has resurfaced"
        )
E       AssertionError: counter did not wrap correctly under load (got 65535, expected 4464) -- BUG-002 (counter saturation) has resurfaced
E       assert 65535 == 4464

tests\performance\test_counter_wraparound.py:24: AssertionError
```

## Status
OPEN -- re-run via `python -m bugtracker.verify_fix <BUG-ID>` once a fix is believed to be in place.
