from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    global_id: Optional[int] = None
    username: str
    hashed_password: str
    status: str = "user"
    disabled: bool = False


class Person(BaseModel):
    id: Optional[int] = None
    global_id: Optional[int] = None
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: Optional[str] = ""
    username: Optional[str] = ""
    status: Optional[str] = ""
    disabled: Optional[bool] = False
