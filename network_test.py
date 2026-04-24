#!/usr/bin/env python3
"""
GNS3 Multivendor Network Tester
================================
각 Pod 내 장비 간 VLAN 연결 및 Ping 테스트를 수행합니다.

사용법:
    # 전체 테스트
    python network_test.py --all

    # 특정 Pod만 테스트
    python network_test.py --pod pod2

    # 상세 출력
    python network_test.py --all --verbose
"""
import json
import sys
import time
import telnetlib
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from settings import PODS, IP_ASSIGNMENTS, get_ip, INTERFACE_MAP
from vendors import VENDOR_MAP


# ──────────────────────────────────────────────
# 테스트 결과 구조
# ──────────────────────────────────────────────
class TestResult:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()

    def add(self, pod: str, source: str, target: str, target_ip: str,
            success: bool, detail: str = ""):
        self.results.append({
            "pod": pod, "source": source, "target": target,
            "target_ip": target_ip, "success": success, "detail": detail,
        })

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        elapsed = (datetime.now() - self.start_time).total_seconds()

        print(f"\n{'='*70}")
        print(f"  테스트 결과 요약")
        print(f"{'='*70}")
        print(f"  총 테스트: {total}  |  성공: {passed}  |  실패: {failed}")
        print(f"  소요 시간: {elapsed:.1f}초")
        print(f"{'='*70}")

        if failed > 0:
            print(f"\n  [실패 항목]")
            for r in self.results:
                if not r["success"]:
                    print(f"    ✗ [{r['pod']}] {r['source']} → {r['target']} "
                          f"({r['target_ip']}) : {r['detail']}")
        print()
        return failed == 0

    def save_report(self, filepath="test_report.json"):
        report = {
            "timestamp": self.start_time.isoformat(),
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r["success"]),
            "failed": sum(1 for r in self.results if not r["success"]),
            "details": self.results,
        }
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[OK] 테스트 리포트 저장: {filepath}")


# ──────────────────────────────────────────────
# 텔넷 기반 명령 실행
# ──────────────────────────────────────────────
def telnet_command(server: str, port: int, command: str, timeout: int = 10) -> str:
    """텔넷으로 장비에 명령어 하나를 실행하고 결과를 반환"""
    try:
        tn = telnetlib.Telnet(server, port, timeout=timeout)
        time.sleep(1)
        tn.write(b"\r\n")
        time.sleep(1)
        tn.read_very_eager()

        tn.write(command.encode("utf-8") + b"\r\n")
        time.sleep(3)
        output = tn.read_very_eager().decode("utf-8", errors="ignore")
        tn.close()
        return output
    except Exception as e:
        return f"[ERROR] {e}"


def check_ping_result(output: str) -> bool:
    """Ping 결과 파싱 (벤더 무관 공통 패턴)"""
    # 성공 패턴들
    success_patterns = [
        r"(\d+)\s+packets?\s+received",       # Linux/일반
        r"Success rate is (\d+) percent",      # Cisco IOS
        r"(\d+) received",                      # MikroTik
        r"Reply from",                          # Huawei/일반
        r"(\d+) packets received",             # Arista/HPE
        r"bytes from",                          # ping 응답
    ]
    for pattern in success_patterns:
        match = re.search(pattern, output)
        if match:
            groups = match.groups()
            if groups:
                val = int(groups[0])
                return val > 0 if val <= 100 else True
            return True

    # 실패 패턴
    fail_patterns = [
        r"0 received", r"0 packets received",
        r"100% packet loss", r"Success rate is 0",
        r"Request timed out", r"Destination unreachable",
    ]
    for pattern in fail_patterns:
        if re.search(pattern, output):
            return False

    return False


# ──────────────────────────────────────────────
# Pod별 테스트 시나리오 생성
# ──────────────────────────────────────────────
def generate_test_plan(pod_key: str) -> List[Tuple[str, str, str]]:
    """
    Pod 내 ping 테스트 매트릭스 생성
    Returns: [(source_dev_key, target_dev_key, target_ip), ...]
    """
    pod = PODS[pod_key]
    subnet_u = pod["subnet_upper"]
    subnet_l = pod["subnet_lower"]

    tests = []

    # Router → 모든 Distribution/Access 스위치
    for target, host_id, subnet in [
        ("dist_sw1", IP_ASSIGNMENTS["dist_sw"], subnet_u),
        ("dist_sw2", IP_ASSIGNMENTS["dist_sw"], subnet_l),
        ("acc_sw1",  IP_ASSIGNMENTS["acc_sw1"], subnet_u),
        ("acc_sw2",  IP_ASSIGNMENTS["acc_sw2"], subnet_u),
        ("acc_sw3",  IP_ASSIGNMENTS["acc_sw1"], subnet_l),
        ("acc_sw4",  IP_ASSIGNMENTS["acc_sw2"], subnet_l),
    ]:
        tests.append(("router", target, get_ip(subnet, host_id)))

    # Distribution Switch 1 → Router, Access Switches
    tests.append(("dist_sw1", "router", get_ip(subnet_u, IP_ASSIGNMENTS["router"])))
    tests.append(("dist_sw1", "acc_sw1", get_ip(subnet_u, IP_ASSIGNMENTS["acc_sw1"])))
    tests.append(("dist_sw1", "acc_sw2", get_ip(subnet_u, IP_ASSIGNMENTS["acc_sw2"])))

    # Distribution Switch 2 → Router, Access Switches
    tests.append(("dist_sw2", "router", get_ip(subnet_l, IP_ASSIGNMENTS["router"])))
    tests.append(("dist_sw2", "acc_sw3", get_ip(subnet_l, IP_ASSIGNMENTS["acc_sw1"])))
    tests.append(("dist_sw2", "acc_sw4", get_ip(subnet_l, IP_ASSIGNMENTS["acc_sw2"])))

    # Cross-VLAN: Access Upper → Access Lower (Router를 통해)
    tests.append(("acc_sw1", "acc_sw3", get_ip(subnet_l, IP_ASSIGNMENTS["acc_sw1"])))

    return tests


