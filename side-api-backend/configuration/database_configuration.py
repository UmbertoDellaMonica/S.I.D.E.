from neo4j import GraphDatabase

# --- CONFIGURAZIONE ---


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


class Config:
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


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
