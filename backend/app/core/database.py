"""Database connection manager with async support for Neon Postgres."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create async engine. If NEON_DATABASE_URL is missing we still build a stub engine
# against a local sqlite URL so the app can import and serve /health; calls that
# actually hit Postgres will fail at request time with a clear error.
_db_url = settings.NEON_DATABASE_URL or "sqlite+aiosqlite:///./_missing.db"
_is_postgres = _db_url.startswith("postgresql")

engine = create_async_engine(
    _db_url,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_recycle=3600,
    **(
        {
            "pool_size": 10,
            "max_overflow": 20,
            "connect_args": {"ssl": "require"},
        }
        if _is_postgres
        else {}
    ),
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session.

    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
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


async def init_db() -> None:
    """Initialize database - create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections gracefully."""
    await engine.dispose()
