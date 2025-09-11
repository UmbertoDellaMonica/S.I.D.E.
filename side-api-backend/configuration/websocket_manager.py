# websocket_service.py
import json
from fastapi import WebSocket
from typing import Set


class WebSocketManager:
    """Gestisce le connessioni WebSocket con il front-end."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active_connections.discard(ws)

    async def broadcast(self, message: dict):
        """Invia un messaggio JSON a tutti i client connessi."""
        data = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception:
                self.disconnect(connection)


ws_manager = WebSocketManager()
