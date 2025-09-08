"""
Configurazioni generali dello sniffer
"""

from enum import Enum


MODBUS_PORT = 502


BASE_DIR_CONFIGURATION = "configuration"

BASE_DIR_RULES = "rules"

RULES_FILE = "protocol_rules.json"


class Protocol(Enum):
    MODBUS = "Modbus"
    DNP3 = "DNP3"
    OPC_UA = "OPC-UA"
    IEC104 = "IEC 60870-5-104"
    MQTT = "MQTT"
