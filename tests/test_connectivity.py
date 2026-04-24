#!/usr/bin/env python3
"""
pytest 기반 네트워크 연결 테스트
================================
사용법: pytest tests/test_connectivity.py -v
"""
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import PODS, IP_ASSIGNMENTS, get_ip
from vendors import VENDOR_MAP


class TestIPUniqueness:
    """모든 Pod의 IP 주소가 고유한지 검증"""

    def test_all_ips_unique(self):
        all_ips = []
        for pod_key, pod in PODS.items():
            for subnet_key in ["subnet_upper", "subnet_lower"]:
                subnet = pod[subnet_key]
                for role, host_id in IP_ASSIGNMENTS.items():
                    ip = get_ip(subnet, host_id)
                    assert ip not in all_ips, (
                        f"IP 중복: {ip} in {pod_key} ({subnet_key})"
                    )
                    all_ips.append(ip)

    def test_all_vlans_unique(self):
        vlans = []
        for pod_key, pod in PODS.items():
            for vlan_key in ["vlan_upper", "vlan_lower"]:
                vlan = pod[vlan_key]
                assert vlan not in vlans, (
                    f"VLAN 중복: {vlan} in {pod_key}"
                )
                vlans.append(vlan)


class TestVendorModules:
    """벤더 모듈이 정상 작동하는지 검증"""

    @pytest.mark.parametrize("vendor_key", VENDOR_MAP.keys())
    def test_vendor_has_all_methods(self, vendor_key):
        vendor = VENDOR_MAP[vendor_key]()
        assert hasattr(vendor, "generate_router_config")
        assert hasattr(vendor, "generate_switch_config")
        assert hasattr(vendor, "get_show_vlan_command")
        assert hasattr(vendor, "get_ping_command")
        assert hasattr(vendor, "get_show_route_command")
        assert hasattr(vendor, "get_save_config_command")

    @pytest.mark.parametrize("vendor_key", VENDOR_MAP.keys())
    def test_ping_command_format(self, vendor_key):
        vendor = VENDOR_MAP[vendor_key]()
        cmd = vendor.get_ping_command("10.1.10.1")
        assert "10.1.10.1" in cmd
        assert isinstance(cmd, str)


class TestConfigGeneration:
    """설정 파일이 정상 생성되는지 검증"""

    @pytest.mark.parametrize("pod_key", PODS.keys())
    def test_router_config_not_empty(self, pod_key):
        pod = PODS[pod_key]
        vendor = VENDOR_MAP[pod["router_vendor"]]()
        subnet_u = pod["subnet_upper"]
        subnet_l = pod["subnet_lower"]

        config = vendor.generate_router_config(
            hostname="TEST-ROUTER",
            vlan_upper=pod["vlan_upper"],
            vlan_lower=pod["vlan_lower"],
            ip_upper=get_ip(subnet_u, 1),
            ip_lower=get_ip(subnet_l, 1),
            mask="255.255.255.0",
            iface_to_dist1="eth0",
            iface_to_dist2="eth1",
            loopback_ip="10.0.0.1",
        )
        assert len(config) > 0, f"Router config empty for {pod_key}"

    @pytest.mark.parametrize("pod_key", PODS.keys())
    def test_switch_config_not_empty(self, pod_key):
        pod = PODS[pod_key]
        vendor = VENDOR_MAP[pod["switch_vendor"]]()

        config = vendor.generate_switch_config(
            hostname="TEST-SWITCH",
            role="distribution",
            vlans=[pod["vlan_upper"], pod["vlan_lower"]],
            svi_vlan=pod["vlan_upper"],
            svi_ip=get_ip(pod["subnet_upper"], 2),
            svi_mask="255.255.255.0",
            trunk_iface="eth0",
            access_ifaces=["eth1", "eth2"],
        )
        assert len(config) > 0, f"Switch config empty for {pod_key}"


class TestPodTopology:
    """Pod 토폴로지 설정이 정상인지 검증"""

    @pytest.mark.parametrize("pod_key", PODS.keys())
    def test_pod_has_all_devices(self, pod_key):
        pod = PODS[pod_key]
        required = ["router", "dist_sw1", "dist_sw2",
                     "acc_sw1", "acc_sw2", "acc_sw3", "acc_sw4"]
        for dev in required:
            assert dev in pod["devices"], f"{pod_key}: {dev} 누락"

    @pytest.mark.parametrize("pod_key", PODS.keys())
    def test_pod_has_two_vlans(self, pod_key):
        pod = PODS[pod_key]
        assert pod["vlan_upper"] != pod["vlan_lower"]
        assert pod["subnet_upper"] != pod["subnet_lower"]
