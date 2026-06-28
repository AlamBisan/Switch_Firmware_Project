"""Pythonic automation client for the mock switch's TCP management interface.

This is the layer real test automation would call into (instead of crafting raw
CLI strings by hand)
"""
from __future__ import annotations

import json
import socket


class SwitchClient:
    def __init__(self, host: str, port: int, timeout: float = 2.0):
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._rfile = self._sock.makefile("r", encoding="utf-8", newline="\n")
        self._wfile = self._sock.makefile("w", encoding="utf-8", newline="\n")

    def close(self):
        for f in (self._rfile, self._wfile):
            try:
                f.close()
            except OSError:
                pass
        try:
            self._sock.close()
        except OSError:
            pass

    def _send(self, raw_cmd: str) -> dict:
        self._wfile.write(raw_cmd + "\n")
        self._wfile.flush()
        line = self._rfile.readline()
        if not line:
            raise ConnectionError("DUT closed the connection unexpectedly")
        return json.loads(line)

    # -- convenience wrappers over the CLI grammar -------------------- #
    def show_version(self) -> dict:
        return self._send("show version")

    def show_interface(self, port: str) -> dict:
        return self._send(f"show interface {port}")

    def show_port_counters(self, port: str) -> dict:
        return self._send(f"show port-counters {port}")

    def set_admin_status(self, port: str, status: str) -> dict:
        return self._send(f"set interface {port} admin {status}")

    def set_port_speed(self, port: str, speed: str) -> dict:
        return self._send(f"set interface {port} speed {speed}")

    def set_vlan(self, port: str, vlan_id: int) -> dict:
        return self._send(f"set interface {port} vlan {vlan_id}")

    def set_mtu(self, port: str, mtu: int) -> dict:
        return self._send(f"set interface {port} mtu {mtu}")

    def simulate_traffic(self, port: str, packets: int) -> dict:
        return self._send(f"simulate traffic {port} {packets}")

    def inject_errors(self, port: str, count: int) -> dict:
        return self._send(f"inject errors {port} {count}")

    def reboot(self) -> dict:
        return self._send("reboot")

    def raw(self, raw_cmd: str) -> dict:
        return self._send(raw_cmd)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()
