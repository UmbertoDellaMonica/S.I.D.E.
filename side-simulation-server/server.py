"""
Entry point per avviare il server Modbus TCP
"""

import logging
from pymodbus.server import StartTcpServer
from pymodbus.transaction import ModbusSocketFramer

from configuration_server import HOST, PORT
from store_server import create_modbus_store
from identity_server import create_identity

# --- Logging generale ---
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)  # DEBUG mostra tutte le richieste


# --- Avvio server ---
def run_modbus_server():
    context = create_modbus_store()
    identity = create_identity()

    print(f"[*] Avvio Modbus server su {HOST}:{PORT}")
    print("[*] Logging richieste attivo (DEBUG)")

    # StartTcpServer non permette hook diretto per callback request,
    # quindi il logging dettagliato avviene tramite livello DEBUG
    StartTcpServer(
        context=context,
        identity=identity,
        address=(HOST, PORT),
        framer=ModbusSocketFramer,
    )


if __name__ == "__main__":
    run_modbus_server()
