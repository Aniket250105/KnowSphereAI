from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.core import config
from src.core.logger import get_logger

logger = get_logger(__name__)

ASYNC_DATABASE_URL = config.ASYNC_DATABASE_URL

engine_kwargs = {}
if ASYNC_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Connection pooling for PostgreSQL
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    **engine_kwargs
)

async_session_factory = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# Keep AsyncSessionLocal for backward compatibility if any file still imports it
AsyncSessionLocal = async_session_factory

Base = declarative_base()

async def init_db():
    """Initializes the database tables (only for tests/dev if not using Alembic)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")

async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()



