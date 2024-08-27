def user_schemas(user) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "password": user["password"]
    }

def users_schemas(users) -> list:
    return [user_schemas(user) for user in users]