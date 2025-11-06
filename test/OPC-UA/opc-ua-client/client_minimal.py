import asyncio
import random
import logging
from asyncua import Client, ua

# --- Configurazione logging ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
logger = logging.getLogger("OPCUA_Client")

# --- Configurazione server ---
URL = "opc.tcp://localhost:4840/freeopcua/server/"
NAMESPACE = "http://examples.freeopcua.github.io"

# --- Parametri di simulazione ---
SIMULATED_VARS = {
    "Temperature": {"min": 20, "max": 100},
    "Pressure": {"min": 0, "max": 10},
    "Level": {"min": 0, "max": 500},
}
METHODS_TO_CALL = [
    {"name": "ServerMethod", "args_range": (0, 10)},
    {"name": "ResetCounter", "args_range": (0, 1)},
]


async def random_read_write(var_node):
    """
    Legge il valore corrente, applica una variazione casuale, scrive il nuovo valore.
    """
    current_value = await var_node.read_value()
    variation = random.uniform(-5, 5)  # variazione casuale
    new_value = current_value + variation

    # Scrittura del nuovo valore
    await var_node.write_value(new_value)
    logger.info(
        f"[VAR] {var_node} | Current={current_value:.2f} -> New={new_value:.2f}"
    )
    return new_value


async def random_method_call(obj_node):
    """
    Chiama un metodo casuale con argomento casuale
    """
    method = random.choice(METHODS_TO_CALL)
    arg = random.randint(*method["args_range"])
    try:
        result = await obj_node.call_method(f"{nsidx}:{method['name']}", arg)
        logger.info(f"[METHOD] {method['name']}({arg}) -> Result={result}")
    except ua.UaStatusCodeError as e:
        logger.warning(f"[METHOD] Failed to call {method['name']}({arg}): {e}")


async def opcua_task():
    """
    Task principale del client OPC-UA
    - Legge/scrive valori casuali
    - Chiama metodi casuali
    - Logga tutte le operazioni
    """
    async with Client(url=URL) as client:
        logger.info(f"Connected to {URL}")

        # Trova namespace index
        global nsidx
        nsidx = await client.get_namespace_index(NAMESPACE)
        logger.info(f"Namespace Index for '{NAMESPACE}': {nsidx}")

        # Recupera nodo root / oggetto principale
        root = client.nodes.root
        objects_node = await root.get_child(f"0:Objects/{nsidx}:MyObject")

        # Recupera nodi variabili
        var_nodes = {}
        for var_name in SIMULATED_VARS.keys():
            try:
                var_nodes[var_name] = await objects_node.get_child(
                    f"{nsidx}:{var_name}"
                )
            except ua.UaError:
                logger.warning(f"Variable {var_name} not found on server")

        # Loop principale
        while True:
            try:
                # Leggi e scrivi valori variabili casuali
                for var_name, node in var_nodes.items():
                    # Simula una probabilità di aggiornamento casuale
                    if random.random() < 0.7:
                        await random_read_write(node)

                # Metodo casuale con probabilità minore
                if random.random() < 0.3:
                    await random_method_call(objects_node)

                await asyncio.sleep(random.uniform(1, 3))  # pausa casuale
            except asyncio.CancelledError:
                logger.info("OPC task cancelled, cleaning up...")
                break
            except Exception as e:
                logger.error(f"OPC-UA error: {e}", exc_info=True)
                await asyncio.sleep(1)  # breve pausa prima del retry


async def main():
    task = asyncio.create_task(opcua_task())
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Main task cancelled")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user (Ctrl+C)")
