import joblib
import numpy as np
import os
from scapy.all import IP, TCP
import logging

# Configurazione logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)  # due livelli sopra services
ML_MODEL_PATH = os.path.join(
    BASE_DIR, "models", "modbus", "isoforest_modbus_model.joblib"
)
ML_SCALER_PATH = os.path.join(
    BASE_DIR, "models", "modbus", "isoforest_modbus_scaler.joblib"
)
ML_THRESHOLD_PATH = os.path.join(
    BASE_DIR, "models", "modbus", "isoforest_modbus_threshold.txt"
)


class IsolationForestModbusService:
    _instance = None

    def __init__(self, model_path=None, scaler_path=None, threshold_path=None):
        model_path = model_path or ML_MODEL_PATH
        scaler_path = scaler_path or ML_SCALER_PATH
        threshold_path = threshold_path or ML_THRESHOLD_PATH

        logging.info(f"[IsolationForestModbusService] Verifica presenza file:")
        logging.info(f"  Modello: {model_path}")
        logging.info(f"  Scaler: {scaler_path}")
        logging.info(f"  Threshold: {threshold_path}")

        if not all(
            os.path.exists(p) for p in [model_path, scaler_path, threshold_path]
        ):
            missing = [
                p
                for p in [model_path, scaler_path, threshold_path]
                if not os.path.exists(p)
            ]
            logging.error(f"[IsolationForestModbusService] File mancanti: {missing}")
            raise FileNotFoundError("Modello ML o scaler o threshold non trovato")

        logging.info(
            "[IsolationForestModbusService] File trovati, caricamento in corso..."
        )

        self.model = joblib.load(model_path)
        logging.info(f"[IsolationForestModbusService] Modello caricato da {model_path}")

        self.scaler = joblib.load(scaler_path)
        logging.info(f"[IsolationForestModbusService] Scaler caricato da {scaler_path}")

        with open(threshold_path, "r") as f:
            self.threshold = float(f.read().strip())
        logging.info(
            f"[IsolationForestModbusService] Threshold caricato da {threshold_path} -> {self.threshold}"
        )

        # Feature extractor completo basato sulle feature utilizzate in training
        def feature_extractor(parsed_modbus, packet=None):
            pkt_size = len(packet) if packet else 0
            ip_layer = packet[IP] if packet and packet.haslayer(IP) else None
            tcp_layer = packet[TCP] if packet and packet.haslayer(TCP) else None

            ip_ttl = ip_layer.ttl if ip_layer else 0
            ip_len = ip_layer.len if ip_layer else 0
            ip_proto_num = ip_layer.proto if ip_layer else 0
            src_port = tcp_layer.sport if tcp_layer else 0
            dst_port = tcp_layer.dport if tcp_layer else 0
            modbus_function_code = parsed_modbus.get("function_code", 0)
            modbus_data_length = len(parsed_modbus.get("data", b""))

            return np.array(
                [
                    pkt_size,
                    ip_ttl,
                    ip_len,
                    ip_proto_num,
                    src_port,
                    dst_port,
                    modbus_function_code,
                    modbus_data_length,
                ]
            ).reshape(1, -1)

        self.feature_extractor = feature_extractor

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = IsolationForestModbusService()
        return cls._instance

    def check(self, parsed_modbus, packet=None):
        """
        Restituisce (is_normal, score)
        - is_normal: True se il traffico è interpretato come NORMALE (dopo eventuale inversione)
        - score: score grezzo restituito da IsolationForest (decision_function)
        Nota: se la classe ha l'attributo self.inverted_training = True, l'interpretazione finale viene invertita.
        """
        try:
            # --- estrazione feature
            X_feat = self.feature_extractor(parsed_modbus, packet)
            logging.info("[IsolationForestModbusService][CHECK] Feature raw estratte:")
            logging.info(f"  {X_feat.flatten().tolist()}")

            # --- shape / meta
            n_features = X_feat.shape[1] if X_feat.ndim == 2 else X_feat.size
            logging.debug(
                f"[IsolationForestModbusService][CHECK] Numero features attese dal modello: {n_features}"
            )

            # --- scaling
            X_scaled = self.scaler.transform(X_feat)
            logging.info("[IsolationForestModbusService][CHECK] Feature scalate:")
            logging.info(f"  {X_scaled.flatten().tolist()}")

            # --- score da modello
            score = float(self.model.decision_function(X_scaled)[0])
            logging.info(
                f"[IsolationForestModbusService][CHECK] Score grezzo (decision_function): {score}"
            )

            # --- threshold & decisione grezza
            logging.info(
                f"[IsolationForestModbusService][CHECK] Threshold caricato: {self.threshold}"
            )
            model_considers_inlier = score >= self.threshold
            logging.info(
                f"[IsolationForestModbusService][CHECK] Decisione grezza modello: "
                f"{'INLIER (modello => normale)' if model_considers_inlier else 'OUTLIER (modello => anomalia)'}"
            )

            # --- informazioni sul modello (se disponibili)
            try:
                mdl_info = {}
                if hasattr(self.model, "n_estimators"):
                    mdl_info["n_estimators"] = getattr(self.model, "n_estimators")
                if hasattr(self.model, "contamination"):
                    mdl_info["contamination"] = getattr(self.model, "contamination")
                if mdl_info:
                    logging.debug(
                        f"[IsolationForestModbusService][CHECK] Info modello: {mdl_info}"
                    )
            except Exception:
                logging.debug(
                    "[IsolationForestModbusService][CHECK] Non è stato possibile leggere le info del modello"
                )

            # --- inversione training (se presente)
            inverted_flag = getattr(self, "inverted_training", False)
            if inverted_flag:
                logging.warning(
                    "[IsolationForestModbusService][CHECK] ATTENZIONE: il modello è stato allenato/invertito; "
                    "interpreto la decisione del modello in modo INVERTITO per mantenere "
                    "semantica is_normal=True => traffico NORMALE"
                )
            # interpretazione finale: True == normale
            is_normal_final = model_considers_inlier
            if inverted_flag:
                is_normal_final = not model_considers_inlier

            logging.info(
                "[IsolationForestModbusService][CHECK] Interpretazione finale: "
                f"{'NORMALE' if is_normal_final else 'ANOMALO'} (after inversion={inverted_flag})"
            )

            # --- dettagli pacchetto / modbus per debug
            if packet is not None:
                ip_layer = packet[IP] if packet.haslayer(IP) else None
                tcp_layer = packet[TCP] if packet.haslayer(TCP) else None
                logging.info(
                    "[IsolationForestModbusService][CHECK] Dettagli pacchetto:"
                )
                if ip_layer:
                    logging.info(
                        f"  IP src: {ip_layer.src}, dst: {ip_layer.dst}, "
                        f"TTL: {ip_layer.ttl}, Len: {ip_layer.len}, Proto: {ip_layer.proto}"
                    )
                if tcp_layer:
                    logging.info(
                        f"  TCP sport: {tcp_layer.sport}, dport: {tcp_layer.dport}"
                    )

            # --- dettagli parsed_modbus
            try:
                func = parsed_modbus.get("function_code", None)
                data_bytes = parsed_modbus.get("data", b"") or b""
                data_len = len(data_bytes)
                # tronca dati troppo lunghi per i log
                hex_data = data_bytes.hex()
                if len(hex_data) > 200:
                    hex_display = hex_data[:200] + "...(troncato)"
                else:
                    hex_display = hex_data
                logging.info(
                    "[IsolationForestModbusService][CHECK] Dettagli Modbus parsed:"
                )
                logging.info(f"  Function code: {func}")
                logging.info(f"  Data length: {data_len}")
                logging.info(f"  Data (hex, truncated): {hex_display}")
            except Exception:
                logging.debug(
                    "[IsolationForestModbusService][CHECK] Errore nel log dei dettagli Modbus parsed"
                )

            # --- ritorno (manteniamo la signature originale)
            return is_normal_final, score

        except Exception as e:
            # se qualcosa va storto, loggalo e considera l'input come anomalo (policy prudente)
            logging.exception(
                "[IsolationForestModbusService][CHECK] Errore durante il check ML: "
            )
            # ritorna False (anomalo) e score NaN per sicurezza
            return False, float("nan")
