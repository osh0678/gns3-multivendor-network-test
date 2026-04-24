"""6WIND Turbo Router CLI (fp-cli 기반, Linux-like set 명령 체계)"""
from typing import List, Optional
from .base import VendorBase


class SixWind(VendorBase):
    vendor_name = "6WIND"

    def generate_router_config(
        self, hostname, vlan_upper, vlan_lower,
        ip_upper, ip_lower, mask,
        iface_to_dist1, iface_to_dist2, loopback_ip,
    ) -> List[str]:
        prefix_len = sum(bin(int(x)).count("1") for x in mask.split("."))
        cmds = [
            "fp-cli",
            f"set system hostname {hostname}",
            "!",
            f"set interfaces physical {iface_to_dist1} enabled true",
            f"set interfaces vlan vlan{vlan_upper} physical-interface {iface_to_dist1}",
            f"set interfaces vlan vlan{vlan_upper} vlan-id {vlan_upper}",
            f"set interfaces vlan vlan{vlan_upper} ipv4 address {ip_upper}/{prefix_len}",
            f"set interfaces vlan vlan{vlan_upper} enabled true",
            "!",
            f"set interfaces physical {iface_to_dist2} enabled true",
            f"set interfaces vlan vlan{vlan_lower} physical-interface {iface_to_dist2}",
            f"set interfaces vlan vlan{vlan_lower} vlan-id {vlan_lower}",
            f"set interfaces vlan vlan{vlan_lower} ipv4 address {ip_lower}/{prefix_len}",
            f"set interfaces vlan vlan{vlan_lower} enabled true",
            "!",
            f"set interfaces loopback lo0 ipv4 address {loopback_ip}",
            "!",
            "set routing ipv4 enabled true",
            "commit",
        ]
        return self.banner(hostname) + cmds

    def generate_switch_config(self, *args, **kwargs) -> List[str]:
        return []  # 6WIND는 라우터 전용

    def get_show_vlan_command(self): return "fp-cli show interfaces vlan"
    def get_show_interface_command(self): return "fp-cli show interfaces"
    def get_ping_command(self, target_ip): return f"fp-cli ping {target_ip}"
    def get_show_route_command(self): return "fp-cli show routing ipv4"
    def get_save_config_command(self): return "fp-cli commit"
