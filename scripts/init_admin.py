
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.engine import async_session
from database.models import UserRole
from database.repo import DBRepository


async def init_admin(tg_id: int):
    async with async_session() as session:
        repo = DBRepository(session)
        
        user = await repo.get_user_by_tg_id(tg_id)
        
        if not user:
            print(f"User {tg_id} not found in database")
            print("User must interact with bot first to be registered")
            return False
        
        success = await repo.assign_role_to_user(tg_id, UserRole.ADMIN.value)
        
        if success:
            print(f"Admin role granted to user {tg_id}")
            print(f"   Name: {user.first_name} {user.last_name or ''}")
            print(f"   Username: @{user.username}")
            return True
        else:
            print(f"Failed to grant admin role to user {tg_id}")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/init_admin.py <telegram_user_id>")
        print("\nExample: python scripts/init_admin.py 123456789")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Invalid user ID. Must be a number.")
        sys.exit(1)
    
    asyncio.run(init_admin(user_id))
