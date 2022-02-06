from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    """
    Main scheme for User in user_base
    mainly it need for not storing pass inside base, which stores all other data (persons_base)
    """

    global_id: Optional[int] = None
    username: str
    hashed_password: Optional[str] = None
    status: str = "user"
    disabled: bool = False


class Person(BaseModel):
    """
    Main scheme for Person in persons_base
    """

    id: Optional[int] = None
    global_id: Optional[int] = None
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: Optional[str] = ""
    username: Optional[str] = ""
    status: Optional[str] = ""
    disabled: Optional[bool] = False
