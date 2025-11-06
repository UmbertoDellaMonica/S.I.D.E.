# websocket_service.py
import json
from fastapi import WebSocket
from typing import Set


class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.add(ws)
        print(f"[WS] Nuovo client connesso ({len(self.active_connections)} attivi).")

    def disconnect(self, ws: WebSocket):
        self.active_connections.discard(ws)
        print(f"[WS] Client disconnesso ({len(self.active_connections)} attivi).")

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception:
                self.disconnect(connection)


# Istanza principale per eventi di rete
ws_manager = WebSocketManager()

# Istanza separata per alert/anomalie
ws_alert_manager = WebSocketManager()
