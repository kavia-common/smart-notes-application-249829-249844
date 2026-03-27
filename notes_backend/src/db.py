"""
Async database setup (PostgreSQL) for the Smart Notes backend.

Environment variables (set via .env by orchestrator):
- DATABASE_URL: SQLAlchemy URL, e.g. postgresql+asyncpg://user:pass@host:port/db
"""

from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.models import Base

_ENGINE: AsyncEngine | None = None
_SESSIONMAKER: async_sessionmaker[AsyncSession] | None = None


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is required (e.g. postgresql+asyncpg://...)."
        )
    return database_url


# PUBLIC_INTERFACE
def get_engine() -> AsyncEngine:
    """Return a singleton async SQLAlchemy engine."""
    global _ENGINE, _SESSIONMAKER
    if _ENGINE is None:
        _ENGINE = create_async_engine(_get_database_url(), pool_pre_ping=True)
        _SESSIONMAKER = async_sessionmaker(_ENGINE, expire_on_commit=False)
    return _ENGINE


# PUBLIC_INTERFACE
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return a singleton async sessionmaker."""
    if _SESSIONMAKER is None:
        get_engine()
    assert _SESSIONMAKER is not None
    return _SESSIONMAKER


# PUBLIC_INTERFACE
async def init_db_schema() -> None:
    """Create tables if they don't exist (simple dev-friendly bootstrap).

    For production, prefer Alembic migrations. For this template, we auto-create.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# PUBLIC_INTERFACE
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an AsyncSession."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
