from scapy.all import TCP, IP, Raw
from configuration.side_sniffer_configuration import MODBUS_PORT, S7_PORT, OPCUA_PORT
from decoder.modbus_decoder import parse_modbus_payload
from decoder.s7_decoder import parse_s7_payload
from decoder.opcua_decoder import parse_opcua_payload
from discovery.side_sniffer_discovery import publish_discovery_event
from services.side_sniff_zscore_service import ZScoreService
from services.side_sniff_ml_service import IsolationForestModbusService
from datetime import datetime


def build_event(
    protocol: str,
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    payload: dict,
    anomaly: str | None = None,
) -> dict:
    """Crea un dizionario evento standardizzato da inviare al Consumer."""
    return {
        "protocol": protocol,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
        "anomaly": anomaly,
    }


# -----------------------------
# HANDLER MODBUS
# -----------------------------
def modbus_packet_handler(packet, publish_event=publish_discovery_event):
    try:
        if not (packet.haslayer(TCP) and packet.haslayer(IP)):
            return

        tcp_layer, ip_layer = packet[TCP], packet[IP]
        if tcp_layer.sport != MODBUS_PORT and tcp_layer.dport != MODBUS_PORT:
            return

        info = f"{ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport}"

        if not packet.haslayer(Raw):
            print(f"[MODBUS] {info} | Nessun payload")
            return

        payload = packet[Raw].load
        parsed = parse_modbus_payload(payload)
        if not parsed:
            print(f"[MODBUS] {info} | Payload troppo corto ({len(payload)}B)")
            return

        # --- Stampa pacchetto --- #
        if parsed.get("exception"):
            print(
                f"[MODBUS-EXC] {info} | "
                f"TID={parsed['transaction_id']} | UID={parsed['unit_id']} | "
                f"FC=0x{parsed['function_code']:02X} | Exception={parsed['exception_code']} ({parsed['exception_message']})"
            )
        else:
            print(
                f"[MODBUS] {info} | TID={parsed['transaction_id']} | UID={parsed['unit_id']} | "
                f"FC={parsed['function_code']} ({parsed.get('function_name')}) | Data={parsed['data'].hex()}"
            )

        # --- Evento base (sempre inviato) --- #
        payload_dict = {
            "transaction_id": parsed["transaction_id"],
            "unit_id": parsed["unit_id"],
            "function_code": parsed["function_code"],
            "function_name": parsed.get("function_name"),
            "exception": parsed.get("exception"),
            "data": (
                parsed.get("data").hex()
                if isinstance(parsed.get("data"), (bytes, bytearray))
                else None
            ),
        }

        base_event = build_event(
            "Modbus",
            ip_layer.src,
            ip_layer.dst,
            tcp_layer.sport,
            tcp_layer.dport,
            payload_dict,
            anomaly="NORMAL_ACTIVITY",
        )
        publish_event(base_event)

        # --- Inizializzazione servizi --- #
        zscore_service = ZScoreService.get_instance()
        ml_service = IsolationForestModbusService.get_instance()

        features = {
            "function_code": parsed.get("function_code", 0),
            "data_length": len(parsed.get("data", b"")),
        }

        # --- 1. Controllo Early Warning (Z-SCORE) --- #
        zscore_anomaly, zscore_msg = zscore_service.check(
            device_id=ip_layer.src,
            protocol="Modbus",
            features=features,
            update_dynamic=True,
        )

        if not zscore_anomaly:
            print(f"[INFO][Z-SCORE] Pacchetto legittimo | Device={ip_layer.src}")
            return  # nessuna anomalia, quindi fine

        # Se è attiva la condizione early warning
        print(f"[EARLY-WARNING][Z-SCORE] {zscore_msg} | Device={ip_layer.src}")
        early_event = build_event(
            "Modbus",
            ip_layer.src,
            ip_layer.dst,
            tcp_layer.sport,
            tcp_layer.dport,
            payload_dict,
            anomaly="EARLY_WARNING_ZSCORE",
        )
        publish_event(early_event)

        # --- 2. Verifica Anomalia (ML) --- #
        ml_anomaly, ml_score = ml_service.check(parsed_modbus=parsed, packet=packet)

        if ml_anomaly:
            print(f"[ANOMALY][ML] Pacchetto anomalo | Score={ml_score:.4f}")
            anomaly_event = build_event(
                "Modbus",
                ip_layer.src,
                ip_layer.dst,
                tcp_layer.sport,
                tcp_layer.dport,
                payload_dict,
                anomaly="CONFIRMED_ANOMALY_ML",
            )
            publish_event(anomaly_event)
        else:
            print(f"[INFO][ML] Pacchetto legittimo | Score={ml_score:.4f}")

    except Exception as e:
        print(f"[ERROR][Modbus Handler] {e}")


