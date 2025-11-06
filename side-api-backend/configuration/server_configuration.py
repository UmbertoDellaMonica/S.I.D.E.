from fastapi.middleware.cors import CORSMiddleware
from configuration.database_configuration import init_driver, close_driver_database
from fastapi import FastAPI
from controller import (
    graph_controller,
    websocket_controller,
    websocket_alert_controller,
)
import threading
from configuration.service_discovery_consumer import start_rabbitmq_consumer
from configuration.service_device_alert_consumer import start_rabbitmq_alert_consumer


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
    app.include_router(graph_controller.router)
    app.include_router(websocket_controller.router)
    app.include_router(websocket_alert_controller.router)


def configure_events(app: FastAPI):

    @app.on_event("startup")
    def startup_event():
        print("[DEBUG] Evento di startup FastAPI eseguito.")
        init_driver()
        start_rabbitmq_consumer()
        start_rabbitmq_alert_consumer()

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
