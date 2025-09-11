#!/usr/bin/env python
import pika, json, logging, sys
from typing import Callable
from configuration.database_configuration import init_driver, close_driver_database
from configuration.device_discovery_publisher import DeviceDiscoveryPublisher
from services.database_service import register_modbus_event


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


publisher = DeviceDiscoveryPublisher(host="localhost", exchange="frontend.events")


# Registry globale degli handler
# Ora ogni handler riceverà anche il driver come secondo argomento
EVENT_HANDLERS: dict[str, Callable[[dict, object], None]] = {}


def register_handler(routing_key: str):
    """Decorator per registrare un handler di eventi."""

    def decorator(func: Callable[[dict, object], None]):
        EVENT_HANDLERS[routing_key] = func
        return func

    return decorator


@register_handler("new_device")
def handle_new_device(event: dict, driver):
    logging.info(f"[Handler] Nuovo device scoperto: {event}")
    try:
        register_modbus_event(event, driver)  # upsert su Neo4j
        # pubblica evento al backend
        publisher.publish({"type": "new_device", "event": event})
    except Exception as e:
        logging.error(f"Errore registrando il device: {e}")


@register_handler("device_update")
def handle_device_update(event: dict, driver):
    logging.info(f"[Handler] Aggiornamento device: {event}")
    try:
        register_modbus_event(event, driver)
        # pubblica evento al backend
        publisher.publish({"type": "device_update", "event": event})
    except Exception as e:
        logging.error(f"Errore aggiornando il device: {e}")


# --- CALLBACK ---
def callback(ch, method, properties, body, driver):
    routing_key = method.routing_key
    event = json.loads(body)
    logging.info(f"[x] Evento ricevuto con routing_key '{routing_key}': {event}")

    handler = EVENT_HANDLERS.get(routing_key)
    if handler:
        handler(event, driver)
    else:
        logging.warning(f"Nessun handler registrato per '{routing_key}'")


# --- MAIN ---
def main():
    # Inizializza Neo4j driver
    driver = init_driver()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    exchange_name = "discovery.events"
    channel.exchange_declare(exchange=exchange_name, exchange_type="direct")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    # Bind dinamico a tutte le routing_key registrate
    for rk in EVENT_HANDLERS.keys():
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=rk)

    logging.info("[*] Waiting for discovery events. To exit press CTRL+C")

    # wrapper per passare il driver agli handler
    on_message = lambda ch, method, properties, body: callback(
        ch, method, properties, body, driver
    )
    channel.basic_consume(
        queue=queue_name, on_message_callback=on_message, auto_ack=True
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info(
            "\n[!] Interruzione richiesta dall'utente. Fermando il consumer ..."
        )
    finally:
        close_driver_database()
        try:
            publisher.close()
        except Exception:
            pass
        try:
            connection.close()
        except Exception:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