# -----------------------------
# HANDLER S7 (con Z-Score + ML)
# -----------------------------
def s7_packet_handler(packet):
    try:
        if not (packet.haslayer(TCP) and packet.haslayer(IP)):
            return

        tcp_layer, ip_layer = packet[TCP], packet[IP]
        if tcp_layer.sport != S7_PORT and tcp_layer.dport != S7_PORT:
            return
        if not packet.haslayer(Raw):
            return

        payload = packet[Raw].load
        parsed = parse_s7_payload(payload)
        if not parsed:
            print(f"[S7] Payload troppo corto ({len(payload)}B)")
            return

        # --- Estrazione campi utili --- #
        job_function = parsed.get("job_function")
        job_function_name = parsed.get("job_function_name", "Unknown")
        area_name = parsed.get("area_name", "N/A")
        db_number = parsed.get("db_number", "N/A")
        data = parsed.get("data")
        data_ascii = data.decode("ascii", errors="replace") if data else "N/A"

        # --- Creazione payload --- #
        payload_dict = {
            "job_function": job_function,
            "job_function_name": job_function_name,
            "area_name": area_name,
            "db_number": db_number,
            "data": data_ascii,
            "parameter_length": parsed.get("parameter_length", 0),
            "data_length": parsed.get("data_length", 0),
        }

        # --- Evento base (discovery) --- #
        base_event = build_event(
            "S7",
            ip_layer.src,
            ip_layer.dst,
            tcp_layer.sport,
            tcp_layer.dport,
            payload_dict,
            anomaly="NORMAL_ACTIVITY",
        )
        publish_discovery_event(base_event)

        # --- Servizi di analisi --- #
        zscore_service = ZScoreService.get_instance()
        # ml_service = IsolationForestS7Service.get_instance()

        features = {
            "job_function": job_function or 0,
            "data_length": parsed.get("data_length", 0),
            "parameter_length": parsed.get("parameter_length", 0),
        }

        # --- 1. Controllo Early Warning (Z-Score) --- #
        zscore_anomaly, zscore_reason = zscore_service.check(
            ip_layer.src, "S7", features, update_dynamic=True
        )

        if zscore_anomaly:
            print(f"[EARLY-WARNING][Z-SCORE] {zscore_reason} | Device={ip_layer.src}")
            zscore_event = build_event(
                "S7",
                ip_layer.src,
                ip_layer.dst,
                tcp_layer.sport,
                tcp_layer.dport,
                payload_dict,
                anomaly="EARLY_WARNING_ZSCORE",
            )
            publish_discovery_event(zscore_event)

        # --- 2. Controllo Anomalia (ML) --- #
        """ml_anomaly, ml_score = ml_service.check(parsed_s7=parsed, packet=packet)

        if ml_anomaly:
            print(f"[ANOMALY][ML] Rilevata anomalia | Score={ml_score:.4f}")
            anomaly_event = build_event(
                "S7",
                ip_layer.src,
                ip_layer.dst,
                tcp_layer.sport,
                tcp_layer.dport,
                payload_dict,
                anomaly="CONFIRMED_ANOMALY_ML",
            )
            publish_discovery_event(anomaly_event)
        else:
            print(f"[INFO][ML] Pacchetto legittimo | Score={ml_score:.4f}")"""

        # --- Log leggibile --- #
        print(
            f"[S7] {ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport} | "
            f"Job={job_function_name} | Area={area_name} | DB={db_number} | Data='{data_ascii}'"
        )

    except Exception as e:
        print(f"[ERROR][S7 Handler] {e}")


