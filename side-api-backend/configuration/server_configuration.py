from fastapi.middleware.cors import CORSMiddleware
from configuration.database_configuration import init_driver, close_driver_database
from fastapi import FastAPI
from controller import graph_controller


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


def configure_events(app: FastAPI):
    """Configure startup and shutdown events."""

    @app.on_event("startup")
    def startup_event():
        init_driver()

    @app.on_event("shutdown")
    def shutdown_event():
        close_driver_database()


def configure_app(app: FastAPI):
    """Configure the FastAPI application with necessary settings."""

    # Configure CORS
    configure_cors(app=app)

    # Configure Events that happen in the API
    configure_events(app=app)

    # Configure Routers
    configure_routers(app=app)
