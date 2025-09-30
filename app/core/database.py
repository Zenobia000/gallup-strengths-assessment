"""
Database connection management with SQLAlchemy 2.0 support.
Provides both sync and async database connections with proper connection pooling.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import get_settings

settings = get_settings()

# Base class for SQLAlchemy models
Base = declarative_base()

# Async Database Setup
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.echo_sql,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "isolation_level": None,
    },
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync Database Setup (for migrations and admin tasks)
sync_engine = create_engine(
    settings.database_sync_url,
    echo=settings.echo_sql,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


# SQLite WAL mode configuration for better concurrent access
@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configure SQLite for optimal performance and concurrency."""
    cursor = dbapi_connection.cursor()
    # Enable WAL mode for better concurrent access
    cursor.execute("PRAGMA journal_mode=WAL")
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys=ON")
    # Set timeout for busy database
    cursor.execute("PRAGMA busy_timeout=30000")
    # Optimize SQLite performance
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=10000")
    cursor.execute("PRAGMA temp_store=memory")
    cursor.close()


@event.listens_for(async_engine.sync_engine, "connect")
def set_async_sqlite_pragma(dbapi_connection, connection_record):
    """Configure async SQLite connection."""
    set_sqlite_pragma(dbapi_connection, connection_record)


# Dependency for FastAPI routes
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session.

    Yields:
        AsyncSession: Database session for async operations
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Generator[Session, None, None]:
    """
    Dependency function to get sync database session.

    Yields:
        Session: Database session for sync operations
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for async database operations.

    Yields:
        AsyncSession: Database session within async context
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Database initialization
async def create_tables():
    """Create all database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables (for testing)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Health check function
async def check_database_health() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if database is accessible, False otherwise
    """
    try:
        async with get_async_db_context() as db:
            await db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False