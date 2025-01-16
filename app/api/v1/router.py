from fastapi import APIRouter, Depends
from app.api.v1.endpoints import demo
from app.core.auth import verify_token

# Create main v1 router with default dependencies
router = APIRouter(dependencies=[Depends(verify_token)])

# Include all endpoint routers 
router.include_router(
    demo.router,
    prefix="/demo",
    tags=["demo"]
)
