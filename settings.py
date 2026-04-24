r"""
GNS3 Multivendor Network Test - Global Settings
================================================
7개 벤더 Pod의 토폴로지, VLAN, IP 주소 설정을 정의합니다.

토폴로지 구조 (각 Pod 동일):
    Access-SW-3   Access-SW-4
         \           /
      Distribution-SW-1
              |
           Router
              |
      Distribution-SW-2
         /           \
    Access-SW-5   Access-SW-6
"""

# ──────────────────────────────────────────────
# GNS3 Server Settings
# ──────────────────────────────────────────────
GNS3_SERVER = "http://127.0.0.1:3080"
GNS3_PROJECT_NAME = "Multivendor-Network-Test"

# Telnet 기본 설정
TELNET_TIMEOUT = 10
TELNET_READ_DELAY = 2
CONSOLE_BASE_PORT = 5000  # GNS3 콘솔 포트 시작 번호

# ──────────────────────────────────────────────
# VLAN & IP Address Plan (모든 VLAN/IP 고유)
# ──────────────────────────────────────────────
# 각 Pod는 상위(Upper) / 하위(Lower) 두 개의 VLAN을 사용
# Pod별 서브넷: 10.{pod_id}.{vlan_id}.0/24

PODS = {
    "pod1": {
        "name": "6WIND Router & Arista Switch",
        "router_vendor": "sixwind",
        "switch_vendor": "arista_eos",
        "router_image": "6WINDTurboRouter-3.4.0",
        "switch_image": "AristaEOS-4.33.1F",
        "vlan_upper": 10,
        "vlan_lower": 20,
        "subnet_upper": "10.1.10.0/24",
        "subnet_lower": "10.1.20.0/24",
        "router_loopback": "10.1.0.1/32",
        "devices": {
            "router": {"hostname": "6WIND-TR-1", "type": "router"},
            "dist_sw1": {"hostname": "Arista-DSW-1", "type": "switch", "role": "distribution"},
            "dist_sw2": {"hostname": "Arista-DSW-2", "type": "switch", "role": "distribution"},
            "acc_sw1":  {"hostname": "Arista-ASW-3", "type": "switch", "role": "access"},
            "acc_sw2":  {"hostname": "Arista-ASW-4", "type": "switch", "role": "access"},
            "acc_sw3":  {"hostname": "Arista-ASW-5", "type": "switch", "role": "access"},
            "acc_sw4":  {"hostname": "Arista-ASW-6", "type": "switch", "role": "access"},
        },
    },
    "pod2": {
        "name": "Cisco Router & Switch",
        "router_vendor": "cisco_ios",
        "switch_vendor": "cisco_iosxe",
        "router_image": "Cisco-7200",
        "switch_image": "CiscoCATIOS-XE9kv",
        "vlan_upper": 30,
        "vlan_lower": 40,
        "subnet_upper": "10.2.30.0/24",
        "subnet_lower": "10.2.40.0/24",
        "router_loopback": "10.2.0.1/32",
        "devices": {
            "router": {"hostname": "Cisco7200-R1", "type": "router"},
            "dist_sw1": {"hostname": "Cisco-DSW-1", "type": "switch", "role": "distribution"},
            "dist_sw2": {"hostname": "Cisco-DSW-2", "type": "switch", "role": "distribution"},
            "acc_sw1":  {"hostname": "Cisco-ASW-3", "type": "switch", "role": "access"},
            "acc_sw2":  {"hostname": "Cisco-ASW-4", "type": "switch", "role": "access"},
            "acc_sw3":  {"hostname": "Cisco-ASW-5", "type": "switch", "role": "access"},
            "acc_sw4":  {"hostname": "Cisco-ASW-6", "type": "switch", "role": "access"},
        },
    },
    "pod3": {
        "name": "Fortinet Router & Cisco Switch",
        "router_vendor": "fortinet",
        "switch_vendor": "cisco_iosxe",
        "router_image": "FortiADC-7.0.0",
        "switch_image": "CiscoCATIOS-XE9kv",
        "vlan_upper": 50,
        "vlan_lower": 60,
        "subnet_upper": "10.3.50.0/24",
        "subnet_lower": "10.3.60.0/24",
        "router_loopback": "10.3.0.1/32",
        "devices": {
            "router": {"hostname": "FortiADC-R1", "type": "router"},
            "dist_sw1": {"hostname": "Cisco-DSW-13", "type": "switch", "role": "distribution"},
            "dist_sw2": {"hostname": "Cisco-DSW-14", "type": "switch", "role": "distribution"},
            "acc_sw1":  {"hostname": "Cisco-ASW-15", "type": "switch", "role": "access"},
            "acc_sw2":  {"hostname": "Cisco-ASW-16", "type": "switch", "role": "access"},
            "acc_sw3":  {"hostname": "Cisco-ASW-17", "type": "switch", "role": "access"},
            "acc_sw4":  {"hostname": "Cisco-ASW-18", "type": "switch", "role": "access"},
        },
    },
    "pod4": {
        "name": "HPE Router & HP Aruba CX Switch",
        "router_vendor": "hpe_comware",
        "switch_vendor": "aruba_cx",
        "router_image": "HPEVSR1001-7.1.049P1",
        "switch_image": "ArubaOS-CX",
        "vlan_upper": 70,
        "vlan_lower": 80,
        "subnet_upper": "10.4.70.0/24",
        "subnet_lower": "10.4.80.0/24",
        "router_loopback": "10.4.0.1/32",
        "devices": {
            "router": {"hostname": "HPE-VSR-R1", "type": "router"},
            "dist_sw1": {"hostname": "Aruba-DSW-1", "type": "switch", "role": "distribution"},
            "dist_sw2": {"hostname": "Aruba-DSW-2", "type": "switch", "role": "distribution"},
            "acc_sw1":  {"hostname": "Aruba-ASW-3", "type": "switch", "role": "access"},
            "acc_sw2":  {"hostname": "Aruba-ASW-4", "type": "switch", "role": "access"},
            "acc_sw3":  {"hostname": "Aruba-ASW-5", "type": "switch", "role": "access"},
            "acc_sw4":  {"hostname": "Aruba-ASW-6", "type": "switch", "role": "access"},
        },
    },
    "pod5": {
        "name": "MikroTik Router & Cisco Switch",
        "router_vendor": "mikrotik",
        "switch_vendor": "cisco_iosxe",
        "router_image": "MikroTikCHR-7.17",
        "switch_image": "CiscoCATIOS-XE9kv",
        "vlan_upper": 90,
        "vlan_lower": 100,
        "subnet_upper": "10.5.90.0/24",
        "subnet_lower": "10.5.100.0/24",
        "router_loopback": "10.5.0.1/32",
        "devices": {
            "router": {"hostname": "MikroTik-CHR-R1", "type": "router"},
            "dist_sw1": {"hostname": "Cisco-DSW-7", "type": "switch", "role": "distribution"},
            "dist_sw2": {"hostname": "Cisco-DSW-8", "type": "switch", "role": "distribution"},
            "acc_sw1":  {"hostname": "Cisco-ASW-9", "type": "switch", "role": "access"},
            "acc_sw2":  {"hostname": "Cisco-ASW-10", "type": "switch", "role": "access"},
            "acc_sw3":  {"hostname": "Cisco-ASW-11", "type": "switch", "role": "access"},
            "acc_sw4":  {"hostname": "Cisco-ASW-12", "type": "switch", "role": "access"},
        },
    },
    "pod6": {
        "name": "HuaWei Router & Switch",
        "router_vendor": "huawei_vrp",
        "switch_vendor": "huawei_vrp",
        "router_image": "HuaWeiNE40E",
        "switch_image": "HuaWeiCE12800",
        "vlan_upper": 110,
        "vlan_lower": 120,
        "subnet_upper": "10.6.110.0/24",
        "subnet_lower": "10.6.120.0/24",
        "router_loopback": "10.6.0.1/32",
        "devices": {
            "router": {"hostname": "HuaWei-NE40E-R1", "type": "router"},
            "dist_sw1": {"hostname": "HuaWei-DSW-1", "type": "switch", "role": "distribution"},
            "dist_sw2": {"hostname": "HuaWei-DSW-2", "type": "switch", "role": "distribution"},
            "acc_sw1":  {"hostname": "HuaWei-ASW-3", "type": "switch", "role": "access"},
            "acc_sw2":  {"hostname": "HuaWei-ASW-4", "type": "switch", "role": "access"},
            "acc_sw3":  {"hostname": "HuaWei-ASW-5", "type": "switch", "role": "access"},
            "acc_sw4":  {"hostname": "HuaWei-ASW-6", "type": "switch", "role": "access"},
        },
    },
    "pod7": {
        "name": "F5 Router & HuaWei Switch",
        "router_vendor": "f5_bigip",
        "switch_vendor": "huawei_vrp",
        "router_image": "F5BIG-IPTMVirt-17.5",
        "switch_image": "HuaWeiCE12800",
        "vlan_upper": 130,
        "vlan_lower": 140,
        "subnet_upper": "10.7.130.0/24",
        "subnet_lower": "10.7.140.0/24",
        "router_loopback": "10.7.0.1/32",
        "devices": {
            "router": {"hostname": "F5-BIGIP-R1", "type": "router"},
            "dist_sw1": {"hostname": "HuaWei-DSW-9", "type": "switch", "role": "distribution"},
            "dist_sw2": {"hostname": "HuaWei-DSW-10", "type": "switch", "role": "distribution"},
            "acc_sw1":  {"hostname": "HuaWei-ASW-7", "type": "switch", "role": "access"},
            "acc_sw2":  {"hostname": "HuaWei-ASW-8", "type": "switch", "role": "access"},
            "acc_sw3":  {"hostname": "HuaWei-ASW-11", "type": "switch", "role": "access"},
            "acc_sw4":  {"hostname": "HuaWei-ASW-12", "type": "switch", "role": "access"},
        },
    },
}


