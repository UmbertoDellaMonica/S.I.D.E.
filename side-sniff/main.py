"""
Entry point dello sniffer
"""

from services.side_sniff_interface_service import select_interface
from core.side_sniffer_core import run_sniffer_in_thread

if __name__ == "__main__":
    iface = select_interface()
    t, stop_event = run_sniffer_in_thread(iface)

    try:
        while t.is_alive():
            t.join(1)  # permette al main thread di intercettare Ctrl+C
    except KeyboardInterrupt:
        print("\n[!] Interruzione richiesta dall'utente. Fermando lo sniffer...")
        stop_event.set()
        t.join()
        print("[*] Sniffer terminato correttamente.")
