def parse_opcua_payload(payload: bytes) -> dict | None:
    """
    Parsing minimale OPC UA TCP Binary
    - TPKT Header: 4 bytes
    - UA Header: MessageType (3 char) + ChunkType (1 char)
    - Restituisce anche il payload in formato esadecimale JSON-serializzabile
    """
    if len(payload) < 8:  # TPKT + UA header minimo
        return None

    # TPKT header: versione, reserved, length (big endian)
    version = payload[0]
    length = int.from_bytes(payload[2:4], byteorder="big")

    # UA Binary message header
    message_type = payload[4:7].decode(
        "ascii", errors="replace"
    )  # e.g., 'MSG', 'OPN', 'CLO'
    chunk_type = payload[7:8].decode(
        "ascii", errors="replace"
    )  # 'F'=Final, 'A'=Intermediate

    # Campi opzionali: SecureChannelId, SequenceNumber, RequestId
    secure_channel_id = (
        int.from_bytes(payload[8:12], "little") if len(payload) >= 12 else None
    )
    sequence_number = (
        int.from_bytes(payload[12:16], "little") if len(payload) >= 16 else None
    )
    request_id = (
        int.from_bytes(payload[16:20], "little") if len(payload) >= 20 else None
    )

    # Payload dati veri e propri
    raw_data = payload[20:] if len(payload) > 20 else b""

    # Conversione in stringa esadecimale JSON-serializzabile
    payload_data_serializable = raw_data.hex() if raw_data else None

    return {
        "message_type": message_type,
        "chunk_type": chunk_type,
        "secure_channel_id": secure_channel_id,
        "sequence_number": sequence_number,
        "request_id": request_id,
        "payload_data": payload_data_serializable,  # già serializzabile
    }
