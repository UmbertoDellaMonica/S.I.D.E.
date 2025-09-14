"""
Gestione dei pacchetti catturati
"""

from scapy.all import TCP, IP, Raw
from configuration.side_sniffer_configuration import MODBUS_PORT, S7_PORT, OPCUA_PORT

from decoder.modbus_decoder import parse_modbus_payload  # helper separato
from decoder.s7_decoder import parse_s7_payload
from decoder.opcua_decoder import parse_opcua_payload

from discovery.side_sniffer_discovery import publish_discovery_event


def modbus_packet_handler(packet):
    """
    Callback per ogni pacchetto Modbus TCP
    - Gestisce richieste e risposte
    - Gestisce eccezioni
    - Ignora multi-frame
    """
    if packet.haslayer(TCP) and packet.haslayer(IP):
        tcp_layer = packet[TCP]
        ip_layer = packet[IP]

        if tcp_layer.sport == MODBUS_PORT or tcp_layer.dport == MODBUS_PORT:
            info = (
                f"{ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}"
            )

            if packet.haslayer(Raw):
                payload = packet[Raw].load
                parsed = parse_modbus_payload(payload)

                if parsed:

                    data_bytes = parsed.get("data")

                    event = {
                        "protocol": "Modbus",
                        "src_ip": ip_layer.src,
                        "dst_ip": ip_layer.dst,
                        "src_port": tcp_layer.sport,
                        "dst_port": tcp_layer.dport,
                        "transaction_id": parsed["transaction_id"],
                        "unit_id": parsed["unit_id"],
                        "function_code": parsed["function_code"],
                        "function_name": parsed.get("function_name"),
                        "exception": parsed.get("exception"),
                        "data": (
                            data_bytes.hex()
                            if isinstance(data_bytes, (bytes, bytearray))
                            else None
                        ),
                    }

                    # Publish event on RabbitMQ
                    publish_discovery_event(event)

                    if parsed["exception"]:
                        print(
                            f"[MODBUS-EXC] {info} | "
                            f"TID={parsed['transaction_id']} | "
                            f"UID={parsed['unit_id']} | "
                            f"FC=0x{parsed['function_code']:02X} | "
                            f"Exception={parsed['exception_code']} ({parsed['exception_message']})"
                        )
                    else:
                        print(
                            f"[MODBUS] {info} | "
                            f"TID={parsed['transaction_id']} | "
                            f"UID={parsed['unit_id']} | "
                            f"FC={parsed['function_code']} ({parsed['function_name']}) | "
                            f"Data={parsed['data'].hex()}"
                        )
                else:
                    print(f"[MODBUS] {info} | Payload troppo corto ({len(payload)}B)")
            else:
                print(f"[MODBUS] {info} | Nessun payload")


def s7_packet_handler(packet):
    """
    Callback per ogni pacchetto S7 TCP
    - Gestisce richieste e risposte S7
    - Ignora segmenti multipli complessi
    - Mostra i dati in ASCII leggibile
    """
    if packet.haslayer(TCP) and packet.haslayer(IP):
        tcp_layer = packet[TCP]
        ip_layer = packet[IP]

        if tcp_layer.sport == S7_PORT or tcp_layer.dport == S7_PORT:
            info = (
                f"{ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}"
            )

            if packet.haslayer(Raw):
                payload = packet[Raw].load
                parsed = parse_s7_payload(payload)

                if parsed:
                    # Sicurezza per valori None
                    job_function = parsed.get("job_function")
                    job_function_name = parsed.get("job_function_name", "Unknown")
                    job_function_hex = (
                        f"{job_function:02X}" if job_function is not None else "N/A"
                    )

                    area_name = parsed.get("area_name", "N/A")
                    db_number = parsed.get("db_number", "N/A")
                    data = parsed.get("data")
                    # Conversione in ASCII, caratteri non stampabili diventano '?'
                    data_ascii = (
                        data.decode("ascii", errors="replace") if data else "N/A"
                    )

                    parameters = parsed.get("parameters")
                    parameters_ascii = (
                        parameters.decode("ascii", errors="replace")
                        if parameters
                        else None
                    )

                    # Costruisci evento
                    event = {
                        "protocol": "S7",
                        "src_ip": ip_layer.src,
                        "dst_ip": ip_layer.dst,
                        "src_port": tcp_layer.sport,
                        "dst_port": tcp_layer.dport,
                        "tpkt_version": parsed.get("tpkt_version"),
                        "tpkt_length": parsed.get("tpkt_length"),
                        "cotp_pdu_type": parsed.get("cotp_pdu_type"),
                        "pdu_type": parsed.get("pdu_type"),
                        "rosctr": parsed.get("rosctr"),
                        "pdu_reference": parsed.get("pdu_reference"),
                        "parameter_length": parsed.get("parameter_length"),
                        "data_length": parsed.get("data_length"),
                        "job_function": job_function,
                        "job_function_name": job_function_name,
                        "area": parsed.get("area"),
                        "area_name": area_name,
                        "db_number": db_number,
                        "parameters": parameters_ascii,
                        "data": data_ascii,
                    }

                    # Publish event su RabbitMQ
                    publish_discovery_event(event)

                    # Stampa leggibile
                    print(
                        f"[S7] {info} | Job=0x{job_function_hex} ({job_function_name})"
                        f" | Area={area_name} DB={db_number} | Data='{data_ascii}'"
                    )
                else:
                    print(f"[S7] {info} | Payload troppo corto ({len(payload)}B)")
            else:
                print(f"[S7] {info} | Nessun payload")


def opcua_packet_handler(packet):
    """
    Callback per ogni pacchetto OPC UA TCP
    - Gestisce richieste e risposte
    - Analizza TPKT + UA Binary Encoding
    """
    if packet.haslayer(TCP) and packet.haslayer(IP):
        tcp_layer = packet[TCP]
        ip_layer = packet[IP]

        if tcp_layer.sport == OPCUA_PORT or tcp_layer.dport == OPCUA_PORT:
            info = (
                f"{ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}"
            )

            if packet.haslayer(Raw):
                payload = packet[Raw].load
                parsed = parse_opcua_payload(payload)

                if parsed:
                    event = {
                        "protocol": "OPC-UA",
                        "src_ip": ip_layer.src,
                        "dst_ip": ip_layer.dst,
                        "src_port": tcp_layer.sport,
                        "dst_port": tcp_layer.dport,
                        "message_type": parsed.get("message_type"),
                        "chunk_type": parsed.get("chunk_type"),
                        "secure_channel_id": parsed.get("secure_channel_id"),
                        "sequence_number": parsed.get("sequence_number"),
                        "request_id": parsed.get("request_id"),
                        "payload_length": len(payload),
                        "payload_data": parsed.get("payload_data"),
                    }

                    # Publish event su RabbitMQ
                    publish_discovery_event(event)

                    # Stampa leggibile
                    print(
                        f"[OPC-UA] {info} | Type={parsed['message_type']} "
                        f"Chunk={parsed['chunk_type']} SCID={parsed.get('secure_channel_id')} "
                        f"Seq={parsed.get('sequence_number')} ReqID={parsed.get('request_id')}"
                    )
                else:
                    print(f"[OPC-UA] {info} | Payload troppo corto ({len(payload)}B)")
            else:
                print(f"[OPC-UA] {info} | Nessun payload")
