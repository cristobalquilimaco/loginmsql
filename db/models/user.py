from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    username: str
    phone: str
    email: str
    disabled: bool

class UserDB(User):
    password: str

class UserCreate(BaseModel):
    id: Optional[str] = None
    username: str
    phone: str
    email: str
    password: str