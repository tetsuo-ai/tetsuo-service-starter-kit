from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import sys

from app.core import get_settings, log
from app.db import redis
from app.services import service_manager
from app.api import v1_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle management for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    try:
        log.info("Starting up FastAPI service...")
        
        # Test Redis connection
        log.info("Testing Redis connection...")
        async with redis as r:
            await r.ping()
            log.info("✓ Redis connection successful")
            
        # Register and start services
        log.info("Initializing services...")
        from app.services.registry import service_registry
        await service_registry.register_all()
        log.info("✓ Services registered")
        
        await service_manager.start_services()
        log.info("✓ Services started")
        
        log.info("Startup complete - ready to handle requests")
        
    except Exception as e:
        log.error(f"Fatal error during startup: {str(e)}")
        # Print full traceback for debugging
        import traceback
        traceback.print_exc()
        # Force exit on startup failure
        sys.exit(1)
    
    yield
    
    # Shutdown
    try:
        log.info("Shutting down FastAPI service...")
        await service_manager.stop_services()
        log.info("Services stopped successfully")
    except Exception as e:
        log.error(f"Error during shutdown: {e}")
        sys.exit(1)

# Create FastAPI app
app = FastAPI(
    servers=[{"url": "https://localhost", "description": "core"}],
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan,
    # Add debug flag based on environment
    debug=True  # TODO: Set from environment
)

security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Basic health check endpoint
@app.get("/")
async def root():
    """Basic health check endpoint"""
    return {
        "status": "online",
        "version": "0.1.0"
    }

# Detailed health check
@app.post("/health")
@app.get("/health")
async def health():
    """Detailed health check"""
    status = {
        "service": "ok",
        "redis": False
    }
    
    try:
        async with redis as r:
            await r.ping()
            status["redis"] = True
    except Exception as e:
        log.error(f"Redis health check failed: {e}")
    
    # Add service status
    try:
        service_status = await service_manager.get_status()
        status["services"] = service_status
    except Exception as e:
        log.error(f"Service status check failed: {e}")
        status["services"] = {"error": str(e)}
    
    return status

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    try:
        await service_manager.register_websocket(websocket)
        while True:
            try:
                data = await websocket.receive_text()
                await websocket.send_text(f"Message received: {data}")
            except WebSocketDisconnect:
                break
            except Exception as e:
                log.error(f"WebSocket error: {e}")
                break
    finally:
        await service_manager.remove_websocket(websocket)

# Include API routers
app.include_router(
    v1_router,
    prefix=settings.API_V1_STR
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=6502,
        #uds="/tmp/uvicorn.sock",
        reload=True,
        log_level="debug"
    )
