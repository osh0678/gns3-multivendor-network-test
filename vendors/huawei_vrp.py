"""Huawei VRP CLI (NE40E 라우터 / CE12800 스위치용)"""
from typing import List, Optional
from .base import VendorBase


class HuaweiVRP(VendorBase):
    vendor_name = "Huawei VRP"

    def generate_router_config(
        self, hostname, vlan_upper, vlan_lower,
        ip_upper, ip_lower, mask,
        iface_to_dist1, iface_to_dist2, loopback_ip,
    ) -> List[str]:
        cmds = [
            "system-view",
            f"sysname {hostname}",
            "#",
            f"vlan batch {vlan_upper} {vlan_lower}",
            "#",
            f"interface {iface_to_dist1}",
            " undo shutdown",
            " port link-type trunk",
            f" port trunk allow-pass vlan {vlan_upper}",
            "#",
            f"interface {iface_to_dist2}",
            " undo shutdown",
            " port link-type trunk",
            f" port trunk allow-pass vlan {vlan_lower}",
            "#",
            f"interface Vlanif{vlan_upper}",
            f" ip address {ip_upper} {mask}",
            "#",
            f"interface Vlanif{vlan_lower}",
            f" ip address {ip_lower} {mask}",
            "#",
            "interface LoopBack0",
            f" ip address {loopback_ip} 255.255.255.255",
            "#",
            "return",
            "save",
            "y",
        ]
        return self.banner(hostname) + cmds

    def generate_switch_config(
        self, hostname, role, vlans, svi_vlan, svi_ip, svi_mask,
        trunk_iface, access_ifaces=None,
    ) -> List[str]:
        vlan_str = " ".join(str(v) for v in vlans)
        cmds = [
            "system-view",
            f"sysname {hostname}",
            "#",
            f"vlan batch {vlan_str}",
            "#",
            f"interface {trunk_iface}",
            " undo shutdown",
            " port link-type trunk",
            f" port trunk allow-pass vlan {vlan_str}",
            "#",
        ]

        if role == "distribution" and access_ifaces:
            for ai in access_ifaces:
                cmds += [
                    f"interface {ai}",
                    " undo shutdown",
                    " port link-type trunk",
                    f" port trunk allow-pass vlan {vlan_str}",
                    "#",
                ]

        cmds += [
            f"interface Vlanif{svi_vlan}",
            f" ip address {svi_ip} {svi_mask}",
            "#",
            "return",
            "save",
            "y",
        ]
        return self.banner(hostname) + cmds

    def get_show_vlan_command(self): return "display vlan"
    def get_show_interface_command(self): return "display interface brief"
    def get_ping_command(self, target_ip): return f"ping -c 4 {target_ip}"
    def get_show_route_command(self): return "display ip routing-table"
    def get_save_config_command(self): return "save"
