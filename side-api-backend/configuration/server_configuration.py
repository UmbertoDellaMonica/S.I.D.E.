from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


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


def configure_app(app: FastAPI):
    """Configure the FastAPI application with necessary settings."""

    # Configure CORS
    configure_cors(app=app)

    # Configure Routers
    configure_routers(app=app)
