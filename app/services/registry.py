from typing import List, Tuple, Type
from app.services import BaseService, service_manager
from app.core.logging import log

class ServiceRegistry:
    """
    Registry of all available services with their dependencies.
    Makes it easy to register new services and manage their dependencies.
    """
    
    def __init__(self):
        self._registered = False
    
    @staticmethod
    async def register_all():
        """Register all available services with the service manager"""
        log.info("Starting service registration")
        
        # Define services and their dependencies
        services: List[Tuple[Type[BaseService], List[str]]] = [
            # DemoService has no dependencies
            #(DemoService, []),
        ]
        
        for service_class, dependencies in services:
            try:
                service_name = service_class.__name__
                log.info(f"Registering service: {service_name}")
                
                # Register with manager
                await service_manager.register_service(service_class, dependencies)
                log.info(f"✓ {service_name} registered successfully")
                
            except Exception as e:
                log.error(f"Failed to register service {service_class.__name__}: {e}")
                # Re-raise to handle in lifespan manager
                raise

# Initialize registry
service_registry = ServiceRegistry()