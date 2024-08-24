from fastapi import APIRouter, Depends, HTTPException, status, Form
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from db.Conexion import conexion  # Asegúrate de que esta importación sea correcta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1  # Duration in minutes
SECRET = "ASJGDJAHSVDajsbjaS1as26552DHFJ6000288ksaBVSJA"

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    username: str
    email: str
    password: str
    disabled: bool

class UserDB(User):
    password: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    cursor = conexion.cursor(dictionary=True)

    # Verificar si el usuario ya existe
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user:
        cursor.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe"
        )

    # Hashear la contraseña
    hashed_password = crypt.hash(password)

    # Insertar el nuevo usuario en la base de datos
    cursor.execute(
        "INSERT INTO users (username, email, disabled, password) VALUES (%s, %s, %s, %s)",
        (username, email, False, hashed_password)
    )
    conexion.commit()
    cursor.close()

    return {"username": username, "email": email}

def search_user_db(username: str):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT username, email, password, disabled FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

async def auth_user(username: str, password: str):
    user_data = search_user_db(username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe"
        )
    try:
        if not crypt.verify(password, user_data['password']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario o contraseña inválida"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar la contraseña",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
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
