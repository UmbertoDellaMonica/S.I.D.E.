import logging

import snap7
from snap7.type import Areas
from snap7.util import (
    get_bool,
    get_int,
    get_real,
    get_string,
    set_bool,
    set_int,
    set_real,
    set_string,
)
import time

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("s7client")


class S7AdvancedClient:
    def __init__(self, ip="127.0.0.1", rack=0, slot=1, port=102):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.port = port
        self.client = snap7.client.Client()
        self.connected = False

    def connect(self):
        if not self.connected:
            try:
                self.client.connect(self.ip, self.rack, self.slot)
                self.connected = self.client.get_connected()
                log.info(
                    "Connesso al server %s:%s (rack=%s slot=%s)",
                    self.ip,
                    self.port,
                    self.rack,
                    self.slot,
                )
            except Exception as e:
                log.error("Errore connessione: %s", e)
                self.connected = False

    def disconnect(self):
        if self.connected:
            self.client.disconnect()
            self.connected = False
            log.info("Disconnesso dal server")

    # --- DB Operations ---
    def read_db(self, db_number, start, size) -> bytearray:
        self.connect()
        data = self.client.db_read(db_number, start, size)
        log.debug("DB%d read start=%d size=%d -> %s", db_number, start, size, data)
        return data

    def write_db(self, db_number, start, data: bytearray):
        self.connect()
        self.client.db_write(db_number, start, data)
        log.debug(
            "DB%d write start=%d size=%d -> %s", db_number, start, len(data), data
        )

    # --- Helpers for types ---
    def read_int(self, db_number, start):
        data = self.read_db(db_number, start, 2)
        return get_int(data, 0)

    def write_int(self, db_number, start, value):
        buf = bytearray(2)
        set_int(buf, 0, value)
        self.write_db(db_number, start, buf)

    def read_real(self, db_number, start):
        data = self.read_db(db_number, start, 4)
        return get_real(data, 0)

    def write_real(self, db_number, start, value):
        buf = bytearray(4)
        set_real(buf, 0, value)
        self.write_db(db_number, start, buf)

    def read_bool(self, db_number, byte_index, bit_index):
        data = self.read_db(db_number, byte_index, 1)
        return get_bool(data, 0, bit_index)

    def write_bool(self, db_number, byte_index, bit_index, value: bool):
        data = self.read_db(db_number, byte_index, 1)
        set_bool(data, 0, bit_index, value)
        self.write_db(db_number, byte_index, data)

    def read_string(self, db_number, start, length):
        data = self.read_db(db_number, start, length)
        return get_string(data, 0)

    def write_string(self, db_number, start, value, length):
        buf = bytearray(length)
        set_string(buf, 0, value, length)
        self.write_db(db_number, start, buf)

    # --- Area Operations (MK, TM, CT) ---
    def read_area(self, area: Areas, start, size, dbnumber=0):
        self.connect()
        return self.client.read_area(area, dbnumber, start, size)

    def write_area(self, area: Areas, start, data: bytearray, dbnumber=0):
        self.connect()
        self.client.write_area(area, dbnumber, start, data)


# --- Demo di utilizzo in loop infinito ---
if __name__ == "__main__":
    client = S7AdvancedClient(ip="127.0.0.1", rack=0, slot=0, port=102)

    try:
        client.connect()

        counter = 0
        while True:
            # Aggiorna un int
            client.write_int(1, 0, counter)
            val_int = client.read_int(1, 0)

            # Aggiorna un real
            client.write_real(1, 2, counter * 0.1)
            val_real = client.read_real(1, 2)

            # Toggle di un bit
            client.write_bool(1, 0, 0, counter % 2 == 0)
            val_bool = client.read_bool(1, 0, 0)

            # Scrivi una stringa variabile
            msg = f"Valore {counter}"
            client.write_string(1, 4, msg, 20)
            val_str = client.read_string(1, 4, 20)

            print(
                f"Int={val_int}, Real={val_real:.2f}, Bool={val_bool}, String='{val_str}'"
            )

            counter += 1
            time.sleep(1)  # pausa 1 secondo tra un ciclo e l'altro

    except KeyboardInterrupt:
        print("Interrotto dall'utente")

    finally:
        client.disconnect()
