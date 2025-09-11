from datetime import datetime
from configuration.database_configuration import NODE_DEVICE, RELATION_COMMUNICATES_WITH
import json


def register_modbus_event(event: dict, driver):
    """
    Inserisce/aggiorna nodi e relazioni per un evento Modbus.
    :param event: dizionario con i dati Modbus
    :param driver: istanza del driver Neo4j (GraphDatabase.driver)
    """
    if driver is None:
        raise RuntimeError(
            "Neo4j driver non inizializzato. Passa il driver come argomento."
        )

    with driver.session() as session:
        session.write_transaction(_upsert_event, event)


def _upsert_event(tx, event: dict):
    now = datetime.utcnow().isoformat()

    src_role = "client" if event["src_port"] != 502 else "slave"
    dst_role = "client" if event["dst_port"] != 502 else "slave"
    protocol = event.get("protocol", "Modbus")

    src_display = f"{src_role}:{event['src_port']}:{event['src_ip']}"
    dst_display = f"{dst_role}:{event['dst_port']}:{event['dst_ip']}"

    tx.run(
        f"""
        MERGE (c:{NODE_DEVICE} {{ip:$src_ip, port:$src_port}})
          ON CREATE SET c.first_seen = $now, c.role = $src_role, c.display_name = $src_display
          ON MATCH  SET c.last_seen = $now, c.role = $src_role, c.display_name = $src_display

        MERGE (s:{NODE_DEVICE} {{ip:$dst_ip, port:$dst_port}})
          ON CREATE SET s.first_seen = $now, s.role = $dst_role, s.display_name = $dst_display
          ON MATCH  SET s.last_seen = $now, s.role = $dst_role, s.display_name = $dst_display

        // Relazione c -> s
        MERGE (c)-[r1:{RELATION_COMMUNICATES_WITH} {{protocol:$protocol}}]->(s)
          ON CREATE SET r1.first_seen = $now, r1.count = 1
          ON MATCH  SET r1.last_seen = $now, r1.count = r1.count + 1

        // Relazione s -> c (bidirezionale)
        MERGE (s)-[r2:{RELATION_COMMUNICATES_WITH} {{protocol:$protocol}}]->(c)
          ON CREATE SET r2.first_seen = $now, r2.count = 1
          ON MATCH  SET r2.last_seen = $now, r2.count = r2.count + 1
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
