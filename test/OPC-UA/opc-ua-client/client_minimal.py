import asyncio
from asyncua import Client

url = "opc.tcp://localhost:4840/freeopcua/server/"
namespace = "http://examples.freeopcua.github.io"


async def opc_task():
    async with Client(url=url) as client:
        print(f"Connected to {url}")

        # Trova namespace index
        nsidx = await client.get_namespace_index(namespace)
        print(f"Namespace Index for '{namespace}': {nsidx}")

        # Variabile da leggere/scrivere
        var = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:MyObject/{nsidx}:MyVariable"
        )

        while True:
            try:
                value = await var.read_value()
                print(f"Current value of MyVariable: {value}")

                new_value = value - 50
                await var.write_value(new_value)
                print(f"New value of MyVariable set to: {new_value}")

                # Esempio di chiamata a metodo
                res = await client.nodes.objects.call_method(f"{nsidx}:ServerMethod", 5)
                print(f"ServerMethod returned: {res}")

                await asyncio.sleep(2)
            except asyncio.CancelledError:
                print("OPC task cancelled, cleaning up...")
                break


async def main():
    task = asyncio.create_task(opc_task())
    try:
        await task
    except asyncio.CancelledError:
        print("Main task cancelled")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user (Ctrl+C)")
