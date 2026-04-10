from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core.config import DB_URL


_PLACEHOLDER_ASYNC_PG = "postgresql+asyncpg://_:_@127.0.0.1:5432/_"


def _database_url() -> str:
    return DB_URL if DB_URL else _PLACEHOLDER_ASYNC_PG


engine = create_async_engine(
    _database_url(),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_async_session_maker():

    worker_engine = create_async_engine(
        _database_url(),
        echo=False,
        pool_pre_ping=True,
        pool_recycle=3600,
        poolclass=None 
    )
    return async_sessionmaker(worker_engine, class_=AsyncSession, expire_on_commit=False)
