import asyncio
from redis.asyncio import Redis
from datetime import datetime

async def test_redis_connection():
    try:
        # Create Redis connection
        redis = Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Test basic operations
        print("Testing Redis connection...")
        
        # Test PING
        result = await redis.ping()
        print(f"✓ PING successful")
        
        # Test SET/GET
        test_key = f"test_key_{datetime.now().timestamp()}"
        await redis.set(test_key, 'test_value', ex=60)  # 60s expiry
        value = await redis.get(test_key)
        print(f"✓ SET/GET successful")
        
        # Test expiry
        ttl = await redis.ttl(test_key)
        print(f"✓ TTL working (expires in {ttl}s)")
        
        # Clean up
        await redis.delete(test_key)
        print(f"✓ DELETE successful")
        
        print("\n✨ All Redis tests passed!")
        
        # Close connection
        await redis.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Redis error: {e}")
        print("\nPlease check that Redis is running:")
        print("  macOS: brew services start redis")
        print("  Linux: sudo systemctl start redis-server")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_redis_connection())
    if not success:
        exit(1)