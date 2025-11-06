from datetime import datetime
from configuration.database_configuration import NODE_DEVICE, RELATION_COMMUNICATES_WITH
import json


def register_device_event(event: dict, driver):
    """
    Inserisce/aggiorna nodi Device e relazioni CommunicatesWith in modo generico.
    """
    if driver is None:
        raise RuntimeError("Neo4j driver non inizializzato")

    with driver.session() as session:
        session.write_transaction(_upsert_generic, event)


def _upsert_generic(tx, event):
    """
    Inserisce/aggiorna nodi Device e relazioni CommunicatesWith.
    Se l'evento contiene un campo 'anomaly', crea anche un nodo Anomaly
    e lo collega al dispositivo di destinazione (Server o Slave).
    """
    from datetime import datetime
    import json

    now = datetime.utcnow().isoformat()
    protocol = event.get("protocol", "Unknown")

    # Determina i ruoli di sorgente e destinazione in base al protocollo
    src_role = "client"
    dst_role = "server"

    if protocol == "Modbus":
        src_role = "client" if event["src_port"] != 502 else "slave"
        dst_role = "slave" if event["dst_port"] == 502 else "client"
    elif protocol == "S7":
        src_role = "client" if event["src_port"] != 102 else "server"
        dst_role = "server" if event["dst_port"] == 102 else "client"
    elif protocol == "OPC-UA":
        src_role = "client" if event["src_port"] != 4840 else "server"
        dst_role = "server" if event["dst_port"] == 4840 else "client"

    src_display = f"{src_role}:{event['src_port']}:{event['src_ip']}"
    dst_display = f"{dst_role}:{event['dst_port']}:{event['dst_ip']}"

    # --- Inserimento/Aggiornamento dei nodi Device e della relazione COMMUNICATES_WITH ---
    tx.run(
        """
        MERGE (src:Device {ip:$src_ip, port:$src_port})
          ON CREATE SET src.first_seen = $now,
                        src.role = $src_role,
                        src.display_name = $src_display
          ON MATCH  SET src.last_seen = $now,
                        src.role = $src_role,
                        src.display_name = $src_display

        MERGE (dst:Device {ip:$dst_ip, port:$dst_port})
          ON CREATE SET dst.first_seen = $now,
                        dst.role = $dst_role,
                        dst.display_name = $dst_display
          ON MATCH  SET dst.last_seen = $now,
                        dst.role = $dst_role,
                        dst.display_name = $dst_display

        MERGE (src)-[r:COMMUNICATES_WITH {protocol:$protocol}]->(dst)
          ON CREATE SET r.first_seen = $now,
                        r.count = 1
          ON MATCH  SET r.last_seen = $now,
                        r.count = r.count + 1
        """,
        src_ip=event["src_ip"],
        src_port=event["src_port"],
        dst_ip=event["dst_ip"],
        dst_port=event["dst_port"],
        src_role=src_role,
        dst_role=dst_role,
        src_display=src_display,
        dst_display=dst_display,
        protocol=protocol,
        now=now,
    )

    # --- Gestione di eventuali anomalie ---
    if event.get("anomaly"):
        anomaly_id = f"{event['dst_ip']}_{event['timestamp']}_{event['anomaly']}"

        tx.run(
            """
            MERGE (a:Anomaly {id:$anomaly_id})
              ON CREATE SET a.type = $anomaly_type,
                            a.timestamp = $timestamp,
                            a.protocol = $protocol,
                            a.details = $payload,
                            a.src_ip = $src_ip,
                            a.dst_ip = $dst_ip
            WITH a
            MATCH (d:Device {ip:$dst_ip, port:$dst_port})
            MERGE (d)-[:HAS_EVENT]->(a)
            """,
            anomaly_id=anomaly_id,
            anomaly_type=event["anomaly"],
            timestamp=event["timestamp"],
            protocol=event["protocol"],
            payload=json.dumps(event.get("payload", {})),
            src_ip=event["src_ip"],
            dst_ip=event["dst_ip"],
            dst_port=event["dst_port"],
        )

        # Aggiorna anche un contatore di anomalie sul nodo del dispositivo
        tx.run(
            """
            MATCH (d:Device {ip:$dst_ip, port:$dst_port})
            SET d.anomaly_count = coalesce(d.anomaly_count, 0) + 1,
                d.last_anomaly_seen = $timestamp
            """,
            dst_ip=event["dst_ip"],
            dst_port=event["dst_port"],
            timestamp=event["timestamp"],
        )
