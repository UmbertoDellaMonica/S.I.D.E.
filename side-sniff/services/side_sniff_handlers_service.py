"""
Gestione dei pacchetti catturati
"""

from scapy.all import TCP, IP, Raw
from configuration.side_sniffer_configuration import MODBUS_PORT
from parser.modbus_parser import parse_modbus_payload  # helper separato
from scapy.all import TCP, UDP


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
