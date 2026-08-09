from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from src.database.database import Base

class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="USER")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

class UserOrganizationModel(Base):
    __tablename__ = "user_organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    role = Column(String, default="USER")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True) # Usually the document_id/hash
    document_hash = Column(String, unique=True, index=True)
    filename = Column(String)
    file_type = Column(String)
    path = Column(String)
    chunk_count = Column(Integer)
    status = Column(String) # UPLOAD, PROCESSING, INDEXED, DELETED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True) # UUID
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.session_id"))
    role = Column(String) # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class FeedbackModel(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    rating = Column(String) # HELPFUL or NOT_HELPFUL
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalyticsEventModel(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, index=True)
    query = Column(Text)
    response_time_seconds = Column(Float)
    retrieval_time_seconds = Column(Float)
    generation_time_seconds = Column(Float)
    confidence_score = Column(String)
    search_mode = Column(String, default="hybrid")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentAnalyticsModel(Base):
    __tablename__ = "document_analytics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(String, index=True)
    document_name = Column(String)
    retrieval_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True))
    average_similarity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserAnalyticsModel(Base):
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, unique=True, index=True)
    total_queries = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    first_activity = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    average_session_duration = Column(Float, default=0.0)

class FeedbackAnalyticsModel(Base):
    __tablename__ = "feedback_analytics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    total_helpful = Column(Integer, default=0)
    total_not_helpful = Column(Integer, default=0)
    helpfulness_percentage = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String, primary_key=True, index=True) # UUID or benchmark_name
    dataset_name = Column(String)
    dataset_version = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    average_score = Column(Float, default=0.0)
    
    # Config Snapshots
    embedding_model = Column(String, nullable=True)
    llm_model = Column(String, nullable=True)
    retrieval_mode = Column(String, nullable=True)
    top_k = Column(Integer, nullable=True)
    reranker = Column(String, nullable=True)
    prompt_version = Column(String, nullable=True)
    
    configuration = Column(Text, nullable=True) # fallback JSON blob if needed

class EvaluationResultModel(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("evaluation_runs.id"), index=True)
    query = Column(Text)
    expected_answer = Column(Text, nullable=True)
    answer = Column(Text)
    retrieval_score = Column(Float, default=0.0)
    grounding_score = Column(Float, default=0.0)
    citation_score = Column(Float, default=0.0)
    latency = Column(Float, default=0.0)
    strategy = Column(String, nullable=True)
    failure_reason = Column(Text, nullable=True)
    retrieved_context = Column(Text, nullable=True) # Added for Failure Explorer

class PromptExperimentModel(Base):
    __tablename__ = "prompt_experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_a = Column(String)
    prompt_b = Column(String)
    winner = Column(String)
    metrics = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

