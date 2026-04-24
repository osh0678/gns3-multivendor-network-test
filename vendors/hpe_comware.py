"""HPE Comware CLI (VSR1001 라우터용)"""
from typing import List, Optional
from .base import VendorBase


class HPEComware(VendorBase):
    vendor_name = "HPE Comware"

    def generate_router_config(
        self, hostname, vlan_upper, vlan_lower,
        ip_upper, ip_lower, mask,
        iface_to_dist1, iface_to_dist2, loopback_ip,
    ) -> List[str]:
        cmds = [
            "system-view",
            f"sysname {hostname}",
            "#",
            f"vlan {vlan_upper}",
            f" description VLAN{vlan_upper}-Upper",
            "#",
            f"vlan {vlan_lower}",
            f" description VLAN{vlan_lower}-Lower",
            "#",
            f"interface {iface_to_dist1}",
            " port link-type trunk",
            f" port trunk permit vlan {vlan_upper}",
            " undo shutdown",
            "#",
            f"interface {iface_to_dist2}",
            " port link-type trunk",
            f" port trunk permit vlan {vlan_lower}",
            " undo shutdown",
            "#",
            f"interface Vlan-interface{vlan_upper}",
            f" ip address {ip_upper} {mask}",
            "#",
            f"interface Vlan-interface{vlan_lower}",
            f" ip address {ip_lower} {mask}",
            "#",
            "interface LoopBack0",
            f" ip address {loopback_ip} 255.255.255.255",
            "#",
            "ip route-static 0.0.0.0 0 NULL0",
            "#",
            "save force",
        ]
        return self.banner(hostname) + cmds

    def generate_switch_config(self, *args, **kwargs) -> List[str]:
        return []

    def get_show_vlan_command(self): return "display vlan"
    def get_show_interface_command(self): return "display interface brief"
    def get_ping_command(self, target_ip): return f"ping {target_ip}"
    def get_show_route_command(self): return "display ip routing-table"
    def get_save_config_command(self): return "save force"
