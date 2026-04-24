"""Fortinet FortiADC / FortiGate CLI (FortiOS 기반)"""
from typing import List, Optional
from .base import VendorBase


class Fortinet(VendorBase):
    vendor_name = "Fortinet"

    def generate_router_config(
        self, hostname, vlan_upper, vlan_lower,
        ip_upper, ip_lower, mask,
        iface_to_dist1, iface_to_dist2, loopback_ip,
    ) -> List[str]:
        cmds = [
            "config system global",
            f"    set hostname {hostname}",
            "end",
            "!",
            f"config system interface",
            f"    edit \"{iface_to_dist1}\"",
            f"        set vdom \"root\"",
            f"        set mode static",
            f"        set type physical",
            f"        set allowaccess ping https ssh",
            f"        set status up",
            "    next",
            "end",
            "!",
            f"config system interface",
            f"    edit \"vlan{vlan_upper}\"",
            f"        set vdom \"root\"",
            f"        set ip {ip_upper} {mask}",
            f"        set allowaccess ping",
            f"        set type vlan",
            f"        set vlanid {vlan_upper}",
            f"        set interface \"{iface_to_dist1}\"",
            f"        set status up",
            "    next",
            "end",
            "!",
            f"config system interface",
            f"    edit \"{iface_to_dist2}\"",
            f"        set vdom \"root\"",
            f"        set mode static",
            f"        set type physical",
            f"        set allowaccess ping https ssh",
            f"        set status up",
            "    next",
            "end",
            "!",
            f"config system interface",
            f"    edit \"vlan{vlan_lower}\"",
            f"        set vdom \"root\"",
            f"        set ip {ip_lower} {mask}",
            f"        set allowaccess ping",
            f"        set type vlan",
            f"        set vlanid {vlan_lower}",
            f"        set interface \"{iface_to_dist2}\"",
            f"        set status up",
            "    next",
            "end",
            "!",
            "config router static",
            "    edit 0",
            "        set dst 0.0.0.0 0.0.0.0",
            "        set device \"port1\"",
            "    next",
            "end",
        ]
        return self.banner(hostname) + cmds

    def generate_switch_config(self, *args, **kwargs) -> List[str]:
        return []  # Fortinet은 라우터/방화벽 전용

    def get_show_vlan_command(self): return "get system interface"
    def get_show_interface_command(self): return "get system interface physical"
    def get_ping_command(self, target_ip): return f"execute ping {target_ip}"
    def get_show_route_command(self): return "get router info routing-table all"
    def get_save_config_command(self): return "execute backup config flash"
