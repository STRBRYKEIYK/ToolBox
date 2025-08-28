from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from .models import Base

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'workbox_db')}",
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)
