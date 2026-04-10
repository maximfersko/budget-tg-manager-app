import asyncio
import os
from datetime import datetime, timedelta
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from database.engine import Base
from database.models import User, Operation, Role, UserRole
from database.repo import DBRepository
from core.redis_client import RedisClient

DB_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
TEST_DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:5432/budget_test_db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def repo(db_session: AsyncSession) -> DBRepository:
    return DBRepository(db_session)


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    client = RedisClient()
    await client.connect()
    
    if client.redis:
        keys = await client.redis.keys("test:*")
        if keys:
            await client.redis.delete(*keys)
    
    yield client
    
    await client.close()


@pytest_asyncio.fixture
async def test_user(repo: DBRepository) -> User:
    await repo.add_user(
        tg_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    return await repo.get_user_by_tg_id(123456789)


@pytest_asyncio.fixture
async def test_operations(repo: DBRepository, test_user: User) -> list[Operation]:
    base_date = datetime(2026, 4, 1)
    
    operations_data = [
        {"amount": 100000.0, "is_income": True, "raw_category": "Зарплата", "description": "Salary April", "date": base_date},
        
        {"amount": 5000.0, "is_income": True, "raw_category": "Возврат", "description": "Refund", "date": base_date + timedelta(days=1)},
        {"amount": 3000.0, "is_income": True, "raw_category": "Прочее", "description": "Other income", "date": base_date + timedelta(days=2)},
        
        {"amount": -5000.0, "is_income": False, "raw_category": "Продукты", "description": "Supermarket", "date": base_date + timedelta(days=3)},
        {"amount": -3000.0, "is_income": False, "raw_category": "Продукты", "description": "Market", "date": base_date + timedelta(days=4)},
        {"amount": -2000.0, "is_income": False, "raw_category": "Продукты", "description": "Store", "date": base_date + timedelta(days=5)},
        
        {"amount": -1500.0, "is_income": False, "raw_category": "Транспорт", "description": "Taxi", "date": base_date + timedelta(days=6)},
        {"amount": -500.0, "is_income": False, "raw_category": "Транспорт", "description": "Metro", "date": base_date + timedelta(days=7)},
        
        {"amount": -8000.0, "is_income": False, "raw_category": "Развлечения", "description": "Cinema", "date": base_date + timedelta(days=8)},
        {"amount": -12000.0, "is_income": False, "raw_category": "Развлечения", "description": "Restaurant", "date": base_date + timedelta(days=9)},
        
        {"amount": 10000.0, "is_income": True, "raw_category": "Переводы", "description": "Transfer from Максим Б", "date": base_date + timedelta(days=10)},
        {"amount": -10000.0, "is_income": False, "raw_category": "Переводы", "description": "Transfer to own account Максим Б", "date": base_date + timedelta(days=10)},
    ]
    
    operations = []
    for op_data in operations_data:
        op = Operation(
            user_id=test_user.tg_id,
            amount=op_data["amount"],
            is_income=op_data["is_income"],
            raw_category=op_data["raw_category"],
            description=op_data["description"],
            date=op_data["date"],
            bank_name="test_bank",
            currency="RUB"
        )
        repo.session.add(op)
        operations.append(op)
    
    await repo.session.commit()
    return operations


@pytest.fixture
def mock_internal_keywords(monkeypatch):
    keywords = ["максим б", "максим сергеевич б", "бобров"]
    monkeypatch.setattr("core.config.INTERNAL_TRANSFER_KEYWORDS", keywords)
    return keywords
