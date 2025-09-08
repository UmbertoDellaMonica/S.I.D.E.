#!/usr/bin/env python
import pika, json, sys, os, logging
from typing import Callable

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# Registry globale degli handler
EVENT_HANDLERS: dict[str, Callable[[dict], None]] = {}


def register_handler(routing_key: str):
    """Decorator per registrare un handler di eventi."""

    def decorator(func: Callable[[dict], None]):
        EVENT_HANDLERS[routing_key] = func
        return func

    return decorator


@register_handler("new_device")
def handle_new_device(event: dict):
    logging.info(f"[Handler] Nuovo device scoperto: {event}")
    # update_device_map(event)  # esempio di chiamata a Neo4j


@register_handler("device_update")
def handle_device_update(event: dict):
    logging.info(f"[Handler] Aggiornamento device: {event}")
    # update_device_map(event)


def callback(ch, method, properties, body):
    routing_key = method.routing_key
    event = json.loads(body)
    logging.info(f"[x] Evento ricevuto con routing_key '{routing_key}': {event}")

    handler = EVENT_HANDLERS.get(routing_key)
    if handler:
        handler(event)
    else:
        logging.warning(f"Nessun handler registrato per '{routing_key}'")


def main():
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
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("\n[!] Interruzione richiesta dall'utente. Fermando il broker ...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":
    main()
