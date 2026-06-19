"""Functional: system/version reporting (`show version`)."""


def test_show_version_reports_expected_fields(firmware):
    """show version must report hostname, fw_version, and a cold-boot baseline state."""
    result = firmware.execute("show version")
    assert result.ok
    assert result.data["hostname"] == "switch01"
    assert result.data["fw_version"].startswith("FW-")
    assert result.data["reboot_count"] == 0
    assert result.data["thermal_warning"] is False


def test_reboot_increments_reboot_count(firmware):
    """Each reboot command must increment reboot_count and reset uptime."""
    firmware.execute("reboot")
    firmware.execute("reboot")
    result = firmware.execute("show version")
    assert result.data["reboot_count"] == 2
    assert result.data["uptime_seconds"] == 0
