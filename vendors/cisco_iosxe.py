"""Cisco IOS-XE CLI (Catalyst 9000v 스위치용)"""
from typing import List, Optional
from .base import VendorBase


class CiscoIOSXE(VendorBase):
    vendor_name = "Cisco IOS-XE"

    def generate_router_config(self, hostname, vlan_upper, vlan_lower,
                               ip_upper, ip_lower, mask,
                               iface_to_dist1, iface_to_dist2, loopback_ip) -> List[str]:
        return []  # IOS-XE는 스위치 전용

    def generate_switch_config(
        self, hostname, role, vlans, svi_vlan, svi_ip, svi_mask,
        trunk_iface, access_ifaces=None,
    ) -> List[str]:
        cmds = [
            "enable",
            "configure terminal",
            f"hostname {hostname}",
            "!",
        ]
        # VLAN 생성
        for v in vlans:
            cmds += [f"vlan {v}", f" name VLAN{v}", "!"]

        # Trunk 포트 (uplink)
        cmds += [
            f"interface {trunk_iface}",
            " switchport mode trunk",
            f" switchport trunk allowed vlan {','.join(str(v) for v in vlans)}",
            " no shutdown",
            "!",
        ]

        # Distribution: access 스위치로 가는 downlink trunk 포트
        if role == "distribution" and access_ifaces:
            for ai in access_ifaces:
                cmds += [
                    f"interface {ai}",
                    " switchport mode trunk",
                    f" switchport trunk allowed vlan {','.join(str(v) for v in vlans)}",
                    " no shutdown",
                    "!",
                ]

        # SVI
        cmds += [
            f"interface Vlan{svi_vlan}",
            f" ip address {svi_ip} {svi_mask}",
            " no shutdown",
            "!",
            "end",
            "write memory",
        ]
        return self.banner(hostname) + cmds

    def get_show_vlan_command(self): return "show vlan brief"
    def get_show_interface_command(self): return "show ip interface brief"
    def get_ping_command(self, target_ip): return f"ping {target_ip}"
    def get_show_route_command(self): return "show ip route"
    def get_save_config_command(self): return "write memory"
