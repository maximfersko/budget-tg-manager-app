from datetime import datetime
from typing import List, Dict, Optional

from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import REDIS_KEY_USER_ROLES
from database.models import User, Operation, Category


def _invalidate_user_roles_cache(tg_id: int):
    from core.redis_client import redis_client
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(redis_client.delete(REDIS_KEY_USER_ROLES.format(user_id=tg_id)))
    except Exception:
        pass


class DBRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_tg_id(self, tg_id: int) -> Optional[User]:
        from sqlalchemy.orm import selectinload
        stmt = select(User).options(selectinload(User.roles)).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_simple(self, tg_id: int) -> Optional[User]:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_operations(
        self,
        tg_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Operation]:
        stmt = select(Operation).where(Operation.user_id == tg_id)
        if start_date:
            stmt = stmt.where(Operation.date >= start_date)
        if end_date:
            stmt = stmt.where(Operation.date <= end_date)
        stmt = stmt.order_by(Operation.date.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_last_operation_date(self, tg_id: int) -> Optional[datetime]:
        stmt = select(func.max(Operation.date)).where(Operation.user_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_operations(self, tg_id: int, start_date: datetime, end_date: datetime) -> int:
        stmt = select(func.count(Operation.id)).where(
            Operation.user_id == tg_id,
            Operation.date >= start_date,
            Operation.date <= end_date,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_unique_raw_categories(self, tg_id: int) -> List[str]:
        stmt = select(distinct(Operation.raw_category)).where(Operation.user_id == tg_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all() if row[0]]

    async def add_user(
        self,
        tg_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
    ) -> User:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            user = User(tg_id=tg_id, first_name=first_name, last_name=last_name, username=username)
            self.session.add(user)
            await self.session.flush()
            from database.models import UserRole
            await self.assign_role_to_user(tg_id, UserRole.USER.value)
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
        await self.session.commit()
        return user

    async def add_operations_batch(self, tg_id: int, operations: List[Dict], bank_name: str) -> Dict:
        if not await self.get_user_by_tg_id(tg_id):
            raise ValueError(f"User with tg_id {tg_id} not found")

        if not operations:
            return {'added': 0, 'duplicates': 0}

        dates = [op["date"] for op in operations]
        min_date, max_date = min(dates), max(dates)

        stmt = select(Operation).where(
            Operation.user_id == tg_id,
            Operation.date >= min_date,
            Operation.date <= max_date,
            Operation.bank_name == bank_name,
        )
        result = await self.session.execute(stmt)
        existing_keys = {
            (op.date, round(float(op.amount), 2), op.raw_category)
            for op in result.scalars().all()
        }

        new_ops = [
            Operation(
                user_id=tg_id,
                date=op["date"],
                amount=op["amount"],
                raw_category=op["category"],
                description=op["description"],
                bank_name=bank_name,
                is_income=op["is_income"],
            )
            for op in operations
            if (op["date"], round(float(op["amount"]), 2), op["category"]) not in existing_keys
        ]

        if not new_ops:
            return {'added': 0, 'duplicates': len(operations)}

        self.session.add_all(new_ops)
        await self.session.commit()
        return {'added': len(new_ops), 'duplicates': len(operations) - len(new_ops)}

    async def add_category(
        self,
        name: str,
        is_income: bool,
        user_id: Optional[int] = None,
        emoji: Optional[str] = None,
    ) -> Category:
        cat = Category(name=name, is_income=is_income, user_id=user_id, emoji=emoji)
        self.session.add(cat)
        await self.session.commit()
        return cat

    async def get_user_categories(self, tg_id: int, is_income: bool) -> List[Category]:
        stmt = select(Category).where(
            Category.is_income == is_income,
            (Category.user_id.is_(None)) | (Category.user_id == tg_id),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_stats(self, tg_id: int, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        stmt = select(
            Operation.is_income,
            func.sum(Operation.amount).label("total"),
        ).where(
            Operation.user_id == tg_id,
            Operation.date >= start_date,
            Operation.date <= end_date,
        ).group_by(Operation.is_income)

        result = await self.session.execute(stmt)
        stats = {"income": 0.0, "expense": 0.0}
        for is_income, total_sum in result.all():
            stats["income" if is_income else "expense"] = float(total_sum)
        return stats

    async def get_category_breakdown(self, tg_id: int, start_date: datetime, end_date: datetime) -> List[tuple]:
        stmt = select(
            Operation.raw_category,
            Operation.is_income,
            func.sum(Operation.amount).label("total"),
            func.count(Operation.id).label("count"),
            func.avg(Operation.amount).label("avg_amount"),
        ).where(
            Operation.user_id == tg_id,
            Operation.date >= start_date,
            Operation.date <= end_date,
        ).group_by(
            Operation.raw_category, Operation.is_income
        ).order_by(
            Operation.is_income, func.sum(Operation.amount).desc()
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_role_by_name(self, role_name: str):
        from database.models import Role, UserRole
        stmt = select(Role).where(Role.name == UserRole(role_name))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_role(self, role_name: str, description: Optional[str] = None):
        from database.models import Role, UserRole
        role = Role(name=UserRole(role_name), description=description)
        self.session.add(role)
        await self.session.commit()
        return role

    async def assign_role_to_user(self, tg_id: int, role_name: str) -> bool:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return False
        role = await self.get_role_by_name(role_name)
        if not role:
            role = await self.create_role(role_name)
        if role not in user.roles:
            user.roles.append(role)
            await self.session.commit()
        await self._invalidate_roles_cache(tg_id)
        return True

    async def remove_role_from_user(self, tg_id: int, role_name: str) -> bool:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return False
        role = await self.get_role_by_name(role_name)
        if role and role in user.roles:
            user.roles.remove(role)
            await self.session.commit()
        await self._invalidate_roles_cache(tg_id)
        return True

    async def get_user_roles(self, tg_id: int) -> List[str]:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return []
        return [role.name.value for role in user.roles]

    async def ban_user(self, tg_id: int) -> bool:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return False
        user.is_banned = True
        user.is_active = False
        await self.session.commit()
        await self._invalidate_roles_cache(tg_id)
        return True

    async def unban_user(self, tg_id: int) -> bool:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return False
        user.is_banned = False
        user.is_active = True
        await self.session.commit()
        await self._invalidate_roles_cache(tg_id)
        return True

    async def get_all_admins(self) -> List[User]:
        from database.models import Role, UserRole, user_roles
        stmt = select(User).join(user_roles).join(Role).where(Role.name == UserRole.ADMIN)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def _invalidate_roles_cache(tg_id: int) -> None:
        from core.redis_client import redis_client
        await redis_client.delete(REDIS_KEY_USER_ROLES.format(user_id=tg_id))
