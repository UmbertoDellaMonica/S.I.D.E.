#!/usr/bin/env python3
"""
pcap_to_csv_enhanced.py

Funzionalità:
- scansiona una cartella di .pcap
- estrae campi IP/TCP/UDP/ICMP/ARP e alcuni metadati
- estrae payload Modbus TCP se presente
- costruisce dinamicamente colonne CSV in base ai campi trovati
- permette selezione di colonne (--select)
- genera file di riepilogo (JSON + CSV) con statistiche per feature
- logging estensivo per debug

Esempio:
  export CLEAN_FOLDER_MODBUS="F:/Sample_PCAP_extract/clean"
  python pcap_to_csv_enhanced.py --out "F:/Sample_PCAP_extract/clean_features.csv" --debug

  # selezionare colonne specifiche:
  python pcap_to_csv_enhanced.py --out clean_features.csv --select src_ip,dst_ip,pkt_size,protocol --debug
"""

import os
import argparse
import logging
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

import pandas as pd
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.all import Raw
import struct

# -----------------------
# Config e costanti
# -----------------------
DEFAULT_OUTPUT_SUMMARY_JSON = "features_summary.json"
DEFAULT_OUTPUT_SUMMARY_CSV = "features_summary.csv"
LOG_FILENAME = "pcap_extract.log"

MODBUS_PORT = 502  # TCP Modbus standard

MODBUS_FUNCTIONS = {
    1: "Read Coils",
    2: "Read Discrete Inputs",
    3: "Read Holding Registers",
    4: "Read Input Registers",
    5: "Write Single Coil",
    6: "Write Single Register",
    15: "Write Multiple Coils",
    16: "Write Multiple Registers",
}

MODBUS_EXCEPTIONS = {
    1: "Illegal Function",
    2: "Illegal Data Address",
    3: "Illegal Data Value",
    4: "Slave Device Failure",
    6: "Slave Device Busy",
    10: "Gateway Path Unavailable",
}

load_dotenv()


# -----------------------
# Logging setup
# -----------------------
def configure_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILENAME, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    if not debug:
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


# -----------------------
# Parsing payload Modbus
# -----------------------
def parse_modbus_payload(payload: bytes) -> dict | None:
    if len(payload) < 8:
        return None
    transaction_id, protocol_id, length = struct.unpack(">HHH", payload[:6])
    unit_id = payload[6]
    function_code = payload[7]
    data = payload[8:] if len(payload) > 8 else b""
    parsed = {
        "transaction_id": transaction_id,
        "protocol_id": protocol_id,
        "length": length,
        "unit_id": unit_id,
        "function_code": function_code,
        "data": data,
    }
    if function_code >= 0x80:
        parsed["exception"] = True
        parsed["exception_code"] = data[0] if data else None
        exception_code = parsed.get("exception_code")
        parsed["exception_message"] = MODBUS_EXCEPTIONS.get(
            int(exception_code) if exception_code is not None else None,
            "Unknown Exception",
        )
    else:
        parsed["exception"] = False
        parsed["function_name"] = MODBUS_FUNCTIONS.get(function_code, "Unknown")
    return parsed


# -----------------------
# Packet extraction
# -----------------------
def _get_pkt_metadata(pkt_metadata) -> Dict[str, Any]:
    meta = {"sec": None, "usec": None, "caplen": None}
    try:
        meta["sec"] = getattr(pkt_metadata, "sec", None)
        meta["usec"] = getattr(pkt_metadata, "usec", None)
        caplen = getattr(pkt_metadata, "caplen", None)
        meta["caplen"] = caplen
        if meta["sec"] is None:
            meta["sec"] = pkt_metadata[0]
            meta["usec"] = pkt_metadata[1]
            meta["caplen"] = pkt_metadata[2]
    except Exception:
        logging.exception("Errore leggendo metadata pacchetto")
    return meta


