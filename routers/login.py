from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional

# Configuración del JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1  # Duración en minutos
SECRET = "ASJGDJAHSVDajsbjaS1as26552DHFJ6000288ksaBVSJA"

# Inicialización
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelos de Solicitud
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/")
async def login(login_request: LoginRequest):
    user_data = search_user_db(login_request.username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe"
        )

    if not crypt.verify(login_request.password, user_data['password']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o contraseña inválida"
        )

    access_token = {
        "sub": login_request.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
    }
    token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

def search_user_db(username: str):
    import mysql.connector
    connection = mysql.connector.connect(
        user="root",
        password="1234",
        host="localhost",
        database="users_db",
        port=3306
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT username, email, password, disabled FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user
