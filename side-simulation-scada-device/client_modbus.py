import time
import random
import os
from dotenv import load_dotenv
from pymodbus.client import ModbusTcpClient

load_dotenv()

# Configurazione server
SERVER_IP = os.getenv("HOST_SERVER_TARGET")
SERVER_PORT = os.getenv("HOST_SERVER_PORT_TARGET")

# Creazione client Modbus TCP
client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

try:
    while True:
        # --- Scrittura coil casuale ---
        coil_address = random.randint(1, 5)  # scegli un coil da 1 a 5
        coil_value = random.choice([True, False])  # valore casuale
        client.write_coil(coil_address, coil_value)
        print(f"[CLIENT] Scrittura coil {coil_address} = {coil_value}")

        # --- Lettura dello stesso coil ---
        result = client.read_coils(coil_address, 1)
        if result.isError():
            print(f"[CLIENT] Errore nella lettura coil {coil_address}")
        else:
            print(f"[CLIENT] Lettura coil {coil_address} = {result.bits[0]}")

        # --- Lettura di un holding register casuale ---
        hr_address = random.randint(0, 10)
        result = client.read_holding_registers(hr_address, 1)
        if result.isError():
            print(f"[CLIENT] Errore nella lettura HR {hr_address}")
        else:
            print(f"[CLIENT] Lettura HR {hr_address} = {result.registers[0]}")

        # Attesa tra le richieste
        time.sleep(2)  # manda pacchetti ogni 2 secondi

except KeyboardInterrupt:
    print("[CLIENT] Interruzione richiesta dall'utente")

finally:
    client.close()
    print("[CLIENT] Connessione chiusa")
