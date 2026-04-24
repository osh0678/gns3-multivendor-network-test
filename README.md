# GNS3 Multivendor Network Test

GNS3 기반 멀티벤더 네트워크 토폴로지 구성 및 자동 테스트 프로젝트입니다.  
7개 벤더 Pod를 구성하고, 각 벤더 고유 CLI 명령어로 VLAN/IP 설정 및 연결 테스트를 수행합니다.

## 토폴로지 구조

각 Pod는 동일한 계층형 트리 구조를 따릅니다:

```
    Access-SW-3   Access-SW-4        ← 액세스 스위치 (VLAN Upper)
         \           /
      Distribution-SW-1              ← 분배 스위치 1
              |
           Router                    ← 벤더별 라우터 (Inter-VLAN 라우팅)
              |
      Distribution-SW-2              ← 분배 스위치 2
         /           \
    Access-SW-5   Access-SW-6        ← 액세스 스위치 (VLAN Lower)
```

### 7개 벤더 Pod 구성

| Pod | 라우터 | 스위치 | VLAN Upper | VLAN Lower | 서브넷 Upper | 서브넷 Lower |
|-----|--------|--------|-----------|-----------|-------------|-------------|
| Pod 1 | **6WIND** Turbo Router 3.4.0 | **Arista** vEOS 4.33.1F | 10 | 20 | 10.1.10.0/24 | 10.1.20.0/24 |
| Pod 2 | **Cisco** 7200 (IOS) | **Cisco** Catalyst IOS-XE 9kv | 30 | 40 | 10.2.30.0/24 | 10.2.40.0/24 |
| Pod 3 | **Fortinet** FortiADC 7.0.0 | **Cisco** Catalyst IOS-XE 9kv | 50 | 60 | 10.3.50.0/24 | 10.3.60.0/24 |
| Pod 4 | **HPE** VSR1001 (Comware) | **HP Aruba** CX (AOS-CX) | 70 | 80 | 10.4.70.0/24 | 10.4.80.0/24 |
| Pod 5 | **MikroTik** CHR 7.17 | **Cisco** Catalyst IOS-XE 9kv | 90 | 100 | 10.5.90.0/24 | 10.5.100.0/24 |
| Pod 6 | **Huawei** NE40E (VRP) | **Huawei** CE12800 (VRP) | 110 | 120 | 10.6.110.0/24 | 10.6.120.0/24 |
| Pod 7 | **F5** BIG-IP LTM 17.5 | **Huawei** CE12800 (VRP) | 130 | 140 | 10.7.130.0/24 | 10.7.140.0/24 |

### IP 할당 규칙

각 서브넷 내에서:

| 역할 | 호스트 ID | 예시 (Pod 2 Upper) |
|------|----------|-------------------|
| Router (sub-interface) | .1 | 10.2.30.1 |
| Distribution Switch (SVI) | .2 | 10.2.30.2 |
| Access Switch 1 (SVI) | .11 | 10.2.30.11 |
| Access Switch 2 (SVI) | .12 | 10.2.30.12 |

## 사전 요구사항

- **GNS3** 2.2+ 설치 및 실행 중
- **Python** 3.10+
- 각 벤더 이미지가 GNS3에 등록되어 있어야 합니다:
  - 6WIND Turbo Router 3.4.0
  - Arista vEOS 4.33.1F
  - Cisco 7200 (IOS)
  - Cisco Catalyst 9000v (IOS-XE)
  - Fortinet FortiADC 7.0.0
  - HPE VSR1001 (Comware 7)
  - HP Aruba CX (AOS-CX)
  - MikroTik CHR 7.17
  - Huawei NE40E / CE12800 (VRP)
  - F5 BIG-IP LTM Virtual 17.5

## 설치

```bash
git clone https://github.com/osh0678/gns3-multivendor-network-test.git
cd gns3-multivendor-network-test
pip install -r requirements.txt
```

## 사용 방법

### Step 1: GNS3 토폴로지 생성

```bash
# GNS3 서버가 기본 포트(3080)에서 실행 중일 때
python topology.py

# 커스텀 서버 주소
python topology.py --server http://192.168.1.100:3080
```

이 명령은:
1. GNS3 프로젝트를 생성합니다
2. 7개 Pod × 7대 장비 = 49개 노드를 생성합니다
3. 각 Pod 내 라우터-분배-액세스 간 링크를 연결합니다
4. `console_ports.json`에 콘솔 포트 정보를 저장합니다

### Step 2: 장비 설정 배포

```bash
# 설정 파일만 생성 (GNS3에 배포하지 않음)
python config_deploy.py --generate-only --all

# 전체 Pod에 설정 배포
python config_deploy.py --all

# 특정 Pod만 배포
python config_deploy.py --pod pod2

# 커스텀 GNS3 서버
python config_deploy.py --all --server 192.168.1.100
```

### Step 3: 네트워크 테스트

```bash
# 전체 Pod 연결 테스트
python network_test.py --all

# 특정 Pod만 테스트
python network_test.py --pod pod6

# 상세 출력 + Show 명령어 포함
python network_test.py --all --verbose --show

# 테스트 리포트 저장
python network_test.py --all --report my_report.json
```

### Step 4: 단위 테스트 (설정 검증)

```bash
# IP/VLAN 고유성, 벤더 모듈, 토폴로지 검증
pytest tests/test_connectivity.py -v
```

## 프로젝트 구조