def get_ip(subnet: str, host_id: int) -> str:
    """서브넷에서 호스트 IP 생성. 예: get_ip('10.1.10.0/24', 1) -> '10.1.10.1'"""
    base = subnet.split("/")[0]
    octets = base.split(".")
    octets[3] = str(host_id)
    return ".".join(octets)


def get_subnet_mask(subnet: str) -> str:
    """CIDR -> 서브넷마스크 변환. 예: '/24' -> '255.255.255.0'"""
    prefix = int(subnet.split("/")[1])
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return f"{(mask >> 24) & 0xFF}.{(mask >> 16) & 0xFF}.{(mask >> 8) & 0xFF}.{mask & 0xFF}"


# ──────────────────────────────────────────────
# IP 할당 규칙 (각 서브넷 내)
# ──────────────────────────────────────────────
# .1  = Router (sub-interface / VLAN interface)
# .2  = Distribution Switch (SVI)
# .11 = Access Switch 1 (SVI)
# .12 = Access Switch 2 (SVI)

IP_ASSIGNMENTS = {
    "router": 1,
    "dist_sw": 2,
    "acc_sw1": 11,
    "acc_sw2": 12,
}

# ──────────────────────────────────────────────
# 인터페이스 매핑 (GNS3 이미지별 기본 인터페이스)
# ──────────────────────────────────────────────
INTERFACE_MAP = {
    "sixwind":    {"wan": "eth0", "lan1": "eth1", "lan2": "eth2"},
    "arista_eos": {"uplink": "Ethernet1", "downlink1": "Ethernet2", "downlink2": "Ethernet3"},
    "cisco_ios":  {"wan": "GigabitEthernet0/0", "lan1": "GigabitEthernet0/1", "lan2": "GigabitEthernet0/2"},
    "cisco_iosxe": {"uplink": "GigabitEthernet1/0/1", "downlink1": "GigabitEthernet1/0/2", "downlink2": "GigabitEthernet1/0/3"},
    "fortinet":   {"wan": "port1", "lan1": "port2", "lan2": "port3"},
    "hpe_comware": {"wan": "GigabitEthernet1/0", "lan1": "GigabitEthernet1/1", "lan2": "GigabitEthernet1/2"},
    "aruba_cx":   {"uplink": "1/1/1", "downlink1": "1/1/2", "downlink2": "1/1/3"},
    "mikrotik":   {"wan": "ether1", "lan1": "ether2", "lan2": "ether3"},
    "huawei_vrp": {"wan": "GigabitEthernet0/0/0", "lan1": "GigabitEthernet0/0/1", "lan2": "GigabitEthernet0/0/2",
                   "uplink": "GigabitEthernet0/0/1", "downlink1": "GigabitEthernet0/0/2", "downlink2": "GigabitEthernet0/0/3"},
    "f5_bigip":   {"wan": "1.1", "lan1": "1.2", "lan2": "1.3"},
}
