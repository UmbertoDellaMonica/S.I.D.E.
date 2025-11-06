import time
import random
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

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

# --- Configurazioni simulazione ---
WRITE_COIL_PROB = 0.4
READ_COIL_PROB = 0.3
READ_REG_PROB = 0.3
ERROR_PROB = 0.02
DELAY_PROB = 0.05
DELAY_RANGE = (3, 6)
SLEEP_RANGE = (1.5, 3.5)
MAX_COIL = 10
MAX_REGISTER = 20

try:
    while True:
        # --- Simulazione ritardo casuale ---
        if random.random() < DELAY_PROB:
            delay = random.uniform(*DELAY_RANGE)
            print(
                f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Simulazione ritardo rete: {delay:.2f}s"
            )
            time.sleep(delay)

        # --- Selezione azione ---
        action = random.choices(
            ["write_coil", "read_coil", "read_register"],
            weights=[WRITE_COIL_PROB, READ_COIL_PROB, READ_REG_PROB],
            k=1,
        )[0]

        # --- Esecuzione azione ---
        if action == "write_coil":
            coil_address = random.randint(1, MAX_COIL)
            coil_value = random.choice([True, False])

            # Simula invio malformato con bassa probabilità
            if random.random() < ERROR_PROB:
                coil_address = 9999  # fuori range

            try:
                result = client.write_coil(coil_address, coil_value, unit=UNIT_ID)
                if result.isError():
                    print(
                        f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Errore scrittura coil {coil_address}"
                    )
                else:
                    print(
                        f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Scrittura coil {coil_address} = {coil_value}"
                    )
            except ModbusException as e:
                print(
                    f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Eccezione scrittura coil: {e}"
                )

        elif action == "read_coil":
            coil_address = random.randint(1, MAX_COIL)
            try:
                result = client.read_coils(coil_address, 1, unit=UNIT_ID)
                if result.isError():
                    print(
                        f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Errore lettura coil {coil_address}"
                    )
                else:
                    print(
                        f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Lettura coil {coil_address} = {result.bits[0]}"
                    )
            except ModbusException as e:
                print(
                    f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Eccezione lettura coil: {e}"
                )

        elif action == "read_register":
            hr_address = random.randint(0, MAX_REGISTER)
            try:
                result = client.read_holding_registers(hr_address, 1, unit=UNIT_ID)
                if result.isError():
                    print(
                        f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Errore lettura HR {hr_address}"
                    )
                else:
                    print(
                        f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Lettura HR {hr_address} = {result.registers[0]}"
                    )
            except ModbusException as e:
                print(
                    f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Eccezione lettura HR: {e}"
                )

        # --- Pausa casuale tra le operazioni ---
        time.sleep(random.uniform(*SLEEP_RANGE))

except KeyboardInterrupt:
    print(
        f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Interruzione richiesta dall'utente"
    )

finally:
    client.close()
    print(f"[{datetime.now().isoformat()}][CLIENT-{UNIT_ID}] Connessione chiusa")
