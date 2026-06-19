"""Loads a multi-switch test topology from YAML and builds firmware instances.

Lets test cases target "appropriate product coverage" across more than one
simulated device, e.g. checking config consistency across an inter-switch
uplink, instead of only ever exercising a single box in isolation.
"""
from __future__ import annotations

from typing import Optional

import yaml

from .firmware import SwitchFirmware


def load_topology(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build_switches(topology: dict, fixed_bugs: Optional[set] = None) -> dict:
    switches = {}
    for sw in topology["switches"]:
        switches[sw["name"]] = SwitchFirmware(
            hostname=sw["name"],
            port_names=sw["ports"],
            fw_version=sw.get("fw_version", "FW-3.2.1"),
            fixed_bugs=fixed_bugs,
        )
    return switches
