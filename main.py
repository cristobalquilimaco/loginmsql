from fastapi import FastAPI
from routers import users_db, login

app = FastAPI()

#ROUTERS
app.include_router(users_db.router)
app.include_router(login.router)



@app.get("/")
def read_root():
    return("hOLA MUNDO")