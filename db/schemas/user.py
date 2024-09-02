def user_schema(user) -> dict:
    return {
        "id": user["_id"], 
        "username": user["username"],
        "phone": user["phone"],
        "email": user["email"],
        "password": user["password"]  
    }

def users_schema(users) -> list:
    return [user_schema(user) for user in users]