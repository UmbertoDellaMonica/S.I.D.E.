import struct
from scapy.all import TCP, IP, Raw
from configuration.side_sniffer_configuration import S7_PORT


# --- Dizionari di supporto ---
S7_JOB_FUNCTIONS = {
    0x01: "CPU Function",
    0x02: "Unknown/Handshake",
    0x03: "User Data",
    0x04: "Read Variable",
    0x05: "Write Variable",
    0x07: "User Communication",
    0x08: "Diagnostic",
    0x10: "PLC Control",
    0x11: "PLC Status",
    0x12: "Alarm",
    0x2E: "Read/Write Multiple Variables",
}

S7_MEMORY_AREAS = {
    0x81: "PE (Process Inputs)",
    0x82: "PA (Process Outputs)",
    0x83: "MK (Merker/Flags)",
    0x84: "DB (Data Block)",
    0x1C: "CT (Counter)",
    0x1D: "TM (Timer)",
}

S7_ROSCTR = {
    1: "Job Request",
    2: "Ack Data",
    3: "User Data",
    7: "Ack",
}


def parse_s7_payload(payload: bytes) -> dict | None:
    """Parsing avanzato di pacchetto S7 TCP"""
    if len(payload) < 10:
        return None

    try:
        # --- TPKT Header ---
        version, reserved, total_length = struct.unpack(">BBH", payload[:4])

        # --- COTP Header ---
        cotp_length = payload[4]
        cotp_pdu_type = payload[5]

        # --- S7 PDU Header ---
        s7_start = 4 + cotp_length
        if len(payload) < s7_start + 8:
            return None

        pdu_type, rosctr, reserved1, pdu_ref, param_len, data_len = struct.unpack(
            ">BBHBBH", payload[s7_start : s7_start + 8]
        )

        # Parametri e dati
        param_data = payload[s7_start + 8 : s7_start + 8 + param_len]
        actual_data = payload[
            s7_start
            + 8
            + param_len : s7_start
            + 8
            + param_len
            + min(data_len, len(payload) - (s7_start + 8 + param_len))
        ]

        parsed = {
            "tpkt_version": version,
            "tpkt_length": total_length,
            "cotp_pdu_type": cotp_pdu_type,
            "pdu_type": pdu_type,
            "rosctr": rosctr,
            "rosctr_name": S7_ROSCTR.get(rosctr, "Unknown"),
            "pdu_reference": pdu_ref,
            "parameter_length": param_len,
            "data_length": data_len,
            "parameters": param_data,
            "data": actual_data,
            "job_function": None,
            "job_function_name": None,
            "items": [],
        }

        # Analisi Job Function
        if param_data:
            function_code = param_data[0]
            parsed["job_function"] = function_code
            parsed["job_function_name"] = S7_JOB_FUNCTIONS.get(
                function_code, f"Unknown (0x{function_code:02X})"
            )

        # Parsing Read/Write Items
        items = []
        if param_data and len(param_data) > 1 and param_data[0] in (0x04, 0x05, 0x2E):
            item_count = param_data[1]
            idx = 2
            for _ in range(item_count):
                if len(param_data) < idx + 4:
                    break
                area_code = param_data[idx + 1]
                db_number = None
                start = None
                length = None
                # Area DB
                if area_code == 0x84 and len(param_data) >= idx + 8:
                    db_number = struct.unpack(">H", param_data[idx + 2 : idx + 4])[0]
                    start = struct.unpack(">H", param_data[idx + 4 : idx + 6])[0]
                    length = struct.unpack(">H", param_data[idx + 6 : idx + 8])[0]
                items.append(
                    {
                        "area": area_code,
                        "area_name": S7_MEMORY_AREAS.get(area_code, "Unknown"),
                        "db_number": db_number,
                        "start": start,
                        "length": length,
                    }
                )
                # avanzamento indice (semplificato)
                idx += 8 if area_code == 0x84 else 4
        parsed["items"] = items

        return parsed
    except Exception as e:
        print("Errore parsing S7:", e)
        return None
