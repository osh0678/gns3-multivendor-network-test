"""벤더 CLI 추상 베이스 클래스"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class VendorBase(ABC):
    """모든 벤더 CLI 모듈의 베이스 클래스"""

    vendor_name: str = "unknown"

    @abstractmethod
    def generate_router_config(
        self,
        hostname: str,
        vlan_upper: int,
        vlan_lower: int,
        ip_upper: str,
        ip_lower: str,
        mask: str,
        iface_to_dist1: str,
        iface_to_dist2: str,
        loopback_ip: str,
    ) -> List[str]:
        """라우터 설정 명령어 생성 (sub-interface, inter-VLAN routing)"""
        ...

    @abstractmethod
    def generate_switch_config(
        self,
        hostname: str,
        role: str,
        vlans: List[int],
        svi_vlan: int,
        svi_ip: str,
        svi_mask: str,
        trunk_iface: str,
        access_ifaces: Optional[List[str]] = None,
    ) -> List[str]:
        """스위치 설정 명령어 생성 (distribution / access)"""
        ...

    @abstractmethod
    def get_show_vlan_command(self) -> str:
        ...

    @abstractmethod
    def get_show_interface_command(self) -> str:
        ...

    @abstractmethod
    def get_ping_command(self, target_ip: str) -> str:
        ...

    @abstractmethod
    def get_show_route_command(self) -> str:
        ...

    @abstractmethod
    def get_save_config_command(self) -> str:
        ...

    def banner(self, hostname: str) -> List[str]:
        """공통 배너 (벤더별 오버라이드 가능)"""
        return [f"! === {self.vendor_name} - {hostname} ==="]
