import pika, json


def publish_discovery_event(event: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # Exchange diretto per eventi di discovery
    channel.exchange_declare(exchange="discovery.events", exchange_type="direct")

    # Serializza evento in JSON
    message = json.dumps(event)
    channel.basic_publish(
        exchange="discovery.events", routing_key="new_device", body=message
    )
    print(f"[x] Sent discovery event: {message}")
    connection.close()
