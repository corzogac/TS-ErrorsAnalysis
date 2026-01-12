# ---------------------------------------------------------------------------
# File    : api/database.py
# Purpose : Database models and session management (with Stage 8 optimizations)
# License : MIT
# ---------------------------------------------------------------------------
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ts_analysis.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class AnalysisRecord(Base):
    """Record of each analysis performed"""
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String, index=True, nullable=True)

    # Input metadata
    n_points = Column(Integer)

    # Key metrics (for quick queries)
    rmse = Column(Float)
    nsc = Column(Float)
    correlation = Column(Float)
    kge2009 = Column(Float)

    # Full metrics as JSON
    metrics_json = Column(JSON)

    # Optional user metadata
    user_id = Column(String, index=True, nullable=True)
    analysis_name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Composite indexes for common query patterns (Stage 8 optimization)
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_user_session', 'user_id', 'session_id'),
    )

class UserSession(Base):
    """Track user sessions"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analysis_count = Column(Integer, default=0)

class SystemStats(Base):
    """System-wide statistics"""
    __tablename__ = "system_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    total_analyses = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    total_users = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
