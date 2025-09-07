# --- Mapping client -> Unit ID ---
client_uid_map = {}
used_uids = set()
max_uid = 247  # UID Modbus TCP valido [1-247]


async def get_next_available_uid():
    for uid in range(1, max_uid + 1):
        if uid not in used_uids:
            used_uids.add(uid)
            return uid
    raise RuntimeError("Nessun UID disponibile")


# --- Gestione nuovo client ---
async def client_connected_cb(reader, writer):
    print("[*] ! Client Connected ! [*]")
    addr = writer.get_extra_info("peername")
    print(f"Address  : {addr}")
    if addr not in client_uid_map:
        uid = get_next_available_uid()
        print(f"UID Next : {uid}")
        client_uid_map[addr] = uid
        print(f"[INFO] Nuovo client {addr}, assegnato UID={uid}")
    else:
        uid = client_uid_map[addr]
        print(f"[INFO] Client {addr} già registrato con UID={uid}")

    # Qui puoi gestire eventuali richieste specifiche, logging, ecc.
    # Il resto della comunicazione è gestito da StartTcpServer
