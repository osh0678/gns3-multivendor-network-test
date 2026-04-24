#!/usr/bin/env python3
"""
GNS3 Multivendor Network Topology Builder
==========================================
GNS3 REST API를 사용하여 7개 벤더 Pod 토폴로지를 자동 생성합니다.

사용법:
    python topology.py [--server http://127.0.0.1:3080]
"""
import json
import sys
import argparse
import urllib.request
import urllib.error
from settings import PODS, GNS3_SERVER, GNS3_PROJECT_NAME


class GNS3API:
    """GNS3 REST API 클라이언트"""

    def __init__(self, server_url: str):
        self.base = server_url.rstrip("/")

    def _request(self, method: str, path: str, data=None):
        url = f"{self.base}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            print(f"[ERROR] {method} {url} -> {e.code}: {e.read().decode()}")
            raise

    def get(self, path):    return self._request("GET", path)
    def post(self, path, data=None): return self._request("POST", path, data)
    def put(self, path, data=None):  return self._request("PUT", path, data)

    # ── Project ──
    def create_project(self, name: str) -> dict:
        projects = self.get("/v2/projects")
        for p in projects:
            if p["name"] == name:
                print(f"[INFO] 기존 프로젝트 발견: {name} ({p['project_id']})")
                return p
        proj = self.post("/v2/projects", {"name": name})
        print(f"[OK] 프로젝트 생성: {name} ({proj['project_id']})")
        return proj

    def open_project(self, project_id: str):
        self.post(f"/v2/projects/{project_id}/open")

    # ── Templates ──
    def list_templates(self) -> list:
        return self.get("/v2/templates")

    def find_template(self, keyword: str) -> dict | None:
        templates = self.list_templates()
        for t in templates:
            if keyword.lower() in t["name"].lower():
                return t
        return None

    # ── Nodes ──
    def create_node(self, project_id, template_id, name, x=0, y=0) -> dict:
        data = {"name": name, "x": x, "y": y}
        node = self.post(
            f"/v2/projects/{project_id}/templates/{template_id}", data
        )
        print(f"  [+] 노드: {name} (console:{node.get('console', 'N/A')})")
        return node

    # ── Links ──
    def create_link(self, project_id, node1_id, adapter1, port1,
                    node2_id, adapter2, port2) -> dict:
        data = {
            "nodes": [
                {"node_id": node1_id, "adapter_number": adapter1, "port_number": port1},
                {"node_id": node2_id, "adapter_number": adapter2, "port_number": port2},
            ]
        }
        return self.post(f"/v2/projects/{project_id}/links", data)

    # ── Start ──
    def start_all(self, project_id):
        self.post(f"/v2/projects/{project_id}/nodes/start")
        print("[OK] 모든 노드 시작됨")


# ──────────────────────────────────────────────
# 토폴로지 좌표 계산
# ──────────────────────────────────────────────
POD_LAYOUT = {
    # pod_key: (base_x, base_y) — Pod 시작 좌표
    "pod1": (400, -200),   # 6WIND & Arista (상단 중앙)
    "pod2": (-300, 100),   # Cisco (중단 좌)
    "pod3": (700, 100),    # Fortinet & Cisco (중단 우)
    "pod4": (-300, 450),   # HPE & Aruba (하단 좌)
    "pod5": (700, 450),    # MikroTik & Cisco (하단 우)
    "pod6": (50, 750),     # HuaWei (최하단 좌)
    "pod7": (600, 750),    # F5 & HuaWei (최하단 우)
}

# 각 Pod 내 상대 좌표 (라우터 중심)
DEVICE_OFFSETS = {
    "router":   (0, 0),
    "dist_sw1": (0, -100),
    "dist_sw2": (0, 100),
    "acc_sw1":  (-100, -200),
    "acc_sw2":  (100, -200),
    "acc_sw3":  (-100, 200),
    "acc_sw4":  (100, 200),
}