def extract_pcap_to_dict(
    pcap_file: str, detect_modbus_by_port: bool = True
) -> List[Dict[str, Any]]:
    logging.info("Apertura PCAP: %s", pcap_file)
    packets = []
    first_ts = None
    pkt_count = 0
    try:
        for pkt_data, pkt_metadata in RawPcapReader(pcap_file):
            try:
                pkt_count += 1
                ether = Ether(pkt_data)
                meta = _get_pkt_metadata(pkt_metadata)
                sec = meta["sec"] or 0
                usec = meta["usec"] or 0
                caplen = meta["caplen"] or len(pkt_data)
                timestamp = float(sec) + float(usec) / 1_000_000.0
                if first_ts is None:
                    first_ts = timestamp
                rel_ts = round(timestamp - first_ts, 6)

                row: Dict[str, Any] = {
                    "pcap_file": os.path.basename(pcap_file),
                    "timestamp": rel_ts,
                    "pkt_size": caplen,
                }

                # Layers list
                layers = []
                try:
                    p = ether
                    while p:
                        layers.append(p.name)
                        p = p.payload if hasattr(p, "payload") else None
                except Exception:
                    pass
                row["layers"] = "|".join(layers)

                # ARP
                if ARP in ether:
                    arp = ether[ARP]
                    row.update(
                        {
                            "arp_psrc": getattr(arp, "psrc", None),
                            "arp_pdst": getattr(arp, "pdst", None),
                            "arp_hwsrc": getattr(arp, "hwsrc", None),
                            "arp_hwdst": getattr(arp, "hwdst", None),
                            "protocol": "ARP",
                        }
                    )
                    packets.append(row)
                    continue

                # IP
                if IP in ether:
                    ip = ether[IP]
                    row.update(
                        {
                            "src_ip": getattr(ip, "src", None),
                            "dst_ip": getattr(ip, "dst", None),
                            "ip_ttl": getattr(ip, "ttl", None),
                            "ip_len": getattr(ip, "len", None),
                            "ip_proto_num": getattr(ip, "proto", None),
                        }
                    )
                else:
                    packets.append(row)
                    continue

                # ICMP
                if ICMP in ether:
                    icmp = ether[ICMP]
                    row.update(
                        {
                            "protocol": "ICMP",
                            "icmp_type": getattr(icmp, "type", None),
                            "icmp_code": getattr(icmp, "code", None),
                        }
                    )

                # TCP
                if TCP in ether:
                    tcp = ether[TCP]
                    row.update(
                        {
                            "protocol": "TCP",
                            "src_port": getattr(tcp, "sport", None),
                            "dst_port": getattr(tcp, "dport", None),
                            "tcp_flags": str(getattr(tcp, "flags", None)),
                            "tcp_seq": getattr(tcp, "seq", None),
                            "tcp_ack": getattr(tcp, "ack", None),
                            "tcp_win": getattr(tcp, "window", None),
                        }
                    )
                    if detect_modbus_by_port and (
                        row.get("src_port") == MODBUS_PORT
                        or row.get("dst_port") == MODBUS_PORT
                    ):
                        row["likely_modbus"] = True

                    # --- Parsing payload Modbus ---
                    try:
                        if Raw in ether and row.get("likely_modbus"):
                            payload_bytes = ether[Raw].load
                            parsed_modbus = parse_modbus_payload(payload_bytes)
                            if parsed_modbus:
                                row.update(
                                    {
                                        "modbus_transaction_id": parsed_modbus.get(
                                            "transaction_id"
                                        ),
                                        "modbus_unit_id": parsed_modbus.get("unit_id"),
                                        "modbus_function_code": parsed_modbus.get(
                                            "function_code"
                                        ),
                                        "modbus_function_name": parsed_modbus.get(
                                            "function_name"
                                        ),
                                        "modbus_data": (
                                            parsed_modbus.get("data").hex()
                                            if parsed_modbus.get("data") is not None
                                            else None
                                        ),
                                        "modbus_data_length": (
                                            len(parsed_modbus.get("data") or b"")
                                            if parsed_modbus.get("data")
                                            else 0
                                        ),
                                        "modbus_exception": parsed_modbus.get(
                                            "exception"
                                        ),
                                        "modbus_exception_code": parsed_modbus.get(
                                            "exception_code"
                                        ),
                                        "modbus_exception_message": parsed_modbus.get(
                                            "exception_message"
                                        ),
                                    }
                                )
                    except Exception:
                        logging.exception("Errore parsing Modbus payload")

                # UDP
                if UDP in ether:
                    udp = ether[UDP]
                    row.update(
                        {
                            "protocol": "UDP",
                            "src_port": getattr(udp, "sport", None),
                            "dst_port": getattr(udp, "dport", None),
                        }
                    )
                    if detect_modbus_by_port and (
                        row.get("src_port") == MODBUS_PORT
                        or row.get("dst_port") == MODBUS_PORT
                    ):
                        row["likely_modbus"] = True

                # Fallback protocol
                if "protocol" not in row or row["protocol"] is None:
                    proto_num = row.get("ip_proto_num")
                    if proto_num is not None:
                        row["protocol"] = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(
                            proto_num, f"IP_PROTO_{proto_num}"
                        )
                    else:
                        row["protocol"] = "IP_PROTO_UNKNOWN"

                packets.append(row)

            except Exception:
                logging.exception("Errore parsing pacchetto %s", pcap_file)
                continue

    except Exception:
        logging.exception("Errore aprendo pcap %s", pcap_file)

    logging.info("Processed %d packets from %s", pkt_count, pcap_file)
    return packets


