from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.repo import DBRepository

router = Router(name="profile_handler")


@router.message(Command("me"))
async def my_profile(message: Message, repo: DBRepository, user, user_roles, is_admin: bool, is_moderator: bool):
    if not user:
        await message.answer("You are not registered. Send /start to register.")
        return

    roles_text = ", ".join([role.name.value for role in user.roles]) if user.roles else "None"

    badges = []
    if is_admin:
        badges.append("Admin")
    if is_moderator:
        badges.append("Moderator")

    text = (
        f"Your Profile\n\n"
        f"ID: {user.tg_id}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"Name: {user.first_name} {user.last_name or ''}\n"
        f"Roles: {roles_text}\n"
    )

    if badges:
        text += f"\n{' '.join(badges)}"

    if user.is_banned:
        text += "\n\nStatus: BANNED"
    elif user.is_active:
        text += "\n\nStatus: Active"
    else:
        text += "\n\nStatus: Inactive"

    text += f"\n\nRegistered: {user.created_at.strftime('%Y-%m-%d %H:%M')}"

    await message.answer(text)


@router.message(Command("help"))
async def help_command(message: Message, is_admin: bool, is_moderator: bool):
    text = (
        "Available Commands\n\n"
        "Profile:\n"
        "/start - Start bot\n"
        "/me - Your profile and roles\n"
        "/help - This help message\n\n"
        "Finance:\n"
        "/incomes - Upload bank statement\n"
        "/statistics - View statistics\n"
        "/ai <query> - Ask AI about your budget\n"
    )

    if is_moderator or is_admin:
        text += (
            "\nModerator:\n"
            "/users - List users\n"
            "/user_info <id> - User details\n"
        )

    if is_admin:
        text += (
            "\nAdmin:\n"
            "/admin - Admin panel\n"
            "/admins - List admins\n"
            "/grant_admin <id> - Grant admin\n"
            "/revoke_admin <id> - Revoke admin\n"
            "/ban <id> - Ban user\n"
            "/unban <id> - Unban user\n"
        )

    await message.answer(text)
