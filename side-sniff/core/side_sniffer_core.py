"""
Funzioni per avviare lo sniffing in thread separato
"""

import threading
from scapy.all import sniff
from services.side_sniff_handlers_service import modbus_packet_handler
from configuration.side_sniffer_configuration import MODBUS_PORT


def start_sniffer(interface, stop_event):
    """
    Avvia lo sniffing dei pacchetti Modbus TCP sulla porta 502
    """
    sniff(
        iface=interface,
        prn=modbus_packet_handler,
        store=False,
        filter=f"tcp port {MODBUS_PORT}",
        stop_filter=lambda x: stop_event.is_set(),
    )


def run_sniffer_in_thread(interface):
    stop_event = threading.Event()
    t = threading.Thread(target=start_sniffer, args=(interface, stop_event))
    t.start()
    return t, stop_event
