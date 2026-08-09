import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
VECTOR_DB_PATH = DATA_DIR / "vector_db"

# Chunking Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Application Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SUPPORTED_FILE_TYPES = [".txt", ".pdf", ".docx"]

DOCUMENT_SCHEMA_VERSION = "1.0"
SUPPORTED_VECTOR_SCHEMA_VERSION = "1.0"

# Embeddings Configuration
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DEVICE = "cpu"
NORMALIZE_EMBEDDINGS = True
EMBEDDING_BATCH_SIZE = 32

# Vector Database Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_TIMEOUT = int(os.getenv("QDRANT_TIMEOUT", "10"))
QDRANT_COLLECTION = "knowsphere_documents"
VECTOR_DISTANCE = "Cosine"
TOP_K_RESULTS = 5
COLLECTION_RECREATE = False

# Database Configuration
if ENVIRONMENT == "production":
    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/knowsphere")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/knowsphere")
else:
    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR}/knowsphere.db")
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/knowsphere.db")

# Redis Cache Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# LLM Configuration
# Development: TinyLlama CPU
# Production: Llama-3-8B CUDA
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
LLM_DEVICE = "cpu"

MAX_NEW_TOKENS = 256
TEMPERATURE = 0.7
TOP_P = 0.9
MAX_CONTEXT_LENGTH = 4000

# Authentication Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_secret_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080"))
