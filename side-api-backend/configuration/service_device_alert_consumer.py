import json
import pika
import threading
import asyncio
from configuration.websocket_manager import ws_alert_manager


def rabbitmq_alert_consumer_thread():
    """
    Consumer RabbitMQ dedicato agli alert/anomalie.
    Inoltra i messaggi ai client WebSocket su /ws/alerts.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    exchange_name = "frontend.alerts"
    channel.exchange_declare(exchange=exchange_name, exchange_type="fanout")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print("[*] RabbitMQ consumer ALERT pronto a ricevere eventi...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def callback(ch, method, properties, body):
        try:
            alert = json.loads(body)
            print(f"[x] ALERT ricevuto: {alert}")
            asyncio.run_coroutine_threadsafe(ws_alert_manager.broadcast(alert), loop)
        except Exception as e:
            print(f"[!] Errore durante l'invio ALERT WebSocket: {e}")

    def start_loop():
        print("[*] Avvio event loop asincrono ALERT...")
        loop.run_forever()

    threading.Thread(target=start_loop, daemon=True).start()

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def start_rabbitmq_alert_consumer():
    """Avvia il consumer ALERT in un thread separato"""
    print("[DEBUG] Avvio consumer ALERT RabbitMQ...")
    thread = threading.Thread(target=rabbitmq_alert_consumer_thread, daemon=True)
    thread.start()
    print("[DEBUG] Thread consumer ALERT avviato.")
