"""MikroTik RouterOS CLI (CHR 7.17 라우터용)"""
from typing import List, Optional
from .base import VendorBase


class MikroTik(VendorBase):
    vendor_name = "MikroTik RouterOS"

    def generate_router_config(
        self, hostname, vlan_upper, vlan_lower,
        ip_upper, ip_lower, mask,
        iface_to_dist1, iface_to_dist2, loopback_ip,
    ) -> List[str]:
        prefix_len = sum(bin(int(x)).count("1") for x in mask.split("."))
        cmds = [
            f"/system identity set name={hostname}",
            "#",
            "# --- Physical Interface 활성화 ---",
            f"/interface ethernet set {iface_to_dist1} disabled=no",
            f"/interface ethernet set {iface_to_dist2} disabled=no",
            "#",
            "# --- VLAN 인터페이스 생성 ---",
            f"/interface vlan add interface={iface_to_dist1} name=vlan{vlan_upper} vlan-id={vlan_upper}",
            f"/interface vlan add interface={iface_to_dist2} name=vlan{vlan_lower} vlan-id={vlan_lower}",
            "#",
            "# --- IP 주소 할당 ---",
            f"/ip address add address={ip_upper}/{prefix_len} interface=vlan{vlan_upper}",
            f"/ip address add address={ip_lower}/{prefix_len} interface=vlan{vlan_lower}",
            f"/ip address add address={loopback_ip} interface=lo",
            "#",
            "# --- IP 라우팅 활성화 ---",
            "/ip settings set ip-forward=yes",
            "#",
            "# --- 방화벽 기본 정책 (ping 허용) ---",
            "/ip firewall filter add chain=input protocol=icmp action=accept",
            "/ip firewall filter add chain=forward protocol=icmp action=accept",
        ]
        return self.banner(hostname) + cmds

    def generate_switch_config(self, *args, **kwargs) -> List[str]:
        return []

    def get_show_vlan_command(self): return "/interface vlan print"
    def get_show_interface_command(self): return "/interface print"
    def get_ping_command(self, target_ip): return f"/ping {target_ip} count=4"
    def get_show_route_command(self): return "/ip route print"
    def get_save_config_command(self): return "/system backup save name=backup"