# -----------------------
# Process folder -> CSV
# -----------------------
def process_folder_to_csv(
    folder_path: str,
    output_csv: str,
    selected_features: Optional[List[str]] = None,
    summary_json: str = DEFAULT_OUTPUT_SUMMARY_JSON,
    summary_csv: str = DEFAULT_OUTPUT_SUMMARY_CSV,
    max_files: int = 20,  # massimo file da processare
) -> None:
    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder non trovato: {folder_path}")

    all_packets = []
    pcap_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pcap")]
    pcap_files.sort()
    if len(pcap_files) > max_files:
        logging.warning(
            "Trovati %d file, ma ne saranno processati solo i primi %d",
            len(pcap_files),
            max_files,
        )
        pcap_files = pcap_files[:max_files]

    logging.info("Trovati %d file pcap in %s", len(pcap_files), folder_path)
    for file in pcap_files:
        path = os.path.join(folder_path, file)
        try:
            pkt_rows = extract_pcap_to_dict(path)
            all_packets.extend(pkt_rows)
        except Exception:
            logging.exception("Errore processing file %s", path)

    if len(all_packets) == 0:
        logging.warning("Nessun pacchetto estratto. Nessun CSV creato.")
        return

    df = pd.DataFrame(all_packets)
    logging.info("DataFrame creato con shape %s", df.shape)

    # subset colonne
    detected_cols = list(df.columns)
    logging.info("Colonne rilevate: %s", detected_cols)
    mandatory = ["pcap_file", "timestamp", "pkt_size", "src_ip", "dst_ip"]
    if selected_features:
        chosen = [c for c in selected_features if c in detected_cols]
        for m in mandatory:
            if m in detected_cols and m not in chosen:
                chosen.insert(0, m)
        if not chosen:
            chosen = detected_cols
        df = df[chosen]
        logging.info("Selezionate colonne finali: %s", list(df.columns))

    df.to_csv(output_csv, index=False)
    logging.info(
        "CSV scritto: %s (righe %d, colonne %d)", output_csv, len(df), len(df.columns)
    )

    # summary JSON + CSV
    summary = {}
    for col in df.columns:
        ser = df[col]
        non_null = ser.dropna()
        cnt = len(ser)
        non_null_cnt = len(non_null)
        unique = non_null.nunique(dropna=True)
        top_vals = None
        if non_null_cnt > 0:
            try:
                top_vals = non_null.value_counts().head(5).to_dict()
            except Exception:
                top_vals = None
            if pd.api.types.is_numeric_dtype(non_null):
                try:
                    summary[col] = {
                        "non_null_count": non_null_cnt,
                        "unique": unique,
                        "top_values": top_vals,
                        "min": float(non_null.min()),
                        "max": float(non_null.max()),
                        "mean": float(non_null.mean()),
                    }
                except Exception:
                    summary[col] = {
                        "non_null_count": non_null_cnt,
                        "unique": unique,
                        "top_values": top_vals,
                    }
            else:
                summary[col] = {
                    "non_null_count": non_null_cnt,
                    "unique": unique,
                    "top_values": top_vals,
                }
        else:
            summary[col] = {
                "non_null_count": non_null_cnt,
                "unique": unique,
                "top_values": top_vals,
            }

    with open(summary_json, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    logging.info("Summary JSON scritto: %s", summary_json)

    rows = []
    for k, v in summary.items():
        row = {
            "column": k,
            "non_null_count": v.get("non_null_count", 0),
            "unique": v.get("unique", 0),
            "top_values": json.dumps(v.get("top_values", {}), ensure_ascii=False),
            "min": v.get("min", None),
            "max": v.get("max", None),
            "mean": v.get("mean", None),
        }
        rows.append(row)
    pd.DataFrame(rows).to_csv(summary_csv, index=False)
    logging.info("Summary CSV scritto: %s", summary_csv)
    logging.debug("Preview DataFrame (top 10):\n%s", df.head(10).to_string())


# -----------------------
# CLI
# -----------------------
def _parse_args():
    parser = argparse.ArgumentParser(
        description="PCAP -> CSV extractor con feature discovery e Modbus parsing"
    )
    parser.add_argument(
        "--folder",
        "-f",
        required=False,
        help="Cartella contenente i pcap (usa env CLEAN_FOLDER_MODBUS se omesso)",
    )
    parser.add_argument("--out", "-o", required=True, help="CSV di output")
    parser.add_argument(
        "--select", "-s", required=False, help="Colonne da includere (csv)"
    )
    parser.add_argument("--summary-json", default=DEFAULT_OUTPUT_SUMMARY_JSON)
    parser.add_argument("--summary-csv", default=DEFAULT_OUTPUT_SUMMARY_CSV)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--num-file",
        "-n",
        help="Inserisci il numero di file da recuperare per tipo di folder ",
        required=False,
        default=3,
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    configure_logging(args.debug)
    folder = args.folder or os.getenv("CLEAN_FOLDER_MODBUS")
    if not folder:
        logging.error("Nessuna cartella pcap specificata.")
        return
    selected = [s.strip() for s in args.select.split(",")] if args.select else None
    logging.info("Start processing folder=%s out=%s", folder, args.out)
    process_folder_to_csv(
        folder,
        args.out,
        selected_features=selected,
        summary_json=args.summary_json,
        summary_csv=args.summary_csv,
    )
    logging.info("Done. Log: %s", LOG_FILENAME)


if __name__ == "__main__":
    main()
