import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

# --- CONFIGURAZIONE --- #

load_dotenv()


URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")  # default se non trovato
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


driver = None


def init_driver():
    global driver
    if driver is None:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        print("✅ Neo4j driver inizializzato")
    return driver


def close_driver_database():
    global driver
    if driver is not None:
        driver.close()
        driver = None
        print("🛑 Neo4j driver chiuso")


class SideDatabaseConfiguration:
    """
    Classe di configurazione per l'applicazione Neo4j-Excel.
    Contiene attributi di connessione e percorso file con metodi getter e setter.
    """

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "standards",
    ):
        self._neo4j_uri = neo4j_uri
        self._neo4j_user = neo4j_user
        self._neo4j_password = neo4j_password

    # Getter

    # Get the driver of Database
    def get_driver(self):
        return GraphDatabase.driver(
            self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
        )

    @property
    def neo4j_uri(self) -> str:
        return self._neo4j_uri

    @property
    def neo4j_user(self) -> str:
        return self._neo4j_user

    @property
    def neo4j_password(self) -> str:
        return self._neo4j_password

    # Setter

    @neo4j_uri.setter
    def neo4j_uri(self, value: str):
        if not isinstance(value, str) or not value.startswith("bolt://"):
            raise ValueError("neo4j_uri must be a valid Bolt URI string")
        self._neo4j_uri = value

    @neo4j_user.setter
    def neo4j_user(self, value: str):
        if not isinstance(value, str) or not value:
            raise ValueError("neo4j_user must be a non-empty string")
        self._neo4j_user = value

    @neo4j_password.setter
    def neo4j_password(self, value: str):
        if not isinstance(value, str):
            raise ValueError("neo4j_password must be a string")
        self._neo4j_password = value


"""
Definizioni statiche di nodi e relazioni per Neo4j
"""

# --- NODES --- #
NODE_DEVICE = "Device"  # Dispositivo SCADA / Modbus

# --- RELATIONS --- #
RELATION_COMMUNICATES_WITH = "COMMUNICATES_WITH"

# --- NODE PROPERTIES ---
NODE_PROPERTIES = {
    NODE_DEVICE: [
        "ip",  # stringa
        "port",  # int
        "role",  # client / server / slave
        "protocol",  # es. Modbus
        "unit_id",  # opzionale (solo per slave)
        "first_seen",  # timestamp
        "last_seen",  # timestamp
    ]
}

# --- RELATION PROPERTIES --- #
RELATION_PROPERTIES = {
    RELATION_COMMUNICATES_WITH: [
        "protocol",  # protocollo (es. Modbus)
        "first_seen",  # timestamp
        "last_seen",  # timestamp
        "total_queries",  # int
        "queries_by_function",  # dizionario {funzione: count}
        "error_count",  # int
    ]
}
