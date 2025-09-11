from fastapi.middleware.cors import CORSMiddleware
from configuration.database_configuration import init_driver, close_driver_database
from fastapi import FastAPI
from controller import graph_controller, websocket_controller
import threading
from configuration.service_discovery_consumer import start_rabbitmq_consumer


def configure_cors(app: FastAPI):
    """Configure CORS settings for the FastAPI application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routers(app: FastAPI):
    """Include all routers in the FastAPI application."""

    app.include_router(graph_controller.router)
    app.include_router(websocket_controller.router)


def configure_events(app: FastAPI):
    """Configure startup and shutdown events."""

    @app.on_event("startup")
    def startup_event():
        # Inizializza Neo4j driver
        init_driver()

        # Avvia il consumer RabbitMQ in un thread separato
        t = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
        t.start()
        print("[*] RabbitMQ consumer avviato in thread separato.")

    @app.on_event("shutdown")
    def shutdown_event():
        # Chiudi Neo4j driver
        close_driver_database()


def configure_app(app: FastAPI):
    """Configure the FastAPI application with necessary settings."""

    # Configure CORS
    configure_cors(app=app)

    # Configure Events that happen in the API
    configure_events(app=app)

    # Configure Routers
    configure_routers(app=app)
