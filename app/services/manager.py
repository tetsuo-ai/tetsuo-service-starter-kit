from typing import Dict, Type, Optional, List
import asyncio
from loguru import logger
from fastapi import WebSocket
from datetime import datetime, timezone

from .base import BaseService
from app.core.config import get_settings
from app.schemas import WSEventType, WSEvent

settings = get_settings()

class ServiceManager:
    """
    Manages the lifecycle and dependencies of all core services.
    Provides centralized control and resource management.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.services: Dict[str, BaseService] = {}
            self.service_dependencies: Dict[str, List[str]] = {}
            self.websocket_clients: set[WebSocket] = set()
            self.start_time = datetime.now(timezone.utc)
            self.initialized = True
            logger.info("ServiceManager initialized")
    
    async def register_service(self, service_class: Type[BaseService], dependencies: List[str] = None) -> None:
        """
        Register a service with its dependencies.
        
        Args:
            service_class: The service class to register
            dependencies: List of service names this service depends on
        """
        service_name = service_class.__name__.lower()
        
        if service_name in self.services:
            logger.warning(f"Service {service_name} already registered")
            return
            
        # Store dependencies
        if dependencies:
            self.service_dependencies[service_name] = dependencies
            
            # Verify all dependencies are or will be registered
            missing_deps = [dep for dep in dependencies if dep not in self.services]
            if missing_deps:
                logger.warning(f"Service {service_name} has unmet dependencies: {missing_deps}")
        
        # Instantiate service
        try:
            service_instance = service_class()
            self.services[service_name] = service_instance
            logger.info(f"Service {service_name} registered successfully")
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")
            raise
    
    def get_service(self, service_name: str) -> Optional[BaseService]:
        """Get a registered service by name"""
        return self.services.get(service_name.lower())
    
    async def start_services(self) -> None:
        """Start all registered services in dependency order"""
        started_services = set()
        
        while len(started_services) < len(self.services):
            started_this_round = False
            
            for service_name, service in self.services.items():
                if service_name in started_services:
                    continue
                    
                # Check if all dependencies are started
                dependencies = self.service_dependencies.get(service_name, [])
                if all(dep in started_services for dep in dependencies):
                    try:
                        logger.info(f"Starting service: {service_name}")
                        await service.start()
                        started_services.add(service_name)
                        started_this_round = True
                    except Exception as e:
                        logger.error(f"Failed to start service {service_name}: {e}")
                        raise
            
            if not started_this_round and len(started_services) < len(self.services):
                remaining = set(self.services.keys()) - started_services
                logger.error(f"Circular dependency detected. Could not start: {remaining}")
                raise RuntimeError("Circular dependency detected in services")
        
        logger.info("All services started successfully")
    
    async def stop_services(self) -> None:
        """Stop all services in reverse dependency order"""
        # Build reverse dependency graph
        reverse_deps = {name: [] for name in self.services}
        for service, deps in self.service_dependencies.items():
            for dep in deps:
                reverse_deps[dep].append(service)
        
        stopped_services = set()
        
        while len(stopped_services) < len(self.services):
            stopped_this_round = False
            
            for service_name, service in self.services.items():
                if service_name in stopped_services:
                    continue
                    
                # Check if all dependent services are stopped
                dependents = reverse_deps[service_name]
                if all(dep in stopped_services for dep in dependents):
                    try:
                        logger.info(f"Stopping service: {service_name}")
                        await service.stop()
                        stopped_services.add(service_name)
                        stopped_this_round = True
                    except Exception as e:
                        logger.error(f"Error stopping service {service_name}: {e}")
            
            if not stopped_this_round and len(stopped_services) < len(self.services):
                remaining = set(self.services.keys()) - stopped_services
                logger.error(f"Could not gracefully stop services: {remaining}")
                break
        
        logger.info("All services stopped")

    def _serialize_datetime(self, obj):
        """Helper to convert datetime objects to ISO format strings"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    def _process_data(self, data: dict) -> dict:
        """Recursively process dict to serialize datetime objects"""
        return {
            k: (
                self._process_data(v) if isinstance(v, dict) else
                [self._process_data(i) if isinstance(i, dict) else self._serialize_datetime(i) for i in v]
                if isinstance(v, (list, tuple)) else
                self._serialize_datetime(v)
            )
            for k, v in data.items()
        }

    async def broadcast_event(self, event_type: WSEventType, data: dict) -> None:
        """Broadcast event to all connected WebSocket clients"""
        if not self.websocket_clients:
            return
            
        # Process data to handle datetime serialization
        processed_data = self._process_data(data)
        event = WSEvent(event_type=event_type, data=processed_data)
        dead_clients = set()
        
        for client in self.websocket_clients:
            try:
                # Use model_dump_json to ensure proper serialization
                await client.send_json(event.model_dump(mode='json'))
            except Exception as e:
                logger.error(f"Failed to send to websocket client: {e}")
                dead_clients.add(client)
        
        # Cleanup dead connections
        self.websocket_clients -= dead_clients
    
    async def register_websocket(self, websocket: WebSocket) -> None:
        """Register a new WebSocket client"""
        await websocket.accept()
        self.websocket_clients.add(websocket)
        logger.info(f"New WebSocket client connected. Total clients: {len(self.websocket_clients)}")
    
    async def remove_websocket(self, websocket: WebSocket) -> None:
        """Remove a WebSocket client"""
        self.websocket_clients.discard(websocket)
        logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.websocket_clients)}")
    
    async def get_status(self) -> dict:
        """Get status of all services"""
        status = {
            "uptime": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
            "websocket_clients": len(self.websocket_clients),
            "services": {}
        }
        
        for name, service in self.services.items():
            try:
                service_status = await service.get_status()
                status["services"][name] = service_status
            except Exception as e:
                logger.error(f"Error getting status for service {name}: {e}")
                status["services"][name] = {"status": "error", "error": str(e)}
        
        return status

# Global instance
service_manager = ServiceManager()