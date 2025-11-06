import asyncio
import logging
import random
from asyncua import Server, ua
from asyncua.common.methods import uamethod

# --- Configurazione logging ---
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger("OPCUA_Server")


# --- Funzioni/metodi server ---
@uamethod
def double_value(parent, value: int) -> int:
    """Esempio di metodo server: raddoppia il valore passato."""
    return value * 2


# --- Configurazione variabili da simulare ---
SIMULATED_VARS = {
    "Temperature": {"min": 20, "max": 100, "value": 25.0},
    "Pressure": {"min": 0, "max": 10, "value": 1.0},
    "Level": {"min": 0, "max": 500, "value": 100.0},
}

UPDATE_INTERVAL = 1.0  # secondi


async def update_variables(var_nodes):
    """
    Aggiorna le variabili del server in maniera realistica e casuale
    """
    while True:
        try:
            for name, node in var_nodes.items():
                # Simula una variazione graduale
                var_info = SIMULATED_VARS[name]
                delta = random.uniform(-1, 1)
                new_value = max(
                    var_info["min"], min(var_info["max"], var_info["value"] + delta)
                )
                var_info["value"] = new_value
                await node.write_value(new_value)
                logger.info(f"[UPDATE] {name} = {new_value:.2f}")
            await asyncio.sleep(UPDATE_INTERVAL)
        except asyncio.CancelledError:
            logger.info("Variable update task cancelled.")
            break
        except Exception as e:
            logger.error(f"Error updating variables: {e}", exc_info=True)
            await asyncio.sleep(0.5)


async def main():
    # --- Setup server OPC-UA ---
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # Namespace personalizzato
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # Popolamento address space
    myobj = await server.nodes.objects.add_object(idx, "MyObject")

    # Variabili scrivibili
    var_nodes = {}
    for var_name, var_info in SIMULATED_VARS.items():
        node = await myobj.add_variable(idx, var_name, var_info["value"])
        await node.set_writable()
        var_nodes[var_name] = node

    # Metodo esposto
    await myobj.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        double_value,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )

    logger.info("OPC-UA Server initialized and starting...")

    # Task di aggiornamento variabili
    async with server:
        update_task = asyncio.create_task(update_variables(var_nodes))
        try:
            # Server rimane attivo
            await update_task
        except asyncio.CancelledError:
            logger.info("Server shutting down...")
        finally:
            update_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server terminated by user (Ctrl+C)")
