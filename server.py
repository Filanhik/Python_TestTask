import uuid
import time
from typing import Dict
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 1) «База данных» в памяти
users_db = {
    "maxim": {
        "password": "1234567890",
        "salary": 100000,
        "next_raise": "2025-09-01"
    },
    "bob": {
        "password": "qwertyuiop12345",
        "salary": 80000,
        "next_raise": "2025-12-15"
    },
}

# 2) Хранилище токенов: token -> { username, expires_at }
tokens: Dict[str, Dict] = {}

TOKEN_TTL = 5 * 60  # 5 минут

# Модель входа через JSON
class LoginInput(BaseModel):
    username: str
    password: str

# Проверка токена и возврат username
def get_current_user(Authorization: Optional[str] = Header(None)):
    if not Authorization:
        raise HTTPException(status_code=403, detail="Требуется токен")
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Неверный заголовок Authorization")
    token = Authorization.split(" ", 1)[1]
    data = tokens.get(token)
    if not data:
        raise HTTPException(status_code=401, detail="Токен не найден")
    if data["expires_at"] < time.time():
        tokens.pop(token)
        raise HTTPException(status_code=401, detail="Токен истёк")
    return data["username"]

# POST /login — принимает JSON
@app.post("/login")
def login(data: LoginInput):
    user = users_db.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Неправильные логин или пароль")

    token = str(uuid.uuid4())
    tokens[token] = {
        "username": data.username,
        "expires_at": time.time() + TOKEN_TTL
    }
    return {"access_token": token, "token_type": "bearer", "expires_in": TOKEN_TTL}

# GET /salary — защищённый доступ
@app.get("/salary")
def read_salary(current_user: str = Depends(get_current_user)):
    user = users_db[current_user]
    return {
        "username": current_user,
        "salary": user["salary"],
        "next_raise": user["next_raise"]
    }