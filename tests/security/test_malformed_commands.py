"""Security/fuzz test that surfaces BUG-005.

Originally found: the CLI dispatcher indexes tokens and converts types
without validating argument count or type first, so malformed input (a
missing argument, a non-numeric value, or a reference to a nonexistent
port) raises a raw, unhandled exception instead of a clean error response.
A management-plane parser that can be crashed by malformed input is a
robustness/security defect, not just a cosmetic one.

Run `python -m bugtracker.verify_fix BUG-005` to re-run this test against
both the unfixed and fixed firmware builds.
"""
import pytest


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
    result = firmware.execute(malformed_cmd)
    assert result.ok is False, (
        f"command '{malformed_cmd}' did not raise but unexpectedly succeeded"
    )


def test_oversized_command_is_rejected_cleanly(firmware):
    """A command far past the max line length must be rejected by a length guard, not parsed."""
    oversized = "set interface eth1 vlan " + "9" * 10_000
    result = firmware.execute(oversized)
    assert not result.ok
    assert "length" in result.message.lower()
