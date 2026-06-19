"""Functional: cross-device coverage using the 2-switch topology.

Models a real network engineering check: the trunk VLAN configured on each
end of an inter-switch uplink must match, or traffic on that VLAN won't
pass between the two switches.
"""
import yaml


def test_uplink_trunk_vlan_matches_on_both_ends(two_switch_topology):
    """Both ends of the switch01<->switch02 uplink must agree on the trunk VLAN."""
    with open("topology.yaml", "r", encoding="utf-8") as fh:
        topo = yaml.safe_load(fh)
    link = topo["links"][0]
    trunk_vlan = link["trunk_vlan"]

    switch_a = two_switch_topology[link["a"]["switch"]]
    switch_b = two_switch_topology[link["b"]["switch"]]
    switch_a.execute(f"set interface {link['a']['port']} vlan {trunk_vlan}")
    switch_b.execute(f"set interface {link['b']['port']} vlan {trunk_vlan}")

    vlan_a = switch_a.execute(f"show interface {link['a']['port']}").data["vlan"]
    vlan_b = switch_b.execute(f"show interface {link['b']['port']}").data["vlan"]
    assert vlan_a == vlan_b == trunk_vlan
