"""Mock Ethernet switch firmware: in-memory device state + CLI command dispatch.

This stands in for a real switch's management-plane firmware. It is
deliberately seeded with 5 realistic firmware defects (see BUG-00x comments
below), each gated behind `fixed_bugs` so the same code can represent the
"buggy" and "R&D-fixed" build of the firmware. Tests exercise both states.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

ALLOWED_SPEEDS = ("1G", "10G", "25G", "40G", "100G")
COUNTER_MAX = 65535
THERMAL_THRESHOLD_C = 80
VLAN_MIN, VLAN_MAX = 1, 4094
MTU_MIN, MTU_MAX = 64, 9216
MAX_CMD_LEN = 256

ALL_BUGS = {"BUG-001", "BUG-002", "BUG-003", "BUG-004", "BUG-005"}


@dataclass
class CommandResult:
    ok: bool
    message: str = "OK"
    data: dict = field(default_factory=dict)


@dataclass
class Port:
    name: str
    admin_status: str = "down"
    oper_status: str = "down"
    admin_speed: str = "1G"
    oper_speed: str = "1G"
    duplex: str = "full"
    mtu: int = 1500
    vlan: int = 1
    dirty: bool = False  # True = a speed change is pending acknowledgement (poll)
    rx_packets: int = 0
    tx_packets: int = 0
    rx_errors: int = 0
    crc_errors: int = 0


class SwitchFirmware:
    def __init__(
        self,
        hostname: str = "switch01",
        port_names: Optional[list] = None,
        fw_version: str = "FW-3.2.1",
        fixed_bugs: Optional[set] = None,
    ):
        self.hostname = hostname
        self.fw_version = fw_version
        self.fixed_bugs = set(fixed_bugs or [])
        self.reboot_count = 0
        self.uptime_seconds = 0
        self.temperature_c = 45
        self.thermal_warning = False
        self.ports = {name: Port(name=name) for name in (port_names or ["eth1", "eth2", "eth3", "eth4"])}

    def is_fixed(self, bug_id: str) -> bool:
        return bug_id in self.fixed_bugs

    def _port(self, name: str) -> Port:
        return self.ports[name]  # KeyError on unknown port is intentional (see BUG-005)

    # ------------------------------------------------------------------ #
    # Commands
    # ------------------------------------------------------------------ #
    def show_version(self) -> CommandResult:
        return CommandResult(True, "OK", {
            "hostname": self.hostname,
            "fw_version": self.fw_version,
            "uptime_seconds": self.uptime_seconds,
            "reboot_count": self.reboot_count,
            "temperature_c": self.temperature_c,
            "thermal_warning": self.thermal_warning,
        })

    def show_interface(self, port_name: str) -> CommandResult:
        port = self._port(port_name)
        port.dirty = False  # polling status acknowledges any pending speed change
        return CommandResult(True, "OK", asdict(port))

    def show_port_counters(self, port_name: str) -> CommandResult:
        port = self._port(port_name)
        return CommandResult(True, "OK", {
            "rx_packets": port.rx_packets,
            "tx_packets": port.tx_packets,
            "rx_errors": port.rx_errors,
            "crc_errors": port.crc_errors,
        })

    def set_admin_status(self, port_name: str, status: str) -> CommandResult:
        if status not in ("up", "down"):
            return CommandResult(False, f"ERROR: invalid admin status '{status}'")
        port = self._port(port_name)
        port.admin_status = status
        port.oper_status = status if status == "up" else "down"
        return CommandResult(True, "OK")

    def set_port_speed(self, port_name: str, speed: str) -> CommandResult:
        if speed not in ALLOWED_SPEEDS:
            return CommandResult(False, f"ERROR: unsupported speed '{speed}' (allowed: {ALLOWED_SPEEDS})")
        port = self._port(port_name)
        port.admin_speed = speed
        # BUG-001: a second speed change issued before the previous one was
        # ever polled (show interface) silently fails to update oper_speed,
        # leaving admin/oper state inconsistent. Fixed firmware always
        # re-applies oper_speed immediately on every config write.
        if self.is_fixed("BUG-001") or not port.dirty:
            port.oper_speed = speed
        port.dirty = True
        if port.admin_status == "up":
            port.oper_status = "up"
        return CommandResult(True, "OK")

    def set_vlan(self, port_name: str, vlan_id: int) -> CommandResult:
        # BUG-003: VLAN ID range (802.1Q: 1-4094) is not validated.
        if self.is_fixed("BUG-003") and not (VLAN_MIN <= vlan_id <= VLAN_MAX):
            return CommandResult(False, f"ERROR: invalid VLAN id {vlan_id} (must be {VLAN_MIN}-{VLAN_MAX})")
        port = self._port(port_name)
        port.vlan = vlan_id
        return CommandResult(True, "OK")

    def set_mtu(self, port_name: str, mtu: int) -> CommandResult:
        if not (MTU_MIN <= mtu <= MTU_MAX):
            return CommandResult(False, f"ERROR: invalid MTU {mtu} (must be {MTU_MIN}-{MTU_MAX})")
        port = self._port(port_name)
        port.mtu = mtu
        return CommandResult(True, "OK")

    def simulate_traffic(self, port_name: str, packets: int) -> CommandResult:
        port = self._port(port_name)
        # BUG-002: rx_packets counter saturates/clamps at COUNTER_MAX instead
        # of wrapping cleanly, silently dropping counts under sustained load.
        if self.is_fixed("BUG-002"):
            port.rx_packets = (port.rx_packets + packets) % (COUNTER_MAX + 1)
        else:
            port.rx_packets = min(COUNTER_MAX, port.rx_packets + packets)
        port.tx_packets = port.rx_packets
        return CommandResult(True, "OK", {"rx_packets": port.rx_packets})

    def inject_errors(self, port_name: str, count: int) -> CommandResult:
        port = self._port(port_name)
        port.crc_errors += count
        port.rx_errors += count
        return CommandResult(True, "OK", {"crc_errors": port.crc_errors})

    def reboot(self) -> CommandResult:
        self.reboot_count += 1
        self.uptime_seconds = 0
        self.temperature_c = min(95, self.temperature_c + 3)
        # BUG-004: thermal warning is never raised, regardless of temperature.
        if self.is_fixed("BUG-004") and self.temperature_c >= THERMAL_THRESHOLD_C:
            self.thermal_warning = True
        return CommandResult(True, "OK", {
            "reboot_count": self.reboot_count,
            "temperature_c": self.temperature_c,
            "thermal_warning": self.thermal_warning,
        })

    # ------------------------------------------------------------------ #
    # CLI parsing / dispatch
    # ------------------------------------------------------------------ #
    def execute(self, raw_cmd: str) -> CommandResult:
        if len(raw_cmd) > MAX_CMD_LEN:
            return CommandResult(False, f"ERROR: command exceeds max length of {MAX_CMD_LEN} chars")
        # BUG-005: the dispatcher indexes tokens / converts ints without
        # validating count or type first, so malformed input (missing
        # arguments, non-numeric values, unknown ports) raises a raw
        # exception instead of a clean error. Fixed firmware guards it.
        if self.is_fixed("BUG-005"):
            try:
                return self._dispatch(raw_cmd)
            except (IndexError, ValueError, KeyError) as exc:
                return CommandResult(False, f"ERROR: malformed command ({exc.__class__.__name__})")
        return self._dispatch(raw_cmd)

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
            sub = tokens[1].lower()
            if sub == "interface":
                port_name, attr = tokens[2], tokens[3].lower()
                if attr == "admin":
                    return self.set_admin_status(port_name, tokens[4].lower())
                if attr == "speed":
                    return self.set_port_speed(port_name, tokens[4].upper())
                if attr == "vlan":
                    return self.set_vlan(port_name, int(tokens[4]))
                if attr == "mtu":
                    return self.set_mtu(port_name, int(tokens[4]))
                return CommandResult(False, f"ERROR: unknown interface attribute '{attr}'")
            return CommandResult(False, f"ERROR: unknown set target '{sub}'")

        if verb == "simulate" and tokens[1].lower() == "traffic":
            return self.simulate_traffic(tokens[2], int(tokens[3]))

        if verb == "inject" and tokens[1].lower() == "errors":
            return self.inject_errors(tokens[2], int(tokens[3]))

        if verb == "reboot":
            return self.reboot()

        return CommandResult(False, f"ERROR: unknown command '{verb}'")