# -----------------------------
# HANDLER OPC-UA
# -----------------------------
def opcua_packet_handler(packet, publish_event=publish_discovery_event):
    try:
        if not (packet.haslayer(TCP) and packet.haslayer(IP)):
            return

        tcp_layer, ip_layer = packet[TCP], packet[IP]
        if tcp_layer.sport != OPCUA_PORT and tcp_layer.dport != OPCUA_PORT:
            return

        if not packet.haslayer(Raw):
            return

        payload = packet[Raw].load
        parsed = parse_opcua_payload(payload)
        if not parsed:
            print(f"[OPC-UA] Payload troppo corto ({len(payload)}B)")
            return

        # Helper conversione sicura
        def safe_int(val, default=0):
            try:
                if isinstance(val, (bytes, bytearray)):
                    return int.from_bytes(val, "big")
                return int(val)
            except Exception:
                return default

        # --- Creazione payload --- #
        payload_dict = {
            "message_type": parsed.get("message_type"),
            "chunk_type": parsed.get("chunk_type"),
            "secure_channel_id": safe_int(parsed.get("secure_channel_id")),
            "sequence_number": safe_int(parsed.get("sequence_number")),
            "request_id": safe_int(parsed.get("request_id")),
            "payload_length": len(payload),
        }

        # --- Evento base (sempre inviato) --- #
        base_event = build_event(
            "OPC-UA",
            ip_layer.src,
            ip_layer.dst,
            tcp_layer.sport,
            tcp_layer.dport,
            payload_dict,
            anomaly="NORMAL_ACTIVITY",
        )
        publish_event(base_event)

        # --- Inizializzazione servizi --- #
        zscore_service = ZScoreService.get_instance()
        #  ml_service = IsolationForestOpcuaService.get_instance()

        features = {"data_length": payload_dict["payload_length"]}

        # --- 1. Controllo Early Warning (Z-SCORE) --- #
        zscore_anomaly, zscore_msg = zscore_service.check(
            device_id=ip_layer.src,
            protocol="OPC-UA",
            features=features,
            update_dynamic=True,
        )

        if not zscore_anomaly:
            print(f"[INFO][Z-SCORE] Pacchetto legittimo | Device={ip_layer.src}")
            return

        # Early Warning attivo
        print(f"[EARLY-WARNING][Z-SCORE] {zscore_msg} | Device={ip_layer.src}")
        early_event = build_event(
            "OPC-UA",
            ip_layer.src,
            ip_layer.dst,
            tcp_layer.sport,
            tcp_layer.dport,
            payload_dict,
            anomaly="EARLY_WARNING_ZSCORE",
        )
        publish_event(early_event)

        """# --- 2. Verifica Anomalia (ML) --- #
        ml_anomaly, ml_score = ml_service.check(parsed_opcua=parsed, packet=packet)

        if ml_anomaly:
            print(f"[ANOMALY][ML] Pacchetto anomalo | Score={ml_score:.4f}")
            anomaly_event = build_event(
                "OPC-UA",
                ip_layer.src,
                ip_layer.dst,
                tcp_layer.sport,
                tcp_layer.dport,
                payload_dict,
                anomaly="CONFIRMED_ANOMALY_ML",
            )
            publish_event(anomaly_event)
        else:
            print(f"[INFO][ML] Pacchetto legittimo | Score={ml_score:.4f}")"""

        # Log finale leggibile
        print(
            f"[OPC-UA] {ip_layer.src}:{tcp_layer.sport} -> {ip_layer.dst}:{tcp_layer.dport} | "
            f"Type={payload_dict['message_type']} | Seq={payload_dict['sequence_number']}"
        )

    except Exception as e:
        print(f"[ERROR][OPC-UA Handler] {e}")
