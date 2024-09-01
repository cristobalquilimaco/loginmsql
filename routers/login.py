from argon2 import PasswordHasher
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from db.Conexion import conexion, cursor
from db.models.user import User, UserCreate, UserDB

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "201d573bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b"

router = APIRouter(prefix="/jwtauth", tags=["jwtauth"], responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def get_user(username: str):
    conn = conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, email, password, disabled FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return UserDB(**user)
    return None

def add_user(username: str, email: str, password: str):
    conn = conexion()
    cursor = conn.cursor()
    hashed_password = ph.hash(password)
    cursor.execute(
        "INSERT INTO users (username, email, password, disabled) VALUES (%s, %s, %s, %s)",
        (username, email, hashed_password, False)
    )
    conn.commit()
    cursor.close()
    conn.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except Exception:
        return False

async def auth_user(token: str = Depends(oauth2_scheme)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise exception
    except JWTError:
        raise exception
    user = get_user(username)
    if user is None:
        raise exception
    return user

async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return user

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no existe"
        )
    if not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña es incorrecta"
        )
    access_token = {"sub": user.username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.post("/register")
async def register(user: UserCreate):
    if get_user(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    add_user(user.username, user.email, user.password)
    return {"message": "Usuario registrado exitosamente"}

@router.get("/users/me", response_model=User)
async def me(user: User = Depends(current_user)):
    return user
