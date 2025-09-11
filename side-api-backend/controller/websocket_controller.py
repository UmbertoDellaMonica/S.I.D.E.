# websocket_controller.py
from fastapi import APIRouter, WebSocket
from configuration.websocket_manager import ws_manager

router = APIRouter()


@router.websocket("/ws/network")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # opzionale, se vuoi gestire input client
    except Exception:
        ws_manager.disconnect(ws)
