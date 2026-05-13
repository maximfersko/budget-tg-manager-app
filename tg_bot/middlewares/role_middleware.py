import json
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from core.constants import REDIS_KEY_USER_ROLES, CACHE_TTL_USER_ROLES
from core.logger import logger
from core.redis_client import redis_client
from database.models import UserRole
from database.repo import DBRepository


class _FakeRole:
    __slots__ = ('name',)

    def __init__(self, name_str: str):
        self.name = UserRole(name_str)


class RoleMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        repo: DBRepository = data.get("repo")
        user_id = event.from_user.id
        cache_key = REDIS_KEY_USER_ROLES.format(user_id=user_id)

        cached = await redis_client.get(cache_key)

        if cached:
            cached_data = json.loads(cached)

            if cached_data["is_banned"]:
                return await self._reply_banned(event)

            user = await repo.get_user_simple(user_id)
            if user:
                user.roles = [_FakeRole(r) for r in cached_data["role_names"]]
                data["user"] = user
                data["user_roles"] = [UserRole(r) for r in cached_data["role_names"]]
                data["is_admin"] = cached_data["is_admin"]
                data["is_moderator"] = cached_data["is_moderator"]
            else:
                data["user"] = None
                data["user_roles"] = []
                data["is_admin"] = False
                data["is_moderator"] = False

            logger.debug(f"User {user_id} roles from cache")
        else:
            user = await repo.get_user_by_tg_id(user_id)

            if user:
                if user.is_banned:
                    return await self._reply_banned(event)

                role_names = [r.name.value for r in user.roles]
                await redis_client.set(cache_key, json.dumps({
                    "is_banned": user.is_banned,
                    "is_admin": user.is_admin(),
                    "is_moderator": user.is_moderator(),
                    "role_names": role_names,
                }), expire=CACHE_TTL_USER_ROLES)

                data["user"] = user
                data["user_roles"] = [role.name for role in user.roles]
                data["is_admin"] = user.is_admin()
                data["is_moderator"] = user.is_moderator()

                logger.debug(f"User {user_id} roles loaded from DB and cached")
            else:
                data["user"] = None
                data["user_roles"] = []
                data["is_admin"] = False
                data["is_moderator"] = False

        return await handler(event, data)

    @staticmethod
    async def _reply_banned(event: TelegramObject) -> None:
        msg = "You are banned from using this bot."
        if isinstance(event, Message):
            await event.answer(msg)
        elif isinstance(event, CallbackQuery):
            await event.answer(msg, show_alert=True)
