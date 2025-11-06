# rabbitmq_publisher.py
import pika
import json


class DeviceDiscoveryPublisher:
    def __init__(self, host="localhost", exchange="frontend.events"):
        self.exchange = exchange
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type="fanout")

    def publish(self, message: dict):
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key="",  # fanout non usa routing key
            body=json.dumps(message),
        )

    def close(self):
        self.connection.close()


class AlertPublisher:
    def __init__(self, host="localhost", exchange="frontend.alerts"):
        self.exchange = exchange
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type="fanout")

    def publish(self, alert: dict):
        """Invia un messaggio di alert o anomalia"""
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key="",
            body=json.dumps(alert),
        )

    def close(self):
        self.connection.close()
