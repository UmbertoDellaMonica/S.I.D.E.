"""
Gestione interfacce di rete cross-platform
Stampa a video le interfacce disponibili con informazioni dettagliate
"""

import platform
import psutil
from scapy.all import get_if_list, get_if_addr, get_if_hwaddr


def list_interfaces():
    """Raccoglie informazioni dettagliate sulle interfacce disponibili"""
    interfaces_info = []
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()

    for iface in get_if_list():
        try:
            ip = get_if_addr(iface)
        except Exception:
            ip = "N/A"
        try:
            mac = get_if_hwaddr(iface)
        except Exception:
            mac = "N/A"

        iface_stat = stats.get(iface, None)
        status = iface_stat.isup if iface_stat else "N/A"
        mtu = iface_stat.mtu if iface_stat else "N/A"
        speed = f"{iface_stat.speed} Mb/s" if iface_stat and iface_stat.speed else "N/A"

        interfaces_info.append(
            {
                "name": iface,
                "ip": ip,
                "mac": mac,
                "status": status,
                "mtu": mtu,
                "speed": speed,
            }
        )

    return interfaces_info


def select_interface():
    """
    Mostra tutte le interfacce disponibili in base al sistema operativo
    e permette all'utente di selezionare una NIC per sniffing
    """
    system_os = platform.system()
    print(f"[*] Sistema operativo rilevato: {system_os}")

    interfaces = list_interfaces()
    print("[*] Interfacce disponibili:")

    for i, iface in enumerate(interfaces):
        print(
            f"{i}: {iface['name']} | IP: {iface['ip']} | MAC: {iface['mac']} | "
            f"Status: {iface['status']} | MTU: {iface['mtu']} | Speed: {iface['speed']}"
        )

    while True:
        try:
            idx = input("Seleziona il numero dell'interfaccia da usare (default 0): ")
            if idx.strip() == "":
                idx = 0
            else:
                idx = int(idx)

            if 0 <= idx < len(interfaces):
                selected_iface = interfaces[idx]["name"]
                print(f"[*] Hai selezionato: {selected_iface}")
                return selected_iface
            else:
                print("[!] Numero non valido, riprova.")
        except ValueError:
            print("[!] Inserisci un numero valido.")