```
gns3-multivendor-network-test/
├── README.md                    # 이 문서
├── requirements.txt             # Python 의존성
├── .gitignore
├── settings.py                  # 전체 Pod/VLAN/IP 설정
├── topology.py                  # GNS3 토폴로지 생성 (REST API)
├── config_deploy.py             # 벤더별 설정 배포 (Telnet)
├── network_test.py              # 연결 테스트 (Ping + Show)
│
├── vendors/                     # 벤더별 CLI 모듈
│   ├── __init__.py
│   ├── base.py                  # 추상 베이스 클래스
│   ├── cisco_ios.py             # Cisco IOS (7200 라우터)
│   ├── cisco_iosxe.py           # Cisco IOS-XE (Catalyst 9kv 스위치)
│   ├── arista_eos.py            # Arista EOS (vEOS 스위치)
│   ├── sixwind.py               # 6WIND Turbo Router (fp-cli)
│   ├── fortinet.py              # Fortinet FortiADC (FortiOS)
│   ├── hpe_comware.py           # HPE Comware (VSR1001)
│   ├── aruba_cx.py              # HP Aruba CX (AOS-CX)
│   ├── mikrotik.py              # MikroTik RouterOS (CHR)
│   ├── huawei_vrp.py            # Huawei VRP (NE40E/CE12800)
│   └── f5_bigip.py              # F5 BIG-IP (tmsh)
│
├── configs/                     # 생성된 정적 설정 파일
│   ├── pod1_6wind_arista/
│   ├── pod2_cisco/
│   ├── pod3_fortinet_cisco/
│   ├── pod4_hpe_aruba/
│   ├── pod5_mikrotik_cisco/
│   ├── pod6_huawei/
│   └── pod7_f5_huawei/
│
└── tests/
    └── test_connectivity.py     # pytest 기반 검증 테스트
```

## 벤더별 CLI 명령어 예시

### Cisco IOS (Router)
```
enable
configure terminal
hostname Cisco7200-R1
interface GigabitEthernet0/1.30
  encapsulation dot1Q 30
  ip address 10.2.30.1 255.255.255.0
```

### Cisco IOS-XE (Switch)
```
enable
configure terminal
vlan 30
  name VLAN30
interface GigabitEthernet1/0/1
  switchport mode trunk
  switchport trunk allowed vlan 30,40
interface Vlan30
  ip address 10.2.30.2 255.255.255.0
```

### Arista EOS (Switch)
```
enable
configure terminal
vlan 10
  name VLAN10
interface Ethernet1
  switchport mode trunk
  switchport trunk allowed vlan 10,20
interface Vlan10
  ip address 10.1.10.2/24
```

### 6WIND Turbo Router
```
fp-cli
set system hostname 6WIND-TR-1
set interfaces vlan vlan10 physical-interface eth1
set interfaces vlan vlan10 vlan-id 10
set interfaces vlan vlan10 ipv4 address 10.1.10.1/24
commit
```

### Fortinet FortiADC
```
config system global
  set hostname FortiADC-R1
end
config system interface
  edit "vlan50"
    set vdom "root"
    set ip 10.3.50.1 255.255.255.0
    set type vlan
    set vlanid 50
    set interface "port2"
  next
end
```

### HPE Comware (Router)
```
system-view
sysname HPE-VSR-R1
vlan 70
  description VLAN70-Upper
interface GigabitEthernet1/1
  port link-type trunk
  port trunk permit vlan 70
interface Vlan-interface70
  ip address 10.4.70.1 255.255.255.0
```

### HP Aruba CX (Switch)
```
configure terminal
hostname Aruba-DSW-1
vlan 70
  name VLAN70
interface 1/1/1
  no shutdown
  no routing
  vlan trunk native 1
  vlan trunk allowed 70,80
interface vlan 70
  ip address 10.4.70.2/24
```

### MikroTik RouterOS
```
/system identity set name=MikroTik-CHR-R1
/interface vlan add interface=ether2 name=vlan90 vlan-id=90
/ip address add address=10.5.90.1/24 interface=vlan90
/ip settings set ip-forward=yes
```

### Huawei VRP (Router/Switch)
```
system-view
sysname HuaWei-NE40E-R1
vlan batch 110 120
interface GigabitEthernet0/0/1
  port link-type trunk
  port trunk allow-pass vlan 110
interface Vlanif110
  ip address 10.6.110.1 255.255.255.0
```

### F5 BIG-IP (tmsh)
```
tmsh
modify sys global-settings hostname F5-BIGIP-R1
create net vlan vlan130 tag 130 interfaces add { 1.2 { tagged } }
create net self self_vlan130 address 10.7.130.1/24 vlan vlan130 allow-service add { default }
save sys config
```

## 커스터마이징

### 새 벤더 추가

1. `vendors/` 디렉토리에 새 벤더 모듈 파일 생성
2. `VendorBase` 클래스를 상속하고 모든 추상 메서드 구현
3. `vendors/__init__.py`의 `VENDOR_MAP`에 등록
4. `settings.py`의 `PODS`에 새 Pod 추가

### VLAN/IP 변경

`settings.py`의 `PODS` 딕셔너리에서 수정:
```python
"pod2": {
    "vlan_upper": 30,       # ← VLAN 번호 변경
    "vlan_lower": 40,
    "subnet_upper": "10.2.30.0/24",  # ← IP 대역 변경
    ...
}
```

## 라이선스

MIT License
