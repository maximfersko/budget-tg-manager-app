from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from database.models import UserRole


class RoleFilter(BaseFilter):
    
    def __init__(self, roles: Union[UserRole, list[UserRole]]):
        if isinstance(roles, UserRole):
            self.roles = [roles]
        else:
            self.roles = roles
    
    async def __call__(self, event: Union[Message, CallbackQuery], user_roles: list[UserRole]) -> bool:
        return any(role in user_roles for role in self.roles)


class IsAdmin(BaseFilter):
    
    async def __call__(self, event: Union[Message, CallbackQuery], is_admin: bool) -> bool:
        return is_admin


class IsModerator(BaseFilter):
    
    async def __call__(self, event: Union[Message, CallbackQuery], is_admin: bool, is_moderator: bool) -> bool:
        return is_admin or is_moderator


class IsNotBanned(BaseFilter):
    
    async def __call__(self, event: Union[Message, CallbackQuery], user) -> bool:
        return user is None or not user.is_banned
