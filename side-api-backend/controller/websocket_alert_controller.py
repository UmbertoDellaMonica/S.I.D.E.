from fastapi import APIRouter, WebSocket
from configuration.websocket_manager import ws_alert_manager

router = APIRouter()


@router.websocket("/ws/alerts")
async def websocket_alert_endpoint(ws: WebSocket):
    await ws_alert_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except Exception:
        ws_alert_manager.disconnect(ws)
