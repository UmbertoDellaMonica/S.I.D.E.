#!/usr/bin/env python
import pika
import json
import logging
import sys
from typing import Callable

# Import delle configurazioni e dei servizi
from configuration.database_configuration import init_driver, close_driver_database
from configuration.device_discovery_publisher import (
    DeviceDiscoveryPublisher,
    AlertPublisher,
)
from services.database_service import (
    register_device_event,
)  # ✅ usa la funzione generica


# ---------------------------------------------------------------------------
# CONFIGURAZIONE DEL LOGGING
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


# ---------------------------------------------------------------------------
# INIZIALIZZAZIONE DEL PUBLISHER
# ---------------------------------------------------------------------------
# Il publisher invia eventi verso l’exchange “frontend.events”,
# usato per aggiornare l’interfaccia o altri moduli backend.
publisher = DeviceDiscoveryPublisher(host="localhost", exchange="frontend.events")
# ---------------------------------------------------------------------------
# INIZIALIZZAZIONE DELL' ALERT PUBLISHER
# ---------------------------------------------------------------------------
# Il publisher invia eventi verso l’exchange “frontend.events”,
# usato per aggiornare l’interfaccia o altri moduli backend.
alert_publisher = AlertPublisher(host="localhost", exchange="frontend.alerts")


# ---------------------------------------------------------------------------
# REGISTRO DEGLI HANDLER
# ---------------------------------------------------------------------------
EVENT_HANDLERS: dict[str, Callable[[dict, object], None]] = {}


# ---------------------------------------------------------------------------
# DECORATOR PER REGISTRARE GLI HANDLER
# ---------------------------------------------------------------------------
def register_handler(routing_key: str):
    """
    Permette di registrare una funzione come gestore di una routing_key RabbitMQ.
    Esempio:
        @register_handler("new_device")
        def handle_new_device(event, driver): ...
    """

    def decorator(func: Callable[[dict, object], None]):
        EVENT_HANDLERS[routing_key] = func
        return func

    return decorator


# ---------------------------------------------------------------------------
# HANDLER: NEW_DEVICE
# ---------------------------------------------------------------------------
@register_handler("new_device")
def handle_new_device(event: dict, driver):
    logging.info(f"[Handler] Nuovo device scoperto: {event}")
    try:
        register_device_event(event, driver)
        publisher.publish({"type": "new_device", "event": event})
        logging.info("[Handler] Device registrato correttamente in Neo4j.")

        # ✅ Se è presente un'anomalia, invia alert
        if event.get("anomaly") is not None:
            alert_publisher.publish(
                {
                    "type": "alert",
                    "level": "warning",
                    "message": f"Anomalia rilevata nel nuovo device: {event['anomaly']}",
                    "device": event.get("src_ip", event.get("device_id", "unknown")),
                    "protocol": event.get("protocol"),
                }
            )

    except Exception as e:
        logging.error(f"Errore durante la registrazione del device: {e}")
        alert_publisher.publish(
            {
                "type": "alert",
                "level": "error",
                "message": f"Errore durante la registrazione del device: {e}",
                "device": event.get("src_ip", event.get("device_id", "unknown")),
            }
        )


# ---------------------------------------------------------------------------
# HANDLER: DEVICE_UPDATE
# ---------------------------------------------------------------------------
@register_handler("device_update")
def handle_device_update(event: dict, driver):
    logging.info(f"[Handler] Aggiornamento device: {event}")
    try:
        register_device_event(event, driver)
        publisher.publish({"type": "device_update", "event": event})
        logging.info("[Handler] Device aggiornato correttamente in Neo4j.")

        # ✅ Se è presente un'anomalia, invia alert
        if event.get("anomaly") is not None:
            alert_publisher.publish(
                {
                    "type": "alert",
                    "level": "warning",
                    "message": f"Anomalia rilevata durante l’aggiornamento: {event['anomaly']}",
                    "device": event.get("src_ip", event.get("device_id", "unknown")),
                    "protocol": event.get("protocol"),
                }
            )

    except Exception as e:
        logging.error(f"Errore durante l’aggiornamento del device: {e}")
        alert_publisher.publish(
            {
                "type": "alert",
                "level": "error",
                "message": f"Errore durante l’aggiornamento del device: {e}",
                "device": event.get("src_ip", event.get("device_id", "unknown")),
            }
        )


# ---------------------------------------------------------------------------
# CALLBACK DI CONSUMO
# ---------------------------------------------------------------------------
def callback(ch, method, properties, body, driver):
    """
    Eseguita automaticamente all’arrivo di un messaggio su RabbitMQ.
    - Identifica la routing_key
    - Decodifica il JSON del messaggio
    - Chiama il relativo handler registrato
    """
    routing_key = method.routing_key
    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        logging.error("Messaggio ricevuto non è un JSON valido.")
        return

    logging.info(f"[x] Evento ricevuto con routing_key '{routing_key}': {event}")

    handler = EVENT_HANDLERS.get(routing_key)
    if handler:
        handler(event, driver)
    else:
        logging.warning(f"Nessun handler registrato per '{routing_key}'")


# ---------------------------------------------------------------------------
# MAIN: AVVIO DEL CONSUMER
# ---------------------------------------------------------------------------
def main():
    # Connessione al database Neo4j
    driver = init_driver()

    # Connessione a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    exchange_name = "discovery.events"
    channel.exchange_declare(exchange=exchange_name, exchange_type="direct")

    # Crea una coda temporanea (verrà rimossa alla chiusura)
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    # Bind automatico per tutte le routing key registrate
    for rk in EVENT_HANDLERS.keys():
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=rk)

    logging.info(
        "[*] In attesa di eventi da 'discovery.events'. Premere CTRL+C per uscire."
    )

    # Passa il driver agli handler tramite lambda
    on_message = lambda ch, method, properties, body: callback(
        ch, method, properties, body, driver
    )

    channel.basic_consume(
        queue=queue_name, on_message_callback=on_message, auto_ack=True
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("\n[!] Interruzione manuale ricevuta. Arresto del consumer...")
    finally:
        # Chiusura risorse
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


# ---------------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
