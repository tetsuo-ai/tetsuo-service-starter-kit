from abc import ABC, abstractmethod
from typing import Optional, Any
from app.core import log
from app.db import redis, RedisSchemas
from app.schemas import WSEventType, WSEvent, DemoData

class BaseService(ABC):
    """
    Base service interface that all core services must implement.
    Provides common functionality and enforces consistent patterns.
    """
    def __init__(self):
        self.redis_schemas = RedisSchemas
        self._websocket_clients = set()
    
    @abstractmethod
    async def start(self) -> None:
        """Initialize and start the service"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Cleanup and stop the service"""
        pass
    
    async def broadcast_event(self, event_type: WSEventType, data: dict) -> None:
        """Broadcast event to all connected WebSocket clients"""
        if not self._websocket_clients:
            return
            
        event = WSEvent(event_type=event_type, data=data)
        dead_clients = set()
        
        for client in self._websocket_clients:
            try:
                await client.send_json(event.model_dump())
            except Exception as e:
                log.error(f"Failed to send to websocket client: {e}")
                dead_clients.add(client)
        
        # Cleanup dead connections
        self._websocket_clients -= dead_clients
    
    def register_websocket(self, websocket) -> None:
        """Register a new WebSocket client"""
        self._websocket_clients.add(websocket)
    
    def remove_websocket(self, websocket) -> None:
        """Remove a WebSocket client"""
        self._websocket_clients.discard(websocket)
    
    async def get_redis_data(self, key: str) -> Optional[Any]:
        """Safely get data from Redis with error handling"""
        try:
            async with redis as r:
                return await r.get(key)
        except Exception as e:
            log.error(f"Redis get error: {e}")
            return None
            
    async def set_redis_data(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Safely set data in Redis with error handling"""
        try:
            async with redis as r:
                await r.set(key, value, ex=ex)
                return True
        except Exception as e:
            log.error(f"Redis set error: {e}")
            return False
    
    @abstractmethod
    async def get_status(self) -> dict:
        """Get service status and metrics
        
        Returns:
            dict: Status information including:
                - service name
                - status (online/offline)
                - uptime
                - any service-specific metrics
        """
        pass