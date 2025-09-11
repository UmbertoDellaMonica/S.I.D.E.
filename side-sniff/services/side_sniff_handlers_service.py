"""
Gestione dei pacchetti catturati
"""

from scapy.all import TCP, IP, Raw
from configuration.side_sniffer_configuration import MODBUS_PORT
from decoder.modbus_decoder import parse_modbus_payload  # helper separato
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
