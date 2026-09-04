"""
KhedutMitra AI — Database Engine & Session Factory
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# SQLite needs connect_args check_same_thread=False; PostgreSQL uses pool settings
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
_engine_kwargs: dict = {"echo": (settings.APP_ENV == "development")}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Vercel/serverless PostgreSQL URLs commonly use PgBouncer transaction
    # pooling, which cannot safely reuse asyncpg prepared statements.
    _engine_kwargs["connect_args"] = {"statement_cache_size": 0}
    _engine_kwargs.update({"pool_size": 10, "max_overflow": 20, "pool_pre_ping": True})

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
