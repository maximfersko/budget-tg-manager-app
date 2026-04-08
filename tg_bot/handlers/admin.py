from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.logger import logger
from database.models import UserRole
from database.repo import DBRepository
from tg_bot.filters.role_filter import IsAdmin

router = Router(name="admin_handler")

@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message):
    await message.answer(
        "Admin Panel\n\n"
        "Available commands:\n"
        "/users - List all users\n"
        "/admins - List all admins\n"
        "/grant_admin <user_id> - Grant admin role\n"
        "/revoke_admin <user_id> - Revoke admin role\n"
        "/ban <user_id> - Ban user\n"
        "/unban <user_id> - Unban user\n"
        "/user_info <user_id> - Get user info"
    )

@router.message(Command("users"), IsAdmin())
async def list_users(message: Message, repo: DBRepository):
    await message.answer("User list feature - implement pagination")

@router.message(Command("admins"), IsAdmin())
async def list_admins(message: Message, repo: DBRepository):
    admins = await repo.get_all_admins()
    
    if not admins:
        await message.answer("No admins found")
        return
    
    text = "Admins:\n\n"
    for admin in admins:
        text += f"- {admin.first_name} (@{admin.username}) - ID: {admin.tg_id}\n"
    
    await message.answer(text)

@router.message(Command("grant_admin"), IsAdmin())
async def grant_admin(message: Message, repo: DBRepository):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /grant_admin <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    
    success = await repo.assign_role_to_user(user_id, UserRole.ADMIN.value)
    if success:
        await message.answer(f"SUCCESS: Admin role granted to user {user_id}")
        logger.info(f"Admin role granted to {user_id} by {message.from_user.id}")
    else:
        await message.answer(f"ERROR: Failed to grant admin role to user {user_id}")

@router.message(Command("revoke_admin"), IsAdmin())
async def revoke_admin(message: Message, repo: DBRepository):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /revoke_admin <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    
    if user_id == message.from_user.id:
        await message.answer("ERROR: You cannot revoke your own admin role")
        return
    
    success = await repo.remove_role_from_user(user_id, UserRole.ADMIN.value)
    if success:
        await message.answer(f"SUCCESS: Admin role revoked from user {user_id}")
        logger.info(f"Admin role revoked from {user_id} by {message.from_user.id}")
    else:
        await message.answer(f"ERROR: Failed to revoke admin role from user {user_id}")

@router.message(Command("ban"), IsAdmin())
async def ban_user(message: Message, repo: DBRepository):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    
    if user_id == message.from_user.id:
        await message.answer("ERROR: You cannot ban yourself")
        return
    
    success = await repo.ban_user(user_id)
    if success:
        await message.answer(f"SUCCESS: User {user_id} has been banned")
        logger.info(f"User {user_id} banned by {message.from_user.id}")
    else:
        await message.answer(f"ERROR: Failed to ban user {user_id}")

@router.message(Command("unban"), IsAdmin())
async def unban_user(message: Message, repo: DBRepository):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    
    success = await repo.unban_user(user_id)
    if success:
        await message.answer(f"SUCCESS: User {user_id} has been unbanned")
        logger.info(f"User {user_id} unbanned by {message.from_user.id}")
    else:
        await message.answer(f"ERROR: Failed to unban user {user_id}")

@router.message(Command("user_info"), IsAdmin())
async def user_info(message: Message, repo: DBRepository):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /user_info <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("Invalid user ID")
        return
    
    user = await repo.get_user_by_tg_id(user_id)
    if not user:
        await message.answer(f"User {user_id} not found")
        return
    
    roles = await repo.get_user_roles(user_id)
    text = (
        f"User Info\n\n"
        f"ID: {user.tg_id}\n"
        f"Username: @{user.username}\n"
        f"Name: {user.first_name} {user.last_name or ''}\n"
        f"Roles: {', '.join(roles) if roles else 'None'}\n"
        f"Active: {'Yes' if user.is_active else 'No'}\n"
        f"Banned: {'Yes' if user.is_banned else 'No'}\n"
        f"Created: {user.created_at.strftime('%Y-%m-%d %H:%M')}"
    )
    await message.answer(text)
