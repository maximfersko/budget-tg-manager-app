from typing import Optional

from pydantic import BaseModel


class UserDto(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str]
    username: str
