from typing import List, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Operation, Category


class DBRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_tg_id(self, tg_id: int) -> Optional[User]:
        from sqlalchemy.orm import selectinload
        
        stmt = select(User).options(selectinload(User.roles)).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_operations(self, tg_id: int) -> List[Operation]:
        stmt = select(Operation).where(
            Operation.user_id == tg_id
        ).order_by(Operation.date.desc())

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_user(self, tg_id: int, first_name: str, last_name: Optional[str] = None,
                       username: Optional[str] = None) -> User:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            user = User(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username
            )
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

    async def add_operations_batch(self, tg_id: int, operations: List[Dict], bank_name: str):
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            raise ValueError(f"User with tg_id {tg_id} not found")

        if not operations:
            return {'added': 0, 'duplicates': 0}

        dates = [op["date"] for op in operations]
        min_date = min(dates)
        max_date = max(dates)

        stmt = select(Operation).where(
            Operation.user_id == tg_id,
            Operation.date >= min_date,
            Operation.date <= max_date,
            Operation.bank_name == bank_name
        )
        result = await self.session.execute(stmt)
        existing_ops = result.scalars().all()

        existing_keys = {
            (op.date, float(op.amount), op.raw_category)
            for op in existing_ops
        }

        unique_operations = []
        for op in operations:
            key = (op["date"], float(op["amount"]), op["category"])
            if key not in existing_keys:
                unique_operations.append(op)

        if not unique_operations:
            return {'added': 0, 'duplicates': len(operations)}

        objs = []
        unique_cat_data = {(op["category"], op["is_income"]) for op in unique_operations}
        cat_names = {name for name, _ in unique_cat_data}

        stmt = select(Category).where(
            Category.name.in_(cat_names),
            (Category.user_id == tg_id) | (Category.user_id == None)
        )
        result = await self.session.execute(stmt)
        existing_categories = result.scalars().all()

        category_map = {
            (c.name, c.is_income): c.id for c in existing_categories
        }

        new_cats = []
        for name, is_income in unique_cat_data:
            if (name, is_income) not in category_map:
                new_cat = Category(name=name, is_income=is_income, user_id=tg_id)
                self.session.add(new_cat)
                new_cats.append(new_cat)

        if new_cats:
            await self.session.flush()
            for nc in new_cats:
                category_map[(nc.name, nc.is_income)] = nc.id

        for op in unique_operations:
            cat_id = category_map.get((op["category"], op["is_income"]))
            objs.append(
                Operation(
                    user_id=tg_id,
                    date=op["date"],
                    amount=op["amount"],
                    category_id=cat_id,
                    raw_category=op["category"],
                    description=op["description"],
                    bank_name=bank_name,
                    is_income=op["is_income"]
                )
            )
        self.session.add_all(objs)
        await self.session.commit()

        return {
            'added': len(objs),
            'duplicates': len(operations) - len(objs)
        }

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

    async def get_user_categories(self, tg_id: int, is_income: bool) -> List[Category]:
        stmt = select(Category).where(
            Category.is_income == is_income,
            (Category.user_id.is_(None)) | (Category.user_id == tg_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_stats(self, tg_id: int, start_date, end_date) -> Dict[str, float]:
        from sqlalchemy import func

        stmt = select(
            Operation.is_income,
            func.sum(Operation.amount).label("total")
        ).where(
            Operation.user_id == tg_id,
            Operation.date >= start_date,
            Operation.date <= end_date
        ).group_by(Operation.is_income)

        result = await self.session.execute(stmt)

        stats = {"income": 0.0, "expense": 0.0}
        for is_income, total_sum in result.all():
            if is_income:
                stats["income"] = total_sum
            else:
                stats["expense"] = total_sum

        return stats

    async def get_user_operations_with_categories(self, tg_id: int) -> List[tuple]:
        stmt = select(Operation, Category).join(
            Category, Operation.category_id == Category.id, isouter=True
        ).where(
            Operation.user_id == tg_id
        ).order_by(Operation.date.desc())

        result = await self.session.execute(stmt)
        return result.all()

    async def get_category_breakdown(self, tg_id: int, start_date, end_date) -> List[tuple]:
        from sqlalchemy import func

        stmt = select(
            Category.name,
            Operation.is_income,
            func.sum(Operation.amount).label("total"),
            func.count(Operation.id).label("count"),
            func.avg(Operation.amount).label("avg_amount")
        ).join(
            Category, Operation.category_id == Category.id, isouter=True
        ).where(
            Operation.user_id == tg_id,
            Operation.date >= start_date,
            Operation.date <= end_date
        ).group_by(
            Category.name, Operation.is_income
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
        
        return True
    
    async def remove_role_from_user(self, tg_id: int, role_name: str) -> bool:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return False
        
        role = await self.get_role_by_name(role_name)
        if role and role in user.roles:
            user.roles.remove(role)
            await self.session.commit()
        
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
        return True
    
    async def unban_user(self, tg_id: int) -> bool:
        user = await self.get_user_by_tg_id(tg_id)
        if not user:
            return False
        
        user.is_banned = False
        user.is_active = True
        await self.session.commit()
        return True
    
    async def get_all_admins(self) -> List[User]:
        from database.models import Role, UserRole, user_roles
        
        stmt = select(User).join(user_roles).join(Role).where(
            Role.name == UserRole.ADMIN
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
