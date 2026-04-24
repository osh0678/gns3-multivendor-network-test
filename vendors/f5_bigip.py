"""F5 BIG-IP LTM CLI (tmsh 기반)"""
from typing import List, Optional
from .base import VendorBase


class F5BigIP(VendorBase):
    vendor_name = "F5 BIG-IP"

    def generate_router_config(
        self, hostname, vlan_upper, vlan_lower,
        ip_upper, ip_lower, mask,
        iface_to_dist1, iface_to_dist2, loopback_ip,
    ) -> List[str]:
        prefix_len = sum(bin(int(x)).count("1") for x in mask.split("."))
        cmds = [
            "tmsh",
            f"modify sys global-settings hostname {hostname}",
            "#",
            "# --- VLAN 생성 ---",
            f"create net vlan vlan{vlan_upper} tag {vlan_upper} interfaces add {{ {iface_to_dist1} {{ tagged }} }}",
            f"create net vlan vlan{vlan_lower} tag {vlan_lower} interfaces add {{ {iface_to_dist2} {{ tagged }} }}",
            "#",
            "# --- Self IP 할당 ---",
            f"create net self self_vlan{vlan_upper} address {ip_upper}/{prefix_len} vlan vlan{vlan_upper} allow-service add {{ default }}",
            f"create net self self_vlan{vlan_lower} address {ip_lower}/{prefix_len} vlan vlan{vlan_lower} allow-service add {{ default }}",
            "#",
            "# --- 라우팅 설정 ---",
            "create net route default_route network default gw 0.0.0.0",
            "#",
            "# --- 설정 저장 ---",
            "save sys config",
            "quit",
        ]
        return self.banner(hostname) + cmds

    def generate_switch_config(self, *args, **kwargs) -> List[str]:
        return []

    def get_show_vlan_command(self): return "tmsh list net vlan"
    def get_show_interface_command(self): return "tmsh show net interface"
    def get_ping_command(self, target_ip): return f"ping -c 4 {target_ip}"
    def get_show_route_command(self): return "tmsh list net route"
    def get_save_config_command(self): return "tmsh save sys config"
