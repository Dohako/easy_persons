from pydantic import BaseModel
from typing import Optional

class NameValues(BaseModel):
    name: str = None
    country: str
    age: int
    base_salary: float
    
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class Person(BaseModel):
    id: int = None
    first_name: str = None
    last_name: str = None
    email: str = None
    status: str = None

class CreatePerson(BaseModel):
    first_name: Optional[str] = ''
    last_name: Optional[str] = ''
    email: Optional[str] = ''
    status: Optional[str] = ''

class UpdatePerson(BaseModel):
    # id: int
    first_name: Optional[str] = ''
    last_name: Optional[str] = ''
    email: Optional[str] = ''
    status: Optional[str] = ''