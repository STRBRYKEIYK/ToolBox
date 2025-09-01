"""
WorkBox Database Connection Module
=================================

This module provides the SQLAlchemy ORM connection for the WorkBox application,
implementing database connection pooling and environment-based configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "workbox_db")

# Connection string
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,                 # Maximum number of connections to keep open
    max_overflow=10,              # Maximum number of connections to create beyond pool_size
    pool_timeout=30,              # Seconds to wait before timeout on connection request
    pool_recycle=3600,            # Recycle connections after 1 hour
    pool_pre_ping=True,           # Test connections before usage to avoid stale connections
    connect_args={
        "connect_timeout": 10,     # Seconds to wait for database connection
        "charset": "utf8mb4",      # Support for full UTF-8 character set including emojis
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session.
    
    Use this function with FastAPI dependency injection to get
    a database session for each request.
    
    Example:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables defined using the SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)

def check_connection():
    """
    Test the database connection.
    
    Returns:
        bool: True if connection successful, False otherwise.
    """
    try:
        # Try to create a connection - using SQLAlchemy 2.0+ compatible syntax
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
            conn.commit()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
