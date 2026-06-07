from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import hmac
import json
from datetime import datetime

from app.api.routes.stats import get_database_stats, get_query_stats
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific WebSocket, checking if still connected."""
        try:
            if websocket.client_state.name != 'DISCONNECTED':
                await websocket.send_text(message)
            else:
                logger.warning("Attempted to send to disconnected WebSocket")
                return False
            return True
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {e}")
            return False
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if self.active_connections:
            message_str = json.dumps(message)
            disconnected = set()
            
            for connection in self.active_connections:
                try:
                    if connection.client_state.name != 'DISCONNECTED':
                        await connection.send_text(message_str)
                    else:
                        disconnected.add(connection)
                except Exception as e:
                    logger.error(f"Error sending to WebSocket: {e}")
                    disconnected.add(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.active_connections.discard(connection)


manager = ConnectionManager()


def websocket_api_key(websocket: WebSocket) -> str:
    auth_header = websocket.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return (
        websocket.headers.get("x-api-key", "").strip()
        or websocket.query_params.get("api_key", "").strip()
    )


async def require_websocket_api_key(websocket: WebSocket) -> bool:
    if settings.ALLOW_UNAUTHENTICATED:
        return True
    configured_key = settings.api_key_value
    supplied_key = websocket_api_key(websocket)
    if configured_key and supplied_key and hmac.compare_digest(supplied_key, configured_key):
        return True
    await websocket.close(code=1008, reason="Authentication required")
    return False


@router.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    """WebSocket endpoint for real-time statistics updates."""
    if not await require_websocket_api_key(websocket):
        return
    await manager.connect(websocket)
    
    try:
        # Send initial stats
        db_stats = await get_database_stats()
        query_stats = await get_query_stats()
        
        initial_message = {
            "type": "initial",
            "data": {
                "database": db_stats,
                "queries": query_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        sent = await manager.send_personal_message(json.dumps(initial_message), websocket)
        if not sent:
            logger.warning("Failed to send initial message, closing connection")
            return
        
        # Send periodic updates every 5 seconds
        while True:
            await asyncio.sleep(5)
            
            try:
                db_stats = await get_database_stats()
                query_stats = await get_query_stats()
                
                update_message = {
                    "type": "update",
                    "data": {
                        "database": db_stats,
                        "queries": query_stats,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
                sent = await manager.send_personal_message(json.dumps(update_message), websocket)
                if not sent:
                    logger.warning("Failed to send update message, closing connection")
                    break
            except Exception as e:
                logger.error(f"Error fetching stats for WebSocket: {e}")
                break
                
    except asyncio.CancelledError:
        logger.info("WebSocket connection cancelled during shutdown")
        manager.disconnect(websocket)
        raise
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)
