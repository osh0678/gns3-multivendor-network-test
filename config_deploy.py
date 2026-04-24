#!/usr/bin/env python3
"""
GNS3 Multivendor Config Deployer
=================================
GNS3 콘솔 포트(Telnet)를 통해 벤더별 설정을 자동 배포합니다.

사용법:
    # 전체 Pod 배포
    python config_deploy.py --all

    # 특정 Pod만 배포
    python config_deploy.py --pod pod2

    # 설정 파일만 생성 (배포 없이)
    python config_deploy.py --generate-only

    # 콘솔 포트 수동 지정
    python config_deploy.py --pod pod2 --base-port 5000
"""
import os
import sys
import json
import time
import telnetlib
import argparse
from pathlib import Path

from settings import (
    PODS, GNS3_SERVER, TELNET_TIMEOUT, TELNET_READ_DELAY,
    IP_ASSIGNMENTS, INTERFACE_MAP, get_ip, get_subnet_mask,
)
from vendors import VENDOR_MAP


def generate_pod_configs(pod_key: str) -> dict:
    """Pod의 모든 장비 설정을 생성하여 반환"""
    pod = PODS[pod_key]
    router_vendor_key = pod["router_vendor"]
    switch_vendor_key = pod["switch_vendor"]

    router_cls = VENDOR_MAP[router_vendor_key]()
    switch_cls = VENDOR_MAP[switch_vendor_key]()

    configs = {}
    devices = pod["devices"]

    vlan_u = pod["vlan_upper"]
    vlan_l = pod["vlan_lower"]
    subnet_u = pod["subnet_upper"]
    subnet_l = pod["subnet_lower"]
    mask_u = get_subnet_mask(subnet_u)
    mask_l = get_subnet_mask(subnet_l)

    r_iface = INTERFACE_MAP[router_vendor_key]
    s_iface = INTERFACE_MAP[switch_vendor_key]

    # ── Router ──
    router_dev = devices["router"]
    configs["router"] = {
        "hostname": router_dev["hostname"],
        "commands": router_cls.generate_router_config(
            hostname=router_dev["hostname"],
            vlan_upper=vlan_u,
            vlan_lower=vlan_l,
            ip_upper=get_ip(subnet_u, IP_ASSIGNMENTS["router"]),
            ip_lower=get_ip(subnet_l, IP_ASSIGNMENTS["router"]),
            mask=mask_u,  # /24 동일
            iface_to_dist1=r_iface.get("lan1", r_iface.get("wan", "eth0")),
            iface_to_dist2=r_iface.get("lan2", r_iface.get("wan", "eth1")),
            loopback_ip=pod["router_loopback"].split("/")[0],
        ),
    }

    # ── Distribution Switch 1 (Upper VLAN) ──
    dist1_dev = devices["dist_sw1"]
    configs["dist_sw1"] = {
        "hostname": dist1_dev["hostname"],
        "commands": switch_cls.generate_switch_config(
            hostname=dist1_dev["hostname"],
            role="distribution",
            vlans=[vlan_u, vlan_l],
            svi_vlan=vlan_u,
            svi_ip=get_ip(subnet_u, IP_ASSIGNMENTS["dist_sw"]),
            svi_mask=mask_u,
            trunk_iface=s_iface.get("uplink", s_iface.get("wan", "eth0")),
            access_ifaces=[
                s_iface.get("downlink1", "eth1"),
                s_iface.get("downlink2", "eth2"),
            ],
        ),
    }

    # ── Distribution Switch 2 (Lower VLAN) ──
    dist2_dev = devices["dist_sw2"]
    configs["dist_sw2"] = {
        "hostname": dist2_dev["hostname"],
        "commands": switch_cls.generate_switch_config(
            hostname=dist2_dev["hostname"],
            role="distribution",
            vlans=[vlan_u, vlan_l],
            svi_vlan=vlan_l,
            svi_ip=get_ip(subnet_l, IP_ASSIGNMENTS["dist_sw"]),
            svi_mask=mask_l,
            trunk_iface=s_iface.get("uplink", s_iface.get("wan", "eth0")),
            access_ifaces=[
                s_iface.get("downlink1", "eth1"),
                s_iface.get("downlink2", "eth2"),
            ],
        ),
    }

    # ── Access Switches (Upper: acc_sw1, acc_sw2) ──
    for idx, acc_key in enumerate(["acc_sw1", "acc_sw2"], start=1):
        acc_dev = devices[acc_key]
        configs[acc_key] = {
            "hostname": acc_dev["hostname"],
            "commands": switch_cls.generate_switch_config(
                hostname=acc_dev["hostname"],
                role="access",
                vlans=[vlan_u, vlan_l],
                svi_vlan=vlan_u,
                svi_ip=get_ip(subnet_u, IP_ASSIGNMENTS[f"acc_sw{idx}"]),
                svi_mask=mask_u,
                trunk_iface=s_iface.get("uplink", s_iface.get("wan", "eth0")),
            ),
        }

    # ── Access Switches (Lower: acc_sw3, acc_sw4) ──
    for idx, acc_key in enumerate(["acc_sw3", "acc_sw4"], start=1):
        acc_dev = devices[acc_key]
        configs[acc_key] = {
            "hostname": acc_dev["hostname"],
            "commands": switch_cls.generate_switch_config(
                hostname=acc_dev["hostname"],
                role="access",
                vlans=[vlan_u, vlan_l],
                svi_vlan=vlan_l,
                svi_ip=get_ip(subnet_l, IP_ASSIGNMENTS[f"acc_sw{idx}"]),
                svi_mask=mask_l,
                trunk_iface=s_iface.get("uplink", s_iface.get("wan", "eth0")),
            ),
        }

    return configs


