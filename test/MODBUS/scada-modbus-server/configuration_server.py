"""
Configurazioni generali del server
Lettura variabili da .env con fallback
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Host e porta del server
HOST = os.getenv("HOST_SERVER", "127.0.0.1")
PORT = int(os.getenv("HOST_SERVER_PORT", 502))

# Numero di registri simulati
NREG = int(os.getenv("MODBUS_NREG", 200))
