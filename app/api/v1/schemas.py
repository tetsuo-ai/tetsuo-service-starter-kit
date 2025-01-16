from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

# Just reuse the base models from app.schemas
from app.schemas import (
    WhaleTransaction,
    MetricsSnapshot,
    SentimentData,
    Platform,
    WSEvent,
    WSEventType
)