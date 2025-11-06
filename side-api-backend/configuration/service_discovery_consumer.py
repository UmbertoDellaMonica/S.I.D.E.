import json
import pika
import threading
import asyncio
from configuration.websocket_manager import ws_manager


def rabbitmq_consumer_thread():
    """
    Thread separato che riceve eventi RabbitMQ e li inoltra ai WebSocket client.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    exchange_name = "frontend.events"
    channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print("[*] RabbitMQ consumer pronto a ricevere eventi...")

    # 🔹 Crea un event loop DEDICATO a questo thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def callback(ch, method, properties, body):
        try:
            event = json.loads(body)
            print(f"[x] Evento ricevuto dal consumer: {event}")

            # 🔹 Usa run_coroutine_threadsafe per eseguire la coroutine nel loop del thread
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast(event), loop)
        except Exception as e:
            print(f"[!] Errore durante l'invio evento WebSocket: {e}")

    # 🔹 Avvia il loop asincrono in background
    def start_loop():
        print("[*] Avvio event loop asincrono del consumer...")
        loop.run_forever()

    threading.Thread(target=start_loop, daemon=True).start()

    # 🔹 Avvia il consumer RabbitMQ (bloccante, ma in thread separato)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def start_rabbitmq_consumer():
    """
    Avvia il consumer in un thread separato per non bloccare FastAPI.
    """
    print("[DEBUG] Avvio consumer RabbitMQ...")
    thread = threading.Thread(target=rabbitmq_consumer_thread, daemon=True)
    thread.start()
    print("[DEBUG] Thread consumer RabbitMQ avviato.")
