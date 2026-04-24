"""Cisco IOS CLI (Cisco 7200 라우터용)"""
from typing import List, Optional
from .base import VendorBase


class CiscoIOS(VendorBase):
    vendor_name = "Cisco IOS"

    def generate_router_config(
        self, hostname, vlan_upper, vlan_lower,
        ip_upper, ip_lower, mask,
        iface_to_dist1, iface_to_dist2, loopback_ip,
    ) -> List[str]:
        cmds = [
            "enable",
            "configure terminal",
            f"hostname {hostname}",
            "!",
            "ip routing",
            "!",
            f"interface Loopback0",
            f" ip address {loopback_ip} 255.255.255.255",
            " no shutdown",
            "!",
            f"interface {iface_to_dist1}",
            " no shutdown",
            "!",
            f"interface {iface_to_dist1}.{vlan_upper}",
            f" encapsulation dot1Q {vlan_upper}",
            f" ip address {ip_upper} {mask}",
            " no shutdown",
            "!",
            f"interface {iface_to_dist2}",
            " no shutdown",
            "!",
            f"interface {iface_to_dist2}.{vlan_lower}",
            f" encapsulation dot1Q {vlan_lower}",
            f" ip address {ip_lower} {mask}",
            " no shutdown",
            "!",
            "end",
            "write memory",
        ]
        return self.banner(hostname) + cmds

    def generate_switch_config(
        self, hostname, role, vlans, svi_vlan, svi_ip, svi_mask,
        trunk_iface, access_ifaces=None,
    ) -> List[str]:
        # Cisco 7200은 라우터이므로 스위치 설정은 cisco_iosxe에서 처리
        return []

    def get_show_vlan_command(self): return "show ip interface brief"
    def get_show_interface_command(self): return "show interfaces"
    def get_ping_command(self, target_ip): return f"ping {target_ip}"
    def get_show_route_command(self): return "show ip route"
    def get_save_config_command(self): return "write memory"
