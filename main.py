## main.py
from fastapi import FastAPI
from app.routers import auth
from app.routers import notifications
from app.routers import users

app = FastAPI()
app.include_router(auth.router)
app.include_router(notifications.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"status": "ok"}