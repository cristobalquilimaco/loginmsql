def user_schemas(user) -> dict:
    return {
        "id": str(user.get("id", "")),  
        "username": user.get("username", ""),   
        "email": user.get("email", ""),
        "password": user.get("password", "")
    }

def users_schemas(users) -> list:
    return [user_schemas(user) for user in users]