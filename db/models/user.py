from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    password: str