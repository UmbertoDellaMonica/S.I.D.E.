import socketio
from fastapi import FastAPI
from configuration.server_configuration import configure_app


app = FastAPI()


# Configure the Application
configure_app(app)
