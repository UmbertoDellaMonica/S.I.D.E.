"""
Funzioni per avviare lo sniffing in thread separato
"""

import threading
from scapy.all import sniff
from core.side_sniffer_dispatcher import dispatch_packet


def start_sniffer(interface, stop_event):
    sniff(
        iface=interface,
        prn=dispatch_packet,
        store=False,
        filter="",
        stop_filter=lambda x: stop_event.is_set(),
    )


def run_sniffer_in_thread(interface):
    stop_event = threading.Event()
    t = threading.Thread(target=start_sniffer, args=(interface, stop_event))
    t.start()
    return t, stop_event
