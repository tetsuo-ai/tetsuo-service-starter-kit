from datetime import datetime, timedelta
from typing import Optional
import json
from app.schemas import DemoData
from app.core.logging import log

class RedisKeys:
    """Redis key patterns for different data types"""
    
    @staticmethod
    def demo_key(test :str) -> str:
        return f"demo:{test.value}:latest"

class RedisSchemas:
    """Methods for storing and retrieving data from Redis"""
    
    @staticmethod
    async def store_demo(redis, data: DemoData) -> None:
        demo_key = RedisKeys.demo_key(data.value)
        await redis.set(
            demo_key,
            json.dumps({
                "value": data.value,
                "timestamp": data.timestamp.isoformat()
            })
        )

    @staticmethod
    async def get_demo(redis, test_val) -> Optional[DemoData]:
        """Get latest sentiment for platform"""
        data = await redis.get(RedisKeys.demo_key(test_val))
        if not data:
            return None
            
        try:
            parsed = json.loads(data)
            return DemoData(
                value=parsed["value"],
                timestamp=datetime.fromisoformat(parsed["timestamp"])
            )
        except Exception as e:
            log.error(f"Error parsing sentiment data: {e}")
            return None
            