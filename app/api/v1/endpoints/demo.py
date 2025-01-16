import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, List, Any, Dict, Literal, Union, Generator

from app.services import service_manager
from app.db.redis import redis
from app.db.schemas import RedisSchemas

router = APIRouter()

load_dotenv()

class DemoRequest(BaseModel):
    demo: str

class DemoResponse(BaseModel):
    demo: str

@router.post("/demo", response_model=DemoResponse)
async def demo_request(
    request: DemoRequest
):
    try:
        return {"demo": request.demo}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

