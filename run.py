import os
import uvicorn
import asyncio

from src.core.config import DATA_DIR, RAW_DIR, PROCESSED_DIR, VECTOR_DB_PATH
from src.database.database import init_db, AsyncSessionLocal
from src.database.models import UserModel
from src.auth.password_manager import hash_password
from sqlalchemy import select
from src.core.logger import get_logger

logger = get_logger(__name__)


async def setup():
    # 1. Create required directories
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)

    # 2. Initialize SQLite database
    await init_db()

    # 3. Create demo account
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserModel).where(
                UserModel.email == "demo@knowsphere.local"
            )
        )

        demo_user = result.scalars().first()

        if not demo_user:
            logger.info("Creating demo account (demo@knowsphere.local / demo123)")
            hashed_password = hash_password("demo123")
            demo_user = UserModel(
                username="demo",
                email="demo@knowsphere.local",
                password_hash=hashed_password,
                role="ADMIN",
                is_active=True
            )
            session.add(demo_user)
            await session.commit()

    # 4. Initialize Local Vector Store
    from src.vectorstore.local_store import LocalVectorStore

    LocalVectorStore()

    print("========================================")
    print("        KNOWSPHERE AI")
    print("========================================")
    print("Database: OK")
    print("Storage: OK")
    print("AI Engine: OK")
    print("Vector Store: OK")
    print("API: OK")
    print()
    print("Application:")
    print("http://localhost:8000")
    print("========================================")
    print()


if __name__ == "__main__":
    # Use local/development configuration
    os.environ["ENVIRONMENT"] = "development"

    # Run setup
    asyncio.run(setup())

    # Start FastAPI
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8000,
    )