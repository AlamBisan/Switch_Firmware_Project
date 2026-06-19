"""Performance: timing budgets for repeated management-plane operations.

Real firmware QA tracks not just correctness but responsiveness under
repeated load -- a command that's individually fast but degrades over many
iterations (e.g. a memory/handle leak) is exactly what this kind of test
is designed to catch.
"""
import time


def test_repeated_reboot_cycles_stay_within_time_budget(firmware):
    """20 reboot cycles must complete quickly; a per-cycle slowdown would indicate a leak."""
    cycles = 20
    budget_seconds = 1.0

    start = time.perf_counter()
    for _ in range(cycles):
        firmware.execute("reboot")
    elapsed = time.perf_counter() - start

    assert elapsed < budget_seconds, (
        f"{cycles} reboot cycles took {elapsed:.3f}s, exceeding the {budget_seconds}s budget"
    )


def test_command_round_trip_latency_over_many_calls(firmware):
    """Average per-command latency across many calls must stay well under 5ms (in-process)."""
    iterations = 500
    start = time.perf_counter()
    for _ in range(iterations):
        firmware.execute("show version")
    elapsed = time.perf_counter() - start

    avg_ms = (elapsed / iterations) * 1000
    assert avg_ms < 5.0, f"average command latency {avg_ms:.3f}ms exceeded the 5ms budget"
