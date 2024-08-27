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
    cursor.excute