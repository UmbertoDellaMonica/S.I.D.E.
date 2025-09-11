# background_consumer.py
import json
import pika
import asyncio
from configuration.websocket_manager import ws_manager  # il manager che gestisce i WS


def start_rabbitmq_consumer():
    """
    Avvia un consumer RabbitMQ che riceve eventi da ServiceDiscovery
    e li inoltra al WebSocket manager.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # Exchange dove ServiceDiscovery pubblica eventi
    exchange_name = "frontend.events"
    channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")

    # Creazione di una coda esclusiva temporanea
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    # Bind alla coda dell'exchange
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print("[*] RabbitMQ consumer pronto a ricevere eventi...")

    def callback(ch, method, properties, body):
        event = json.loads(body)
        print(f"[x] Evento ricevuto dal consumer: {event}")

        # Inoltra al WebSocket manager in modo asincrono
        try:
            asyncio.run(ws_manager.broadcast(event))
        except Exception as e:
            print(f"[!] Errore inviando evento al WebSocket: {e}")

    # Consuma i messaggi
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
