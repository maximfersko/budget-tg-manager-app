
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from core.logger import logger
from database.models import UserRole
from database.repo import DBRepository


class RoleMiddleware(BaseMiddleware):
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        repo: DBRepository = data.get("repo")
        
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            
            user = await repo.get_user_by_tg_id(user_id)
            
            if user:
                if user.is_banned:
                    if isinstance(event, Message):
                        await event.answer("You are banned from using this bot.")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("You are banned from using this bot.", show_alert=True)
                    return
                
                data["user"] = user
                data["user_roles"] = [role.name for role in user.roles]
                data["is_admin"] = user.is_admin()
                data["is_moderator"] = user.is_moderator()
                
                logger.debug(f"User {user_id} roles: {data['user_roles']}")
            else:
                data["user"] = None
                data["user_roles"] = []
                data["is_admin"] = False
                data["is_moderator"] = False
        
        return await handler(event, data)
