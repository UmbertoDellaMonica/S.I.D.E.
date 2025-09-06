"""
Gestione dei pacchetti catturati
"""

from scapy.all import TCP, IP, Raw
from configuration.side_sniffer_configuration import MODBUS_PORT


def modbus_packet_handler(packet):
    """
    Callback per ogni pacchetto Modbus TCP catturato
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
                print(f"[MODBUS] {info} | Payload (hex): {payload.hex()}")
            else:
                print(f"[MODBUS] {info} | Nessun payload")
