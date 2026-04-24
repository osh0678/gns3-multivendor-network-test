"""HP Aruba CX (AOS-CX) CLI"""
from typing import List, Optional
from .base import VendorBase


class ArubaCX(VendorBase):
    vendor_name = "Aruba CX"

    def generate_router_config(self, *args, **kwargs) -> List[str]:
        return []

    def generate_switch_config(
        self, hostname, role, vlans, svi_vlan, svi_ip, svi_mask,
        trunk_iface, access_ifaces=None,
    ) -> List[str]:
        prefix_len = sum(bin(int(x)).count("1") for x in svi_mask.split("."))
        vlan_list = ",".join(str(v) for v in vlans)
        cmds = [
            "configure terminal",
            f"hostname {hostname}",
            "!",
        ]
        for v in vlans:
            cmds += [f"vlan {v}", f"    name VLAN{v}", "    exit", "!"]

        # Trunk uplink
        cmds += [
            f"interface {trunk_iface}",
            "    no shutdown",
            "    no routing",
            "    vlan trunk native 1",
            f"    vlan trunk allowed {vlan_list}",
            "    exit",
            "!",
        ]

        if role == "distribution" and access_ifaces:
            for ai in access_ifaces:
                cmds += [
                    f"interface {ai}",
                    "    no shutdown",
                    "    no routing",
                    "    vlan trunk native 1",
                    f"    vlan trunk allowed {vlan_list}",
                    "    exit",
                    "!",
                ]

        cmds += [
            f"interface vlan {svi_vlan}",
            f"    ip address {svi_ip}/{prefix_len}",
            "    no shutdown",
            "    exit",
            "!",
            "end",
            "copy running-config startup-config",
        ]
        return self.banner(hostname) + cmds

    def get_show_vlan_command(self): return "show vlan"
    def get_show_interface_command(self): return "show interface brief"
    def get_ping_command(self, target_ip): return f"ping {target_ip}"
    def get_show_route_command(self): return "show ip route"
    def get_save_config_command(self): return "copy running-config startup-config"
