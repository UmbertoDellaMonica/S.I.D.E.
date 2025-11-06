from configuration.database_configuration import driver

from fastapi import APIRouter, Depends, Query
from services.database_service import get_devices
from datetime import datetime, timedelta


router = APIRouter()


def get_db_driver():
    from configuration.database_configuration import driver

    if driver is None:
        raise RuntimeError("Neo4j driver not initialized")
    return driver


@router.get("/api/devices")
def handle_get_device_controller(driver=Depends(get_db_driver)):
    return get_devices(driver=driver)


@router.get("/api/devices/filter")
def handle_get_devices_by_protocol(
    protocol: str = Query(None, description="Filtra i dispositivi per protocollo"),
    driver=Depends(get_db_driver),
):
    """
    Recupera tutti i dispositivi presenti nel grafo, filtrando (opzionalmente) per protocollo.

    ✅ Considera entrambe le direzioni della relazione COMMUNICATES_WITH.
    ✅ Calcola lo stato 'active' / 'inactive' in base a last_seen (≤ 2 ore).
    ✅ Evita duplicati basandosi su display_name.
    """

    with driver.session() as session:
        query = """
        MATCH (d:Device)
        WHERE $protocol IS NULL 
           OR EXISTS {
                MATCH (d)-[r:COMMUNICATES_WITH]-()
                WHERE r.protocol = $protocol
           }
        RETURN DISTINCT d
        """

        result = session.run(query, protocol=protocol)

        devices = []
        for record in result:
            n = record["d"]
            last_seen_str = n.get("last_seen")
            last_seen = None

            # Conversione last_seen in datetime (se è una stringa ISO)
            if isinstance(last_seen_str, str):
                try:
                    last_seen = datetime.fromisoformat(last_seen_str)
                except ValueError:
                    last_seen = None
            elif isinstance(last_seen_str, datetime):
                last_seen = last_seen_str

            # Calcolo dello stato del dispositivo
            status = (
                "active"
                if last_seen and (datetime.utcnow() - last_seen).total_seconds() <= 200
                else "inactive"
            )

            devices.append(
                {
                    "id": n.element_id,
                    "ip": n.get("ip"),
                    "port": n.get("port"),
                    "role": n.get("role"),
                    "display_name": n.get("display_name"),
                    "first_seen": n.get("first_seen"),
                    "last_seen": n.get("last_seen"),
                    "protocol": n.get("protocol"),
                    "status": status,
                }
            )

    # Deduplica per display_name (nel caso più nodi identici)
    unique_devices = {d["display_name"]: d for d in devices}.values()

    return {"devices": list(unique_devices)}


@router.get("/api/alerts")
def handle_get_all_alerts(driver=Depends(get_db_driver)):
    """
    Recupera tutte le anomalie presenti nel grafo Neo4j.

    ✅ Collega ciascuna anomalia al dispositivo associato.
    ✅ Ordina per timestamp decrescente.
    ✅ Ritorna struttura coerente con le altre API del backend.
    """

    with driver.session() as session:
        query = """
        MATCH (a:Anomaly)<-[:HAS_EVENT]-(d:Device)
        RETURN 
            a.id AS id,
            a.type AS type,
            a.timestamp AS timestamp,
            a.protocol AS protocol,
            a.details AS details,
            d.ip AS device_ip,
            d.role AS device_role,
            d.display_name AS device_display_name
        ORDER BY a.timestamp DESC
        """

        result = session.run(query)
        alerts = []
        for record in result:
            timestamp = record["timestamp"]

            # Conversione in datetime leggibile (ISO 8601 → stringa)
            if isinstance(timestamp, datetime):
                timestamp_str = timestamp.isoformat()
            else:
                timestamp_str = str(timestamp)

            alerts.append(
                {
                    "id": record["id"],
                    "type": record["type"],
                    "protocol": record["protocol"],
                    "timestamp": timestamp_str,
                    "details": record["details"],
                    "device": {
                        "ip": record["device_ip"],
                        "role": record["device_role"],
                        "display_name": record.get("device_display_name"),
                    },
                }
            )

    return {"alerts": alerts}