# ──────────────────────────────────────────────
# 메인 테스트 루프
# ──────────────────────────────────────────────
def run_pod_tests(pod_key: str, console_map: dict, result: TestResult,
                  server: str, verbose: bool):
    """단일 Pod에 대해 테스트 수행"""
    pod = PODS[pod_key]
    router_vendor_key = pod["router_vendor"]
    switch_vendor_key = pod["switch_vendor"]

    print(f"\n{'─'*60}")
    print(f"  [{pod_key}] {pod['name']} 테스트")
    print(f"{'─'*60}")

    test_plan = generate_test_plan(pod_key)

    for src_key, tgt_key, tgt_ip in test_plan:
        map_key = f"{pod_key}/{src_key}"
        if map_key not in console_map:
            result.add(pod_key, src_key, tgt_key, tgt_ip, False, "콘솔 포트 없음")
            continue

        port = console_map[map_key]["console_port"]
        src_dev = pod["devices"][src_key]

        # 벤더별 ping 명령어
        if src_dev["type"] == "router":
            vendor = VENDOR_MAP[router_vendor_key]()
        else:
            vendor = VENDOR_MAP[switch_vendor_key]()

        ping_cmd = vendor.get_ping_command(tgt_ip)
        output = telnet_command(server, port, ping_cmd)
        success = check_ping_result(output)

        status = "✓" if success else "✗"
        src_name = src_dev["hostname"]
        tgt_name = pod["devices"][tgt_key]["hostname"]
        print(f"  {status} {src_name} → {tgt_name} ({tgt_ip})")

        if verbose and not success:
            print(f"    CMD: {ping_cmd}")
            print(f"    OUT: {output[:200]}")

        result.add(pod_key, src_name, tgt_name, tgt_ip, success,
                   output[:200] if not success else "")


def run_vendor_show_commands(pod_key: str, console_map: dict, server: str):
    """벤더별 show 명령어 실행 (VLAN, Interface, Route 확인)"""
    pod = PODS[pod_key]

    print(f"\n{'─'*60}")
    print(f"  [{pod_key}] Show 명령어 검증")
    print(f"{'─'*60}")

    for dev_key, dev_info in pod["devices"].items():
        map_key = f"{pod_key}/{dev_key}"
        if map_key not in console_map:
            continue

        port = console_map[map_key]["console_port"]
        if dev_info["type"] == "router":
            vendor = VENDOR_MAP[pod["router_vendor"]]()
        else:
            vendor = VENDOR_MAP[pod["switch_vendor"]]()

        print(f"\n  [{dev_info['hostname']}]")

        for cmd_name, cmd in [
            ("VLAN", vendor.get_show_vlan_command()),
            ("Interface", vendor.get_show_interface_command()),
            ("Route", vendor.get_show_route_command()),
        ]:
            output = telnet_command(server, port, cmd)
            lines = output.strip().split("\n")
            preview = "\n    ".join(lines[:5])
            print(f"    {cmd_name}: {cmd}")
            print(f"    {preview}")
            if len(lines) > 5:
                print(f"    ... ({len(lines) - 5} more lines)")


def main():
    parser = argparse.ArgumentParser(description="GNS3 Multivendor Network Tester")
    parser.add_argument("--all", action="store_true", help="모든 Pod 테스트")
    parser.add_argument("--pod", type=str, help="특정 Pod만 테스트")
    parser.add_argument("--verbose", action="store_true", help="상세 출력")
    parser.add_argument("--show", action="store_true", help="show 명령어도 실행")
    parser.add_argument("--server", default="127.0.0.1", help="GNS3 서버 IP")
    parser.add_argument("--report", default="test_report.json", help="리포트 파일명")
    args = parser.parse_args()

    target_pods = list(PODS.keys()) if args.all else ([args.pod] if args.pod else [])
    if not target_pods:
        print("사용법: python network_test.py --all 또는 --pod pod2")
        sys.exit(1)

    try:
        with open("console_ports.json") as f:
            console_map = json.load(f)
    except FileNotFoundError:
        print("[ERROR] console_ports.json 없음. topology.py를 먼저 실행하세요.")
        sys.exit(1)

    result = TestResult()

    for pod_key in target_pods:
        if pod_key not in PODS:
            print(f"[ERROR] 존재하지 않는 Pod: {pod_key}")
            continue
        run_pod_tests(pod_key, console_map, result, args.server, args.verbose)
        if args.show:
            run_vendor_show_commands(pod_key, console_map, args.server)

    all_passed = result.summary()
    result.save_report(args.report)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
