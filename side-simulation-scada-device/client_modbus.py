import time
import random
import os
import sys
from dotenv import load_dotenv
from pymodbus.client import ModbusTcpClient

# --- Caricamento variabili ambiente ---
load_dotenv()
SERVER_IP = os.getenv("HOST_SERVER_TARGET")
SERVER_PORT = int(
    os.getenv("HOST_SERVER_PORT_TARGET", 5020)
)  # default 5020 se non impostato

# --- Lettura unit_id da parametro CLI ---
if len(sys.argv) < 2:
    print(f"Uso: python {sys.argv[0]} <unit_id>")
    sys.exit(1)

UNIT_ID = int(sys.argv[1])
print(f"[CLIENT] Avvio client Modbus con UNIT_ID = {UNIT_ID}")

# --- Creazione client Modbus TCP ---
client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

try:
    while True:
        # --- Scrittura coil casuale ---
        coil_address = random.randint(1, 5)
        coil_value = random.choice([True, False])
        client.write_coil(coil_address, coil_value, unit=UNIT_ID)
        print(f"[CLIENT-{UNIT_ID}] Scrittura coil {coil_address} = {coil_value}")

        # --- Lettura dello stesso coil ---
        result = client.read_coils(coil_address, 1, unit=UNIT_ID)
        if result.isError():
            print(f"[CLIENT-{UNIT_ID}] Errore nella lettura coil {coil_address}")
        else:
            print(f"[CLIENT-{UNIT_ID}] Lettura coil {coil_address} = {result.bits[0]}")

        # --- Lettura di un holding register casuale ---
        hr_address = random.randint(0, 10)
        result = client.read_holding_registers(hr_address, 1, unit=UNIT_ID)
        if result.isError():
            print(f"[CLIENT-{UNIT_ID}] Errore nella lettura HR {hr_address}")
        else:
            print(f"[CLIENT-{UNIT_ID}] Lettura HR {hr_address} = {result.registers[0]}")

        time.sleep(2)  # pausa tra le richieste

except KeyboardInterrupt:
    print(f"[CLIENT-{UNIT_ID}] Interruzione richiesta dall'utente")

finally:
    client.close()
    print(f"[CLIENT-{UNIT_ID}] Connessione chiusa")
