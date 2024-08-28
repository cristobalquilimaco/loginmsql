from fastapi import APIRouter, HTTPException, status
from typing import List
from db.models.user import User
from db.schemas.user import user_schema, users_schema
from db.Conexion import conexion, cursor
from passlib.context import CryptContext

router = APIRouter(
    prefix="/userdb",
    tags=["userdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)

crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=List[User])
async def users():
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    return users_schema(result)

@router.get("/{id}", response_model=User)
async def user(id: int):
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    result = cursor.fetchone()
    if result:
        return user_schema(result)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")

    # Hashear la contraseña antes de almacenarla
    hashed_password = crypt.hash(user.password)
    
    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (user.username, user.email, hashed_password)
    )
    conexion.commit()  

    user_id = cursor.lastrowid  
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    new_user = cursor.fetchone()

    return user_schema(new_user)

@router.put("/", response_model=User)
async def update_user(user: User):
    user_dict = user.dict()
    user_id = user.id

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    cursor.execute(
        "UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s",
        (user.username, user.email, user.password, user_id)
    )
    conexion.commit()  

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    updated_user = cursor.fetchone()

    return user_schema(updated_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int):
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conexion.commit()  

    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    return None
