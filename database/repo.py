from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, Operation, Category
from typing import List, Dict, Optional


class DBRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, tg_id: int, first_name: str, last_name: Optional[str] = None,
                       username: Optional[str] = None) -> User:
        user = await self.session.get(User, tg_id)
        if not user:
            user = User(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username
            )
            self.session.add(user)
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.username = username

        await self.session.commit()
        return user

    async def add_operations_batch(self, user_id: int, operations: List[Dict]):
        objs = []
        for op in operations:
            objs.append(
                Operation(
                    user_id=user_id,
                    date=op["date"],
                    amount=op["amount"],
                    raw_category=op["category"],
                    description=op["description"],
                    is_income=op["is_income"]
                )
            )
        self.session.add_all(objs)
        await self.session.commit()

    async def add_category(self, name: str, is_income: bool, user_id: Optional[int] = None,
                           emoji: Optional[str] = None) -> Category:
        cat = Category(
            name=name,
            is_income=is_income,
            user_id=user_id,
            emoji=emoji
        )
        self.session.add(cat)
        await self.session.commit()
        return cat

    async def get_user_categories(self, user_id: int, is_income: bool) -> List[Category]:
        stmt = select(Category).where(
            Category.is_income == is_income,
            (Category.user_id.is_(None)) | (Category.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
