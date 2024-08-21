from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1  # Duration in minutes
SECRET = "ASJGDJAHSVDajsbjaS1as26552DHFJ6000288ksaBVSJA"

router = APIRouter(prefix="/login",
                   tags=["login"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

crypt = CryptContext(schemes=["bcrypt"])

# Base de datos simulada
users_db = {}

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    password: str

@router.post("/login", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    # Verificar si el usuario ya existe
    # Verificar si el usuario ya existe
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe"
        )
    # Hashear la contraseña
    hashed_password = crypt.hash(user.password)
    # Crear y agregar el nuevo usuario a la base de datos simulada
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password,
    }
    return {"username": user.username, "email": user.email}

def search_user_db(username: str):
    return users_db.get(username)

async def auth_user(user: User):
    user_data = search_user_db(user.username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe"
        )
    if not crypt.verify(user.password, user_data['password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o contraseña inválida"
        )
    access_token = {"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/")
async def login(user: User):
    return await auth_user(user)

@router.get("/user/me")
async def me(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario no activo",
            headers={"WWW-Autenticate": "Bearer"}
        )
    return user
