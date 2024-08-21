from fastapi import APIRouter, Depends, HTTPException, status, Form
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Dict, Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1  # Duration in minutes
SECRET = "ASJGDJAHSVDajsbjaS1as26552DHFJ6000288ksaBVSJA"

router = APIRouter(prefix="/login",
                   tags=["login"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

users_db: Dict[str, Dict[str, str]] = {}

class User(BaseModel):
    username: str
    email: str
    password: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    # Verificar si el usuario ya existe
    if username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe"
        )
    # Hashear la contraseña
    hashed_password = crypt.hash(password)

    users_db[username] = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
    }
    return {"username": username, "email": email}

def search_user_db(username: str):
    return users_db.get(username)

async def auth_user(username: str, password: str):
    user_data = search_user_db(username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe"
        )
    if not crypt.verify(password, user_data['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o contraseña inválida"
        )
    access_token = {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/")
async def login(username: str = Form(...), password: str = Form(...)):
    return await auth_user(username, password)

@router.get("/user/me")
async def me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = search_user_db(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"username": user["username"], "email": user["email"]}
