# routers/users_db.py

from fastapi import APIRouter, HTTPException, status
from typing import List
from env.db.models.user import User
from env.db.schemas.user import user_schemas, users_schemas
from env.db.Conexion import conexion

router = APIRouter(prefix="/userdb",
                   tags=["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")

    user_dict = dict(user)
    user_dict.pop("id", None)  # Elimina la clave 'id' si existe

    columns = ', '.join(user_dict.keys())
    values = ', '.join(['%s'] * len(user_dict))
    sql = f"INSERT INTO users ({columns}) VALUES ({values})"
    cursor.execute(sql, tuple(user_dict.values()))
    conexion.commit()
    new_id = cursor.lastrowid
    cursor.close()

    # Busca el nuevo usuario y devuelve los datos
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (new_id,))
    new_user = cursor.fetchone()
    cursor.close()
    return user_schemas(new_user)

@router.get("/", response_model=List[User])
async def users():
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()

    # Verifica si hay datos inesperados
    for user in users:
        if not all(key in user for key in ["id", "name", "email"]):
            print(f"Datos incompletos: {user}")

    return users_schemas(users)