def save_configs(pod_key: str, configs: dict):
    """설정 파일을 configs/ 디렉토리에 저장"""
    pod = PODS[pod_key]
    folder_map = {
        "pod1": "pod1_6wind_arista",
        "pod2": "pod2_cisco",
        "pod3": "pod3_fortinet_cisco",
        "pod4": "pod4_hpe_aruba",
        "pod5": "pod5_mikrotik_cisco",
        "pod6": "pod6_huawei",
        "pod7": "pod7_f5_huawei",
    }
    config_dir = Path("configs") / folder_map.get(pod_key, pod_key)
    config_dir.mkdir(parents=True, exist_ok=True)

    for dev_key, cfg in configs.items():
        filename = config_dir / f"{cfg['hostname']}.cfg"
        with open(filename, "w") as f:
            f.write(f"! Pod: {pod['name']}\n")
            f.write(f"! Device: {cfg['hostname']} ({dev_key})\n")
            f.write(f"! Generated by GNS3 Multivendor Network Test\n")
            f.write("!" + "=" * 50 + "\n\n")
            for cmd in cfg["commands"]:
                f.write(cmd + "\n")
        print(f"  [FILE] {filename}")


def deploy_via_telnet(hostname: str, console_port: int, commands: list,
                      server: str = "127.0.0.1"):
    """텔넷으로 장비에 접속하여 명령어 실행"""
    print(f"\n[DEPLOY] {hostname} (telnet {server}:{console_port})")
    try:
        tn = telnetlib.Telnet(server, console_port, timeout=TELNET_TIMEOUT)
        time.sleep(1)

        # 프롬프트 대기 (Enter 키로 깨움)
        tn.write(b"\r\n")
        time.sleep(TELNET_READ_DELAY)
        output = tn.read_very_eager().decode("utf-8", errors="ignore")
        print(f"  [PROMPT] {output[-100:].strip()}")

        for cmd in commands:
            if cmd.startswith("!") or cmd.startswith("#"):
                continue  # 주석 건너뜀
            tn.write(cmd.encode("utf-8") + b"\r\n")
            time.sleep(0.5)

        time.sleep(TELNET_READ_DELAY)
        final_output = tn.read_very_eager().decode("utf-8", errors="ignore")
        tn.close()
        print(f"  [OK] {hostname} 설정 배포 완료")
        return True

    except Exception as e:
        print(f"  [FAIL] {hostname}: {e}")
        return False


def load_console_ports() -> dict:
    """console_ports.json에서 포트 정보 로드"""
    try:
        with open("console_ports.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[WARN] console_ports.json 없음. topology.py를 먼저 실행하세요.")
        return {}


def main():
    parser = argparse.ArgumentParser(description="GNS3 Multivendor Config Deployer")
    parser.add_argument("--all", action="store_true", help="모든 Pod 배포")
    parser.add_argument("--pod", type=str, help="특정 Pod만 배포 (예: pod2)")
    parser.add_argument("--generate-only", action="store_true", help="설정 파일만 생성")
    parser.add_argument("--server", default="127.0.0.1", help="GNS3 서버 IP")
    args = parser.parse_args()

    target_pods = list(PODS.keys()) if args.all else ([args.pod] if args.pod else [])

    if not target_pods:
        print("사용법: python config_deploy.py --all 또는 --pod pod2")
        print("가능한 Pod:", ", ".join(PODS.keys()))
        sys.exit(1)

    console_map = {} if args.generate_only else load_console_ports()

    for pod_key in target_pods:
        if pod_key not in PODS:
            print(f"[ERROR] 존재하지 않는 Pod: {pod_key}")
            continue

        print(f"\n{'='*60}")
        print(f"[POD] {PODS[pod_key]['name']} ({pod_key})")
        print(f"{'='*60}")

        configs = generate_pod_configs(pod_key)
        save_configs(pod_key, configs)

        if not args.generate_only:
            for dev_key, cfg in configs.items():
                map_key = f"{pod_key}/{dev_key}"
                if map_key in console_map:
                    port = console_map[map_key]["console_port"]
                    deploy_via_telnet(
                        cfg["hostname"], port, cfg["commands"],
                        server=args.server,
                    )
                else:
                    print(f"  [SKIP] {cfg['hostname']}: 콘솔 포트 정보 없음")

    print(f"\n{'='*60}")
    print("[DONE] 설정 배포 완료!")


if __name__ == "__main__":
    main()
