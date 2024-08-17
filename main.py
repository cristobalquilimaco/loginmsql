from fastapi import FastAPI
from routers import users_db

app = FastAPI()

#ROUTERS
app.include_router(users_db.router)



@app.get("/")
def read_root():
    return("hOLA MUNDO")