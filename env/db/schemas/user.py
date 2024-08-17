

def user_schemas(user) -> dict:
    return {
        "id": str(user.get("id", "")),  
        "name": user.get("name", ""),   
        "email": user.get("email", "")
    }

def users_schemas(users) -> list:
    return [user_schemas(user) for user in users]
