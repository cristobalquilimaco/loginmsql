# env/db/schemas/user.py

def user_schemas(user) -> dict:
    return {
        "id": str(user.get("id", "")),  # Usa get para manejar claves faltantes
        "name": user.get("name", ""),   # Proporciona un valor predeterminado vacío
        "email": user.get("email", "")
    }

def users_schemas(users) -> list:
    return [user_schemas(user) for user in users]
