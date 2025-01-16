from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json

class DemoData(BaseModel):
    value: str
    timestamp: datetime = None
    
class WSEventType(str, Enum):
    NEW_EVENT = "new_event"
    
class WSEvent(BaseModel):
    event_type: WSEventType
    data: Dict
    timestamp: datetime = None

