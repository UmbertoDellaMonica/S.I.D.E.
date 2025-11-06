"""
Configurazioni generali dello sniffer
"""

from enum import Enum


BASE_DIR_CONFIGURATION = "configuration"

BASE_DIR_RULES = "rules"

RULES_FILE = "protocol_rules.json"


# ---- PORT STANDARD CONFIGURATION ---- #

MODBUS_PORT = 502
S7_PORT = 102
OPCUA_PORT = 4840


class Protocol(Enum):
    MODBUS = "Modbus"
    SNAP_7 = "S7"
    OPC_UA = "OPC-UA"
    # IEC104 = "IEC 60870-5-104"
    # MQTT = "MQTT"
