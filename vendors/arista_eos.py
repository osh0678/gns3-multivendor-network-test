"""Arista EOS CLI (vEOS 4.33.1F 스위치용)"""
from typing import List, Optional
from .base import VendorBase


class AristaEOS(VendorBase):
    vendor_name = "Arista EOS"

    def generate_router_config(self, *args, **kwargs) -> List[str]:
        return []  # EOS는 스위치 전용

    def generate_switch_config(
        self, hostname, role, vlans, svi_vlan, svi_ip, svi_mask,
        trunk_iface, access_ifaces=None,
    ) -> List[str]:
        prefix_len = sum(bin(int(x)).count("1") for x in svi_mask.split("."))
        cmds = [
            "enable",
            "configure terminal",
            f"hostname {hostname}",
            "!",
            "spanning-tree mode mstp",
            "!",
        ]
        for v in vlans:
            cmds += [f"vlan {v}", f"   name VLAN{v}", "!"]

        # Trunk uplink
        cmds += [
            f"interface {trunk_iface}",
            "   switchport mode trunk",
            f"   switchport trunk allowed vlan {','.join(str(v) for v in vlans)}",
            "   no shutdown",
            "!",
        ]

        if role == "distribution" and access_ifaces:
            for ai in access_ifaces:
                cmds += [
                    f"interface {ai}",
                    "   switchport mode trunk",
                    f"   switchport trunk allowed vlan {','.join(str(v) for v in vlans)}",
                    "   no shutdown",
                    "!",
                ]

        # SVI (Arista는 CIDR 표기)
        cmds += [
            "ip routing",
            f"interface Vlan{svi_vlan}",
            f"   ip address {svi_ip}/{prefix_len}",
            "   no shutdown",
            "!",
            "end",
            "write memory",
        ]
        return self.banner(hostname) + cmds

    def get_show_vlan_command(self): return "show vlan"
    def get_show_interface_command(self): return "show ip interface brief"
    def get_ping_command(self, target_ip): return f"ping {target_ip}"
    def get_show_route_command(self): return "show ip route"
    def get_save_config_command(self): return "write memory"
