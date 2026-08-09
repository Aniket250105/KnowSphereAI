import asyncio
import os
import sys

# Add root to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import config
from sqlalchemy.ext.asyncio import create_async_engine
from qdrant_client import QdrantClient
import redis.asyncio as redis

async def run_tests():
    print("Testing Production Infrastructure Connection")
    print("-" * 50)
    
    # Test Redis
    try:
        r = redis.from_url(config.REDIS_URL, decode_responses=True)
        await r.ping()
        print("✅ Redis Connected")
        await r.close()
    except Exception as e:
        print(f"❌ Redis Failed: {e}")
        
    # Test PostgreSQL
    try:
        engine = create_async_engine(config.ASYNC_DATABASE_URL)
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL Connected")
    except Exception as e:
        print(f"❌ PostgreSQL Failed: {e}")
        
    # Test Qdrant
    try:
        if getattr(config, 'QDRANT_URL', None):
            q_client = QdrantClient(url=config.QDRANT_URL)
            q_client.get_collections()
            print("✅ Qdrant Connected")
        else:
            print("⚠️ Qdrant using local mode")
    except Exception as e:
        print(f"❌ Qdrant Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())
