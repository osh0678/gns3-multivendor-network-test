"""Vendor CLI 모듈 패키지"""
from .cisco_ios import CiscoIOS
from .cisco_iosxe import CiscoIOSXE
from .arista_eos import AristaEOS
from .sixwind import SixWind
from .fortinet import Fortinet
from .hpe_comware import HPEComware
from .aruba_cx import ArubaCX
from .mikrotik import MikroTik
from .huawei_vrp import HuaweiVRP
from .f5_bigip import F5BigIP

VENDOR_MAP = {
    "cisco_ios": CiscoIOS,
    "cisco_iosxe": CiscoIOSXE,
    "arista_eos": AristaEOS,
    "sixwind": SixWind,
    "fortinet": Fortinet,
    "hpe_comware": HPEComware,
    "aruba_cx": ArubaCX,
    "mikrotik": MikroTik,
    "huawei_vrp": HuaweiVRP,
    "f5_bigip": F5BigIP,
}
