"""
Gestione delle interfacce di rete
"""

import platform
from scapy.all import get_if_list, get_if_addr, get_if_hwaddr


def select_interface():
    """
    Mostra le interfacce disponibili e permette all'utente di selezionare una interfaccia fisica
    """
    system_os = platform.system()
    interfaces = get_if_list()
    print(f"[*] Sistema operativo rilevato: {system_os}")
    print("[*] Interfacce disponibili:")

    for i, iface in enumerate(interfaces):
        try:
            ip = get_if_addr(iface)
            mac = get_if_hwaddr(iface)
        except Exception:
            ip = "N/A"
            mac = "N/A"
        print(f"{i}: {iface} | IP: {ip} | MAC: {mac}")

    while True:
        try:
            idx = int(input("Seleziona il numero dell'interfaccia da usare: "))
            if 0 <= idx < len(interfaces):
                selected_iface = interfaces[idx]
                print(f"[*] Hai selezionato: {selected_iface}")
                return selected_iface
            else:
                print("[!] Numero non valido, riprova.")
        except ValueError:
            print("[!] Inserisci un numero valido.")
