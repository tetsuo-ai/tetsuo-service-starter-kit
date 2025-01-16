#!/usr/bin/env python3
import asyncio
import websockets
import httpx
import json
from datetime import datetime
from typing import Any, Dict
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from app.core.config import get_settings

settings = get_settings()

class APITester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {settings.API_TOKEN}"}
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=self.headers
        )
        self.ws_url = f"ws://localhost:8080/ws"
        
    async def test_health(self) -> bool:
        """Test basic health endpoint"""
        try:
            print("\n🏥 Testing Health Endpoints...")
            
            # Test root endpoint
            response = await self.client.get(f"{self.base_url}/")
            root_data = response.json()
            print(f"✓ Root endpoint: {root_data}")
            
            # Test detailed health
            response = await self.client.get(f"{self.base_url}/health")
            health_data = response.json()
            print(f"✓ Health check: {json.dumps(health_data, indent=2)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False            
            
    async def test_websocket(self) -> bool:
        """Test WebSocket connection"""
        try:
            print("\n🔌 Testing WebSocket...")
            
            async with websockets.connect(self.ws_url) as ws:
                print("✓ WebSocket connected")
                
                # Send test message
                test_msg = f"Test message at {datetime.now().isoformat()}"
                await ws.send(test_msg)
                print(f"✓ Sent: {test_msg}")
                
                # Wait for response
                response = await ws.recv()
                print(f"✓ Received: {response}")
                
                return True
                
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            return False
            
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()

async def main():
    tester = APITester()
    try:
        # Run all tests
        await tester.test_health()
        await tester.test_websocket()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())