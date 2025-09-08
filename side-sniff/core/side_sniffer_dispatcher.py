from services.side_sniff_handlers_service import modbus_packet_handler
from core.side_sniffer_protocol_tree import protocol_tree
from configuration.side_sniffer_configuration import Protocol
from scapy.all import TCP, UDP

# Mappa protocollo -> handler
PROTOCOL_HANDLERS = {
    Protocol.MODBUS: modbus_packet_handler,
    # puoi aggiungere altri handler: "http": http_handler, "bacnet": bacnet_handler
}


def dispatch_packet(packet):
    layer_type = None
    port = None

    # Determina se è TCP o UDP
    if packet.haslayer(TCP):
        layer_type = "TCP"
        port = packet[TCP].sport or packet[TCP].dport
    elif packet.haslayer(UDP):
        layer_type = "UDP"
        port = packet[UDP].sport or packet[UDP].dport

    if not layer_type or not port:
        return  # Non è TCP/UDP, ignoralo

    # Cerca corrispondenza nel Radix Tree
    key = f"{layer_type}-{port}"
    match = protocol_tree.search(key)

    if match:
        protocol_name = match[0]["protocol"]
        print(f"[INFO] Pacchetto identificato come {protocol_name}")
        handler = PROTOCOL_HANDLERS.get(protocol_name)
        if handler:
            handler(packet)
        else:
            print(f"[WARN] Nessun handler registrato per protocollo {protocol_name}")
