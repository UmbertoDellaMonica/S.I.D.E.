from scapy.all import TCP, IP, Raw
from configuration.side_sniffer_configuration import MODBUS_PORT
import struct

#### Struct of Single Packet
""" 
Il pacchetto modbus è composto da vari identificativi : 

- Transaction ID (2byte) 
- Protocol ID (2 byte) 
- Length (2 byte) 
- Unit ID (1 byte) 
- Function Code (1 byte) 
- Dati (variabile) 

"""


# Dizionario dei function code Modbus
MODBUS_FUNCTIONS = {
    1: "Read Coils",
    2: "Read Discrete Inputs",
    3: "Read Holding Registers",
    4: "Read Input Registers",
    5: "Write Single Coil",
    6: "Write Single Register",
    15: "Write Multiple Coils",
    16: "Write Multiple Registers",
}

# Dizionario exception codes Modbus
MODBUS_EXCEPTIONS = {
    1: "Illegal Function",
    2: "Illegal Data Address",
    3: "Illegal Data Value",
    4: "Slave Device Failure",
    6: "Slave Device Busy",
    10: "Gateway Path Unavailable",
}


def parse_modbus_payload(payload: bytes) -> dict | None:
    """
    Parsing di un singolo pacchetto Modbus TCP (senza multi-frame)
    """
    if len(payload) < 8:
        return None  # Payload troppo corto

    # MBAP Header: Transaction ID, Protocol ID, Length
    transaction_id, protocol_id, length = struct.unpack(">HHH", payload[:6])
    unit_id = payload[6]
    function_code = payload[7]
    data = payload[8:] if len(payload) > 8 else b""

    parsed = {
        "transaction_id": transaction_id,
        "protocol_id": protocol_id,
        "length": length,
        "unit_id": unit_id,
        "function_code": function_code,
        "data": data,
    }

    # Gestione eccezioni Modbus
    if function_code >= 0x80:
        parsed["exception"] = True
        parsed["exception_code"] = data[0] if data else None
        parsed["exception_message"] = MODBUS_EXCEPTIONS.get(
            parsed["exception_code"], "Unknown Exception"
        )
    else:
        parsed["exception"] = False
        parsed["function_name"] = MODBUS_FUNCTIONS.get(function_code, "Unknown")

    return parsed
