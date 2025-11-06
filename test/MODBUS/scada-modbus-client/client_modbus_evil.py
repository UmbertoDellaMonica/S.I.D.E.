#!/usr/bin/env python3
"""
client_modbus_custom.py

Client Modbus per test IDS basato su pacchetti CSV forniti.
Invia pacchetti personalizzati simili a quelli catturati.
"""

import argparse
import time
import random
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from scapy.all import IP, TCP, Ether, Raw, sendp

# -----------------------
# Parametri di sicurezza
# -----------------------
MAX_SAFE_DURATION = 600  # secondi
DEFAULT_SLEEP = 1.0


# -----------------------
# Funzioni utili
# -----------------------
def now():
    return datetime.now().isoformat()


def safe_sleep(sec):
    try:
        time.sleep(sec)
    except KeyboardInterrupt:
        raise


# -----------------------
# Funzione per inviare pacchetto custom
# -----------------------
def send_custom_modbus_packet(
    src_ip, dst_ip, src_port, dst_port, tcp_flags, payload_hex=""
):
    """Costruisce pacchetto TCP/IP con Scapy simile a quelli del CSV e lo invia"""
    payload_bytes = bytes.fromhex(payload_hex) if payload_hex else b""
    packet = (
        Ether()
        / IP(src=src_ip, dst=dst_ip)
        / TCP(sport=src_port, dport=dst_port, flags=tcp_flags)
        / Raw(load=payload_bytes)
    )
    sendp(packet, verbose=False)
    print(
        f"{now()} [CUSTOM] Packet inviato {src_ip}:{src_port} -> {dst_ip}:{dst_port} Flags={tcp_flags} DataLen={len(payload_bytes)}"
    )


# -----------------------
# Pattern CSV-based
# -----------------------
def pattern_csv_like(client, unit_id, duration):
    """
    Replica pattern simili al CSV:
    - alternanza tra pacchetti con Raw e Padding
    - funzione Modbus Read Holding Registers
    - utilizza indirizzi, porte e flags dal CSV
    """
    print(f"{now()} [TEST] pattern_csv_like start: duration={duration}s")
    end_time = time.time() + duration

    src_ips = ["172.27.224.70", "172.27.224.250", "172.27.224.251"]
    dst_ips = ["172.27.224.250", "172.27.224.70", "172.27.224.250"]
    src_ports = [49499, 502, 57569]
    dst_ports = [502, 49499, 502]
    tcp_flags_list = ["A", "PA", "S", "SA", "FA"]

    payloads = [
        "0000000b",
        "16000100000000000000000000001e0000000000000000",
        "0006001e",
    ]

    while time.time() < end_time:
        # selezione randomizzata simile ai dati CSV
        idx = random.randint(0, len(src_ips) - 1)
        src_ip, dst_ip = src_ips[idx], dst_ips[idx]
        src_port, dst_port = src_ports[idx], dst_ports[idx]
        tcp_flags = random.choice(tcp_flags_list)
        payload_hex = random.choice(payloads)

        # invio pacchetto custom
        send_custom_modbus_packet(
            src_ip, dst_ip, src_port, dst_port, tcp_flags, payload_hex
        )

        # pacing simile al CSV
        safe_sleep(random.uniform(0.05, 0.15))

    print(f"{now()} [TEST] pattern_csv_like end")


# -----------------------
# Main
# -----------------------
def main():
    parser = argparse.ArgumentParser(
        description="Custom Modbus IDS test client (lab only)"
    )
    parser.add_argument(
        "--target", required=False, default="127.0.0.1", help="IP del server target"
    )
    parser.add_argument("--unit", type=int, default=1, help="Unit ID Modbus")
    parser.add_argument("--duration", type=int, default=10, help="Durata in secondi")
    args = parser.parse_args()

    print(
        f"{now()} [CLIENT-TEST] Target={args.target}:502 Unit={args.unit} Duration={args.duration}s"
    )
    client = ModbusTcpClient(args.target, port=502)
    if not client.connect():
        print(f"{now()} [ERROR] impossibile connettersi a {args.target}:502")
        return

    try:
        pattern_csv_like(client, args.unit, args.duration)
    except KeyboardInterrupt:
        print(f"{now()} [CLIENT-TEST] Interrotto dall'utente")
    finally:
        client.close()
        print(f"{now()} [CLIENT-TEST] Connessione chiusa")


if __name__ == "__main__":
    main()