def build_topology(server_url: str):
    """전체 토폴로지 생성"""
    api = GNS3API(server_url)

    # 1) 프로젝트 생성/열기
    project = api.create_project(GNS3_PROJECT_NAME)
    pid = project["project_id"]
    api.open_project(pid)

    # 2) 사용 가능한 템플릿 조회
    templates = api.list_templates()
    print(f"\n[INFO] 사용 가능한 GNS3 템플릿: {len(templates)}개")
    for t in templates:
        print(f"  - {t['name']} ({t['template_type']})")

    # 3) 각 Pod에 대해 노드 생성
    all_nodes = {}
    for pod_key, pod_cfg in PODS.items():
        print(f"\n{'='*50}")
        print(f"[POD] {pod_cfg['name']}")
        print(f"{'='*50}")

        base_x, base_y = POD_LAYOUT.get(pod_key, (0, 0))
        pod_nodes = {}

        for dev_key, dev_info in pod_cfg["devices"].items():
            # 이미지 결정
            if dev_info["type"] == "router":
                image_key = pod_cfg["router_image"]
            else:
                image_key = pod_cfg["switch_image"]

            template = api.find_template(image_key)
            if not template:
                print(f"  [WARN] 템플릿 없음: {image_key} — 이미지를 GNS3에 등록하세요.")
                print(f"         건너뜀: {dev_info['hostname']}")
                continue

            ox, oy = DEVICE_OFFSETS[dev_key]
            node = api.create_node(
                pid, template["template_id"],
                dev_info["hostname"],
                x=base_x + ox, y=base_y + oy,
            )
            pod_nodes[dev_key] = node

        # 4) 링크 생성 (Router ↔ Dist ↔ Access)
        link_pairs = [
            # (from, adapter, port) -> (to, adapter, port)
            ("router", 1, 0, "dist_sw1", 0, 0),   # Router lan1 ↔ Dist1 uplink
            ("router", 2, 0, "dist_sw2", 0, 0),   # Router lan2 ↔ Dist2 uplink
            ("dist_sw1", 1, 0, "acc_sw1", 0, 0),   # Dist1 downlink1 ↔ Acc1
            ("dist_sw1", 2, 0, "acc_sw2", 0, 0),   # Dist1 downlink2 ↔ Acc2
            ("dist_sw2", 1, 0, "acc_sw3", 0, 0),   # Dist2 downlink1 ↔ Acc3
            ("dist_sw2", 2, 0, "acc_sw4", 0, 0),   # Dist2 downlink2 ↔ Acc4
        ]
        for from_key, a1, p1, to_key, a2, p2 in link_pairs:
            if from_key in pod_nodes and to_key in pod_nodes:
                try:
                    api.create_link(
                        pid,
                        pod_nodes[from_key]["node_id"], a1, p1,
                        pod_nodes[to_key]["node_id"], a2, p2,
                    )
                    f_name = pod_cfg["devices"][from_key]["hostname"]
                    t_name = pod_cfg["devices"][to_key]["hostname"]
                    print(f"  [LINK] {f_name} ↔ {t_name}")
                except Exception as e:
                    print(f"  [WARN] 링크 실패: {from_key} ↔ {to_key} — {e}")

        all_nodes[pod_key] = pod_nodes

    # 5) 콘솔 포트 매핑 저장
    console_map = {}
    for pod_key, pod_nodes in all_nodes.items():
        for dev_key, node in pod_nodes.items():
            console_map[f"{pod_key}/{dev_key}"] = {
                "hostname": node["name"],
                "console_port": node.get("console"),
                "node_id": node["node_id"],
            }

    with open("console_ports.json", "w") as f:
        json.dump(console_map, f, indent=2)
    print(f"\n[OK] 콘솔 포트 매핑 → console_ports.json 저장 완료")

    # 6) 시작 여부
    ans = input("\n모든 노드를 시작하시겠습니까? (y/n): ").strip().lower()
    if ans == "y":
        api.start_all(pid)

    print("\n[DONE] 토폴로지 빌드 완료!")
    return all_nodes


def main():
    parser = argparse.ArgumentParser(description="GNS3 Multivendor Topology Builder")
    parser.add_argument("--server", default=GNS3_SERVER, help="GNS3 서버 URL")
    args = parser.parse_args()
    build_topology(args.server)


if __name__ == "__main__":
    main()
