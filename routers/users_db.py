# routers/users_db.py

from fastapi import APIRouter, HTTPException, status
from typing import List
from db.models.user import User
from db.schemas.user import user_schemas, users_schemas
from db.Conexion import conexion, cursor

router = APIRouter(prefix="/userdb",
                    tags=["userdb"],
                    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.get("/", response_model=list[User])
async def users():
    cursor.excute("SELECT * FROM users")
    result = cursor.fetchall()
    return user_schemas(result)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email))
    if cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")