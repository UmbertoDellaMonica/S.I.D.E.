"""
Funzioni di logging personalizzato per richieste Modbus
"""


def log_request(request):
    """
    Stampa informazioni dettagliate sulla richiesta Modbus.
    """
    try:
        func_name = type(request).__name__
        addr = getattr(request, "address", None)
        count = getattr(request, "count", None)
        value = getattr(request, "value", None)

        print(
            f"[SERVER] Funzione: {func_name} | Address: {addr} | Count: {count} | Value: {value}"
        )
    except Exception as e:
        print(f"[SERVER] Logging richiesta fallito: {e}")
    return request
