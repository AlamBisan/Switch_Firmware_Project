"""Performance/stress test that surfaces BUG-002.

Originally found: rx_packets is meant to behave like a real hardware
counter and wrap cleanly past its max value under sustained traffic. The
buggy firmware instead clamps/saturates at COUNTER_MAX, silently dropping
counts -- a defect that's invisible on a quick smoke test and only shows
up under sustained load, hence it lives in the performance suite.
"""

from dut.firmware import COUNTER_MAX


def test_rx_counter_wraps_cleanly_under_sustained_load(firmware):
    """Driving traffic well past COUNTER_MAX must wrap the counter, not saturate it."""
    packets_per_call = 100
    calls = 700  # 70,000 total packets, comfortably past the 65,535 boundary
    total_packets = packets_per_call * calls

    for _ in range(calls):
        firmware.execute(f"simulate traffic eth1 {packets_per_call}")

    counters = firmware.execute("show port-counters eth1")
    expected = total_packets % (COUNTER_MAX + 1)
    assert counters.data["rx_packets"] == expected, (
        f"counter did not wrap correctly under load (got {counters.data['rx_packets']}, "
        f"expected {expected}) -- BUG-002 (counter saturation) has resurfaced"
    )


def test_rx_counter_below_max_is_exact(firmware):
    """Well below the wraparound boundary, the counter must just be a plain running total."""
    firmware.execute("simulate traffic eth1 500")
    firmware.execute("simulate traffic eth1 250")
    counters = firmware.execute("show port-counters eth1")
    assert counters.data["rx_packets"] == 750
